# PromptWizard UI 🧙‍♂️✨

A modern, user-friendly web interface for the PromptWizard prompt optimization framework.

<p align="center">
  <img src="../images/promptwizard_ui_showcase.png" alt="PromptWizard UI" width="800">
</p>

## Features

<p align="center">
  <img src="../images/ui_features_diagram.png" alt="UI Features" width="700">
  <br>
  <em>PromptWizard UI features and their relationships</em>
</p>

### Tabbed Interface
- **Basic Info**: Configure task description, base instruction, answer format, model, and API key
- **Data Selection**: Choose datasets, configure in-context examples, and preview data
- **Prompt Configuration**: Select optimization scenarios and configure advanced parameters
- **Evaluation**: Set evaluation criteria and manage optimization sessions

<p align="center">
  <img src="../images/tabs_workflow.png" alt="Tabs Workflow" width="650">
  <br>
  <em>The workflow between different tabs in the UI</em>
</p>

### Advanced Features
- **Advanced Optimization Parameters**: Fine-tune the optimization process with parameters like mutate refine iterations, refine task examples iterations, and more
- **Advanced Evaluation Metrics**: Use metrics like Faithfulness, Semantic Similarity, Context Relevancy, and more
- **Dataset Preview**: Visualize and inspect your dataset before optimization
- **Multimodal Support**: Optimize prompts for image-based tasks with image uploads
- **Session Management**: Save and load optimization sessions for later use

<p align="center">
  <img src="../images/optimization_process.png" alt="Optimization Process" width="700">
  <br>
  <em>The prompt optimization process flow</em>
</p>

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Running instance of the PromptWizard API

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env.local` file with the following content:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:5000
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

## Usage

1. **Basic Info Tab**:
   - Enter your task description and base instruction
   - Specify the answer format (optional)
   - Select the model and enter your API key

2. **Data Selection Tab**:
   - Choose a dataset or upload your own
   - Configure in-context examples settings
   - Preview your dataset (if available)

3. **Prompt Configuration Tab**:
   - Select an optimization scenario
   - Configure optimization parameters
   - Enable multimodal support if needed

4. **Evaluation Tab**:
   - Select evaluation criteria
   - Configure advanced evaluation metrics
   - Set up session management

5. Click "Optimize Prompt" to start the optimization process

## Deployment

### Build for Production

```bash
npm run build
```

### Start Production Server

```bash
npm run start
```

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t promptwizard-ui .
   ```

2. Run the container:
   ```bash
   docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://api:5000 promptwizard-ui
   ```

## Configuration

The UI can be configured using environment variables:

- `NEXT_PUBLIC_API_URL`: URL of the PromptWizard API (default: http://localhost:5000)
- `NEXT_PUBLIC_DEFAULT_MODEL`: Default model to use (default: Gemini)

## Learn More

To learn more about the technologies used:

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://reactjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
