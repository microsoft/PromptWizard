# Deploying PromptWizard on Vercel

This guide provides step-by-step instructions for deploying PromptWizard on Vercel.

## Prerequisites

- A [Vercel](https://vercel.com) account
- A GitHub account (for connecting your repository)
- API keys for the LLM services you plan to use (Gemini, OpenAI, etc.)

## Deployment Steps

### 1. Fork or Clone the Repository

First, fork or clone the PromptWizard repository to your GitHub account.

### 2. Connect to Vercel

1. Log in to your Vercel account
2. Click "Add New..." and select "Project"
3. Import your GitHub repository
4. Select the PromptWizard repository

### 3. Configure Project Settings

1. **Framework Preset**: Select "Other"
2. **Root Directory**: Leave as is (should be the root of the repository)
3. **Build Command**: Leave blank (defined in vercel.json)
4. **Output Directory**: Leave blank (defined in vercel.json)

### 4. Environment Variables

Add the following environment variables:

| Name | Value | Description |
|------|-------|-------------|
| `GOOGLE_API_KEY` | Your Gemini API key | Required for Gemini model |
| `OPENAI_API_KEY` | Your OpenAI API key | Required for GPT-4 model |
| `NEXT_PUBLIC_API_URL` | `/api` | API URL for the frontend |

You can add these as plain text or as [Vercel Secrets](https://vercel.com/docs/concepts/projects/environment-variables#securing-environment-variables) for better security.

### 5. Deploy

Click "Deploy" and wait for the deployment to complete. Vercel will automatically build and deploy both the API and UI components based on the configuration in `vercel.json`.

## Vercel Configuration

The `vercel.json` file in the repository root configures the deployment:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/app.py",
      "use": "@vercel/python"
    },
    {
      "src": "ui/package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/app.py"
    },
    {
      "src": "/(.*)",
      "dest": "ui/$1"
    }
  ]
}
```

This configuration:
- Builds the Python API using the Vercel Python runtime
- Builds the Next.js UI using the Vercel Next.js runtime
- Routes API requests to the Python backend
- Routes all other requests to the Next.js frontend
- Sets up environment variables

## Vercel Serverless Functions Limitations

Vercel serverless functions have some limitations to be aware of:

1. **Execution Time**: Functions have a maximum execution time of 10 seconds on the Hobby plan and 60 seconds on the Pro plan. Prompt optimization can take longer than this.

2. **Memory**: Functions are limited to 1GB of memory on the Hobby plan and 3GB on the Pro plan.

3. **Cold Starts**: Serverless functions may experience cold starts, which can add latency to the first request after a period of inactivity.

For production use with heavy optimization workloads, consider:
- Upgrading to a Vercel Pro plan
- Using a different deployment option like Docker on a VPS
- Implementing a queue system for long-running tasks

## Troubleshooting

### API Connection Issues

If the UI cannot connect to the API, check:
1. The `NEXT_PUBLIC_API_URL` environment variable is set correctly
2. The API routes in `vercel.json` are correct
3. The API is successfully deployed (check Vercel logs)

### Long-Running Operations

If prompt optimization times out:
1. Consider implementing a queue system for long-running tasks
2. Break down the optimization process into smaller steps
3. Use a different deployment option for production workloads

### API Key Issues

If you encounter API key errors:
1. Verify the API keys are correctly set in the Vercel environment variables
2. Check that the API keys have the necessary permissions
3. Ensure you have sufficient quota/credits for the LLM services

## Monitoring and Logs

Vercel provides logs and monitoring for your deployment:
1. Go to your project in the Vercel dashboard
2. Click on "Deployments" to see all deployments
3. Select a deployment to view its logs
4. Use the "Functions" tab to see serverless function metrics

For more detailed monitoring, consider integrating with services like Sentry or LogRocket.
