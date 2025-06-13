# Railway Deployment Guide for SupportOps Automator

This guide provides step-by-step instructions for deploying the SupportOps Automator application on Railway.

## Prerequisites

- A GitHub repository with your SupportOps Automator code
- A Railway account (https://railway.app)
- Your database setup (PostgreSQL)

## Step 1: Deploy the Backend

1. **Create a new project in Railway**:
   - Go to the Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Configure the backend service**:
   - Set the root directory to `/backend`
   - Set the build command: `pip install -r requirements.txt`
   - Set the start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Add environment variables**:
   - Click on "Variables" tab
   - Add the following variables:
     ```
     DATABASE_URL=postgresql://postgres:password@postgres:5432/supportops
     SECRET_KEY=your_secret_key_for_auth_if_needed
     ```

4. **Add PostgreSQL database**:
   - Click "New" → "Database" → "PostgreSQL"
   - Railway will automatically link the database to your service
   - The `DATABASE_URL` variable will be automatically set

## Step 2: Deploy the Frontend

1. **Create a new service for the frontend**:
   - In your Railway project, click "New" → "Service" → "GitHub Repo"
   - Select the same repository

2. **Configure the frontend service**:
   - Set the root directory to `/frontend/Ops-automator`
   - Set the build command: `npm install && npm run build`
   - Set the start command: `npx serve -s dist`

3. **Add environment variables**:
   - Add `VITE_API_URL` pointing to your backend service URL
   - For example: `VITE_API_URL=https://your-backend-service.railway.app`

4. **Update the frontend API calls** (if not already done):
   - Create a `.env` file in the frontend directory:
     ```
     VITE_API_URL=https://your-backend-service.railway.app
     ```
   - Make sure API calls use this environment variable:
     ```typescript
     // Example
     const response = await fetch(`${import.meta.env.VITE_API_URL}/api/endpoint`);
     ```

## Step 3: Configure Domain Settings (Optional)

1. **Add custom domains**:
   - In the Railway dashboard, go to your service
   - Click "Settings" → "Domains"
   - Add your custom domain (e.g., `api.supportops-automator.com` for backend)
   - Add your custom domain (e.g., `app.supportops-automator.com` for frontend)

2. **Update CORS settings** if using custom domains:
   ```python
   # In main.py
   allow_origins=["https://app.supportops-automator.com"]
   ```

## Step 4: Testing Your Deployment

1. **Test the backend API**:
   - Visit `https://your-backend-service.railway.app/docs` to see the Swagger UI
   - Test the endpoints to ensure they're working

2. **Test the frontend**:
   - Visit `https://your-frontend-service.railway.app`
   - Try creating rules, testing webhooks, etc.

## Step 5: Setting Up Webhooks for External Services

### Zendesk Webhook Setup

1. Log into your Zendesk admin panel
2. Go to Settings → Extensions → Webhooks
3. Create a new webhook:
   - Name: SupportOps Automator
   - Endpoint URL: `https://your-backend-service.railway.app/trigger/zendesk`
   - Request method: POST
   - Request format: JSON
4. Set up a trigger to use this webhook when tickets are tagged

### Freshdesk Webhook Setup

1. Log into your Freshdesk admin panel
2. Go to Admin → Automations → Webhooks
3. Create a new webhook:
   - Name: SupportOps Automator
   - URL: `https://your-backend-service.railway.app/trigger/freshdesk`
   - Method: POST
   - Encoding: JSON
4. Configure the events that should trigger the webhook

## Troubleshooting

### Common Issues

1. **CORS errors**:
   - Ensure the CORS middleware in the backend allows requests from your frontend domain
   - Check that the frontend is using the correct backend URL

2. **Database connection issues**:
   - Verify the `DATABASE_URL` is correctly set
   - Check that the database is running and accessible

3. **Build failures**:
   - Check the build logs for errors
   - Ensure all dependencies are correctly specified in requirements.txt and package.json

### Viewing Logs

1. In the Railway dashboard, select your service
2. Click on the "Logs" tab to view real-time logs
3. Filter logs by severity if needed

## Monitoring and Maintenance

1. **Set up monitoring**:
   - Railway provides basic monitoring for your services
   - Consider adding additional monitoring tools if needed

2. **Regular updates**:
   - Keep your dependencies up to date
   - Test updates locally before deploying to production

3. **Backup strategy**:
   - Set up regular database backups
   - Railway provides automatic backups for databases

## Security Considerations

1. **API security**:
   - Consider adding authentication to your API endpoints
   - Use HTTPS for all communications

2. **Environment variables**:
   - Never commit sensitive environment variables to your repository
   - Use Railway's variable management for all secrets

3. **Webhook verification**:
   - Implement verification for incoming webhooks (HMAC, tokens, etc.)
   - Log and monitor webhook requests for suspicious activity
