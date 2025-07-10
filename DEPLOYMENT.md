# PromptWizard Deployment Guide

This guide provides instructions for deploying PromptWizard in various environments.

## Table of Contents

- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
  - [Azure](#azure)
  - [AWS](#aws)
  - [Google Cloud](#google-cloud)
- [Environment Variables](#environment-variables)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Local Development

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### API Setup

1. Navigate to the API directory:
   ```bash
   cd api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Start the API server:
   ```bash
   python app.py
   ```

The API will be available at http://localhost:5000.

### UI Setup

1. Navigate to the UI directory:
   ```bash
   cd ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env.local` file with the following content:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:5000
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

The UI will be available at http://localhost:3000.

## Docker Deployment

### Prerequisites

- Docker
- Docker Compose

### Deployment Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/microsoft/PromptWizard.git
   cd PromptWizard
   ```

2. Create a `.env` file in the root directory with your API keys:
   ```
   GOOGLE_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

3. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

4. Access the UI at http://localhost:3000

### Individual Container Deployment

If you prefer to deploy the API and UI separately:

#### API Container

```bash
cd api
docker build -t promptwizard-api .
docker run -p 5000:5000 -e GOOGLE_API_KEY=your_key -e OPENAI_API_KEY=your_key promptwizard-api
```

#### UI Container

```bash
cd ui
docker build -t promptwizard-ui .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:5000 promptwizard-ui
```

## Cloud Deployment

### Azure

#### Azure App Service

1. Create two App Services (one for API, one for UI)
2. Deploy the API:
   ```bash
   cd api
   az webapp up --sku B1 --name promptwizard-api
   ```
3. Deploy the UI:
   ```bash
   cd ui
   az webapp up --sku B1 --name promptwizard-ui
   ```
4. Configure environment variables in the Azure Portal

#### Azure Container Instances

1. Build and push Docker images to Azure Container Registry
2. Deploy containers using Azure CLI or Azure Portal
3. Configure networking to allow communication between containers

### AWS

#### AWS Elastic Beanstalk

1. Create two Elastic Beanstalk environments
2. Deploy the API:
   ```bash
   cd api
   eb init && eb create promptwizard-api
   ```
3. Deploy the UI:
   ```bash
   cd ui
   eb init && eb create promptwizard-ui
   ```
4. Configure environment variables in the Elastic Beanstalk console

#### AWS ECS

1. Create an ECS cluster
2. Define task definitions for API and UI
3. Create services for each task
4. Configure load balancers and networking

### Google Cloud

#### Google Cloud Run

1. Build and push Docker images to Google Container Registry
2. Deploy the API:
   ```bash
   cd api
   gcloud run deploy promptwizard-api --image gcr.io/your-project/promptwizard-api
   ```
3. Deploy the UI:
   ```bash
   cd ui
   gcloud run deploy promptwizard-ui --image gcr.io/your-project/promptwizard-ui
   ```
4. Configure environment variables in the Cloud Run console

## Environment Variables

### API Environment Variables

- `GOOGLE_API_KEY`: API key for Google Gemini
- `OPENAI_API_KEY`: API key for OpenAI
- `FLASK_ENV`: Set to `production` for production deployment
- `FLASK_APP`: Set to `app.py`

### UI Environment Variables

- `NEXT_PUBLIC_API_URL`: URL of the PromptWizard API
- `NEXT_PUBLIC_DEFAULT_MODEL`: Default model to use (Gemini, GPT-4, etc.)

## Security Considerations

1. **API Keys**: Never commit API keys to version control. Use environment variables or secrets management.
2. **CORS**: The API has CORS enabled for the frontend. In production, restrict CORS to your frontend domain.
3. **Rate Limiting**: Consider implementing rate limiting to prevent abuse.
4. **Input Validation**: All user input is validated, but be cautious when deploying to production.
5. **HTTPS**: Always use HTTPS in production environments.

## Troubleshooting

### Common Issues

1. **API Connection Error**:
   - Check if the API server is running
   - Verify the `NEXT_PUBLIC_API_URL` environment variable
   - Check network connectivity between UI and API

2. **Model API Errors**:
   - Verify API keys are correct
   - Check if you have sufficient quota/credits
   - Ensure the model is available in your region

3. **Docker Issues**:
   - Run `docker-compose logs` to view container logs
   - Check if ports are correctly mapped
   - Verify environment variables are set correctly

For more help, please open an issue on the GitHub repository.
