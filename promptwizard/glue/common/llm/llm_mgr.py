import os
import google.generativeai as genai
from typing import Dict
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core.llms import ChatMessage
from llama_index.core.llms import LLM
from ..base_classes import LLMConfig
from ..constants.str_literals import InstallLibs, OAILiterals, LLMLiterals, LLMOutputTypes
from ..exceptions import GlueLLMException
from ..utils.runtime_tasks import install_lib_if_missing, str_to_class
from ..utils.logging import get_glue_logger

logger = get_glue_logger(__name__)

def call_openai_api(messages):
    from openai import OpenAI
    from azure.identity import get_bearer_token_provider, AzureCliCredential
    from openai import AzureOpenAI

    if os.environ.get('USE_OPENAI_API_KEY') == "True":
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model=os.environ["OPENAI_MODEL_NAME"],
            messages=messages,
            temperature=0.0,
        )
    else:
        token_provider = get_bearer_token_provider(
            AzureCliCredential(), "https://cognitiveservices.azure.com/.default"
        )
        client = AzureOpenAI(
            api_version=os.environ["OPENAI_API_VERSION"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_ad_token_provider=token_provider
        )
        response = client.chat.completions.create(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            messages=messages,
            temperature=0.0,
        )

    return response.choices[0].message.content

def call_gemini_api(messages):
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise GlueLLMException("GOOGLE_API_KEY environment variable not set")
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        chat = model.start_chat(history=[])
        
        # Convert messages to Gemini format and maintain conversation
        for message in messages:
            if message["role"] in ["system", "user", "assistant"]:
                response = chat.send_message(message["content"])
        
        return response.text
    except Exception as e:
        logger.error(f"Error in Gemini API call: {str(e)}")
        raise GlueLLMException("Failed to get response from Gemini", e)

class LLMMgr:
    @staticmethod
    def chat_completion(messages: Dict):
        llm_handle = os.getenv("MODEL_TYPE", "AzureOpenAI")
        try:
            if llm_handle == "AzureOpenAI":
                return call_openai_api(messages)
            elif llm_handle == "Gemini":
                return call_gemini_api(messages)
            else:
                raise GlueLLMException(f"Unsupported model type: {llm_handle}")
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            return "Sorry, I am not able to understand your query. Please try again."

    @staticmethod
    def get_all_model_ids_of_type(llm_config: LLMConfig, llm_output_type: str):
        res = []
        if llm_config.azure_open_ai:
            for azure_model in llm_config.azure_open_ai.azure_oai_models:
                if azure_model.model_type == llm_output_type:
                    res.append(azure_model.unique_model_id)
        if llm_config.custom_models:
            if llm_config.custom_models.model_type == llm_output_type:
                res.append(llm_config.custom_models.unique_model_id)
        return res

    @staticmethod
    def get_llm_pool(llm_config: LLMConfig) -> Dict[str, LLM]:
        """
        Create a dictionary of LLMs. key would be unique id of LLM, value is object using which
        methods associated with that LLM service can be called.

        :param llm_config: Object having all settings & preferences for all LLMs to be used in out system
        :return: Dict key=unique_model_id of LLM, value=Object of class llama_index.core.llms.LLM
        which can be used as handle to that LLM
        """
        llm_pool = {}
        
        # Handle Azure OpenAI configuration
        if llm_config.azure_open_ai:
            install_lib_if_missing(InstallLibs.LLAMA_LLM_AZ_OAI)
            install_lib_if_missing(InstallLibs.LLAMA_EMB_AZ_OAI)
            install_lib_if_missing(InstallLibs.LLAMA_MM_LLM_AZ_OAI)
            install_lib_if_missing(InstallLibs.TIKTOKEN)

            import tiktoken
            from openai import AzureOpenAI
            from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
            from llama_index.multi_modal_llms.azure_openai import AzureOpenAIMultiModal

            az_token_provider = None
            from azure.identity import get_bearer_token_provider, AzureCliCredential
            az_token_provider = get_bearer_token_provider(
                AzureCliCredential(),
                "https://cognitiveservices.azure.com/.default"
            )

            for azure_oai_model in az_llm_config.azure_oai_models:
                callback_mgr = None
                if azure_oai_model.track_tokens:
                    
                    # If we need to count number of tokens used in LLM calls
                    token_counter = TokenCountingHandler(
                        tokenizer=tiktoken.encoding_for_model(azure_oai_model.model_name_in_azure).encode
                        )
                    callback_mgr = CallbackManager([token_counter])
                    token_counter.reset_counts()
                    # ()

                if azure_oai_model.model_type in [LLMOutputTypes.CHAT, LLMOutputTypes.COMPLETION]:
                    # ()
                    llm_pool[azure_oai_model.unique_model_id] = \
                        AzureOpenAI(
                            # use_azure_ad=az_llm_config.use_azure_ad,
                                    azure_ad_token_provider=az_token_provider,
                                    # model=azure_oai_model.model_name_in_azure,
                                    # deployment_name=azure_oai_model.deployment_name_in_azure,
                                    api_key=az_llm_config.api_key,
                                    azure_endpoint=az_llm_config.azure_endpoint,
                                    api_version=az_llm_config.api_version,
                                    # callback_manager=callback_mgr
                                    )
                    # ()
                elif azure_oai_model.model_type == LLMOutputTypes.EMBEDDINGS:
                    llm_pool[azure_oai_model.unique_model_id] =\
                        AzureOpenAIEmbedding(use_azure_ad=az_llm_config.use_azure_ad,
                                             azure_ad_token_provider=az_token_provider,
                                             model=azure_oai_model.model_name_in_azure,
                                             deployment_name=azure_oai_model.deployment_name_in_azure,
                                             api_key=az_llm_config.api_key,
                                             azure_endpoint=az_llm_config.azure_endpoint,
                                             api_version=az_llm_config.api_version,
                                             callback_manager=callback_mgr
                                             )
                elif azure_oai_model.model_type == LLMOutputTypes.MULTI_MODAL:

                    llm_pool[azure_oai_model.unique_model_id] = \
                        AzureOpenAIMultiModal(use_azure_ad=az_llm_config.use_azure_ad,
                                              azure_ad_token_provider=az_token_provider,
                                              model=azure_oai_model.model_name_in_azure,
                                              deployment_name=azure_oai_model.deployment_name_in_azure,
                                              api_key=az_llm_config.api_key,
                                              azure_endpoint=az_llm_config.azure_endpoint,
                                              api_version=az_llm_config.api_version,
                                              max_new_tokens=4096
                                              )

        # Handle Gemini configuration
        if hasattr(llm_config, 'gemini') and llm_config.gemini:
            try:
                install_lib_if_missing("google-generativeai>=0.3.0")
                from llama_index.llms.gemini import Gemini
                from llama_index.multi_modal_llms.gemini import GeminiMultiModal

                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise GlueLLMException("GOOGLE_API_KEY environment variable not set")

                # Configure Gemini
                gemini_config = llm_config.gemini
                for gemini_model in gemini_config.models:
                    if gemini_model.model_type == LLMOutputTypes.CHAT:
                        llm_pool[gemini_model.unique_model_id] = Gemini(
                            api_key=api_key,
                            model_name=gemini_model.model_name,
                            temperature=gemini_config.temperature or 0.0,
                            max_tokens=gemini_config.max_tokens,
                        )
                    elif gemini_model.model_type == LLMOutputTypes.MULTI_MODAL:
                        llm_pool[gemini_model.unique_model_id] = GeminiMultiModal(
                            api_key=api_key,
                            model_name=gemini_model.model_name,
                            temperature=gemini_config.temperature or 0.0,
                            max_tokens=gemini_config.max_tokens,
                        )
            except Exception as e:
                logger.error(f"Failed to initialize Gemini models: {str(e)}")
                raise GlueLLMException("Failed to initialize Gemini models", e)

        # Handle custom models
        if llm_config.custom_models:
            for custom_model in llm_config.custom_models:
                try:
                    custom_llm_class = str_to_class(
                        custom_model.class_name, 
                        None, 
                        custom_model.path_to_py_file
                    )
                    callback_mgr = None
                    if custom_model.track_tokens:
                        token_counter = TokenCountingHandler(
                            tokenizer=custom_llm_class.get_tokenizer()
                        )
                        callback_mgr = CallbackManager([token_counter])
                        token_counter.reset_counts()
                    llm_pool[custom_model.unique_model_id] = custom_llm_class(
                        callback_manager=callback_mgr
                    )
                except Exception as e:
                    logger.error(f"Failed to load custom model {custom_model.unique_model_id}: {str(e)}")
                    raise GlueLLMException(f"Custom model {custom_model.unique_model_id} not loaded.", e)

        return llm_pool

    @staticmethod
    def get_tokens_used(llm_handle: LLM) -> Dict[str, int]:
        """
        For a given LLM, output the number of tokens used.

        :param llm_handle: Handle to a single LLM
        :return: Dict of token-type and count of tokens used
        """
        token_counter = get_token_counter(llm_handle)
        if token_counter:
            return {
                LLMLiterals.EMBEDDING_TOKEN_COUNT: token_counter.total_embedding_token_count,
                LLMLiterals.PROMPT_LLM_TOKEN_COUNT: token_counter.prompt_llm_token_count,
                LLMLiterals.COMPLETION_LLM_TOKEN_COUNT: token_counter.completion_llm_token_count,
                LLMLiterals.TOTAL_LLM_TOKEN_COUNT: token_counter.total_llm_token_count
                }
        return None
