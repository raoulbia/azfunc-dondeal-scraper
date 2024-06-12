# Azure Function Python Script Scheduler

This section provides the steps to create and deploy an Azure Function that runs a Python script on a daily schedule.

## Prerequisites

Check if you have the following installed:
- Azure Functions Core Tools: `func --version`
- Azure CLI: `az --version`

## Setup

### 1. Prepare Your Environment

First, install the necessary tools if you haven't already:

```bash
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@3 --unsafe-perm true

# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### 2. Initialize the Function App

Create a new function project and navigate to the project directory:

```bash
# Initialize a new Azure Function project
func init MyFunctionApp --worker-runtime python

# Navigate to the project directory
cd MyFunctionApp
```

### 3. Create a Function

Generate a new function with a timer trigger that runs once daily:

```bash
# Create a new function
func new --name DailyPythonScript --template "Timer trigger"

# Configure the function to run once daily
# Open function.json and update the schedule to "0 0 * * * *"
```

### 4. Add Your Python Script

Copy your Python script into the function's directory, and ensure the script is callable from the function's `__init__.py` file.

### 5. Manage Dependencies

Add a `requirements.txt` file in the root of your function project and install dependencies:

```bash
azure-functions
azure-storage-blob
requests 
selenium
webdriver-manager
lxml
pandas
pyarrow
```

### 6. Local Testing

Test your function locally to ensure it runs correctly:

```bash
# Start the function locally
func start
```

### 7. Deploy to Azure

Deploy your function app to Azure:

```bash
# Login to Azure
az login

# Publish your function app to Azure
func azure functionapp publish MyFunctionApp
```

### 8. Schedule and Monitor

- Check the function’s execution in the Azure portal under your Function App settings.
- Use Azure Application Insights for monitoring and logging.

<br>

# GitHub Actions with Azure Login Using Federated Credentials

This section provides detailed steps to configure GitHub Actions for Azure login using federated credentials. Follow these instructions to set up the necessary Azure AD app registration, assign roles, configure GitHub secrets, and update the GitHub Actions workflow.

## Step 1: Register an Application in Azure AD

1. **Navigate to Azure Active Directory**:
   - Go to the [Azure portal](https://portal.azure.com).
   - Select `Azure Active Directory`.

2. **Register a New Application**:
   - In the Azure AD menu, select `App registrations`.
   - Click `New registration`.
   - Provide a name for your application (e.g., `GitHub Actions OIDC`).
   - Set the supported account types to `Accounts in this organizational directory only`.
   - Leave the redirect URI empty.
   - Click `Register`.

## Step 2: Configure API Permissions

1. **Add API Permissions**:
   - After registering the app, go to `API permissions`.
   - Click `Add a permission`.
   - Select `Azure Service Management`.
   - Select `Delegated permissions`.
   - Select `user_impersonation`.
   - Click `Add permissions`.

2. **Grant Admin Consent**:
   - Click `Grant admin consent for <your-tenant>`.

## Step 3: Add a Client Secret

1. **Create Client Secret**:
   - Go to `Certificates & secrets`.
   - Click `New client secret`.
   - Provide a description and expiration period.
   - Click `Add`.
   - Copy the client secret value. You will need this for your GitHub secrets.

## Step 4: Configure Federated Credentials

1. **Add Federated Credentials**:
   - Go to `Certificates & secrets`.
   - Click `Federated credentials`.
   - Click `Add credential`.
   - Choose `GitHub Actions` as the identity provider.
   - Fill in the required fields:
     - **Organization**: `raoulbia`
     - **Repository**: `azfunc-dondeal-scraper`
     - **Entity type**: `Environment`
     - **Environment**: `Production`
     - **Issuer URL**: `https://token.actions.githubusercontent.com`
     - **Subject identifier**: `repo:raoulbia/azfunc-dondeal-scraper:environment:Production`

## Step 5: Assign Roles to the Service Principal

1. **Navigate to your Azure Subscription**:
   - Go to the [Azure portal](https://portal.azure.com).
   - Select `Subscriptions`.
   - Select the subscription you are using.

2. **Assign a Role to the Service Principal**:
   - In the subscription menu, select `Access control (IAM)`.
   - Click `Add` > `Add role assignment`.
   - In the `Role` dropdown, select `Contributor`.
   - Under `Assign access to`, select `User, group, or service principal`.
   - Click `Select members`.
   - Search for your application by name and select it.
   - Click `Review + assign`.

## Step 6: Configure GitHub Secrets

1. **Add Secrets to GitHub**:
   - Go to your GitHub repository.
   - Click `Settings`.
   - Click `Secrets and variables` > `Actions`.
   - Click `New repository secret` and add the following secrets:
     - `AZURE_CLIENT_ID`: The Application (client) ID from your Azure AD App Registration.
     - `AZURE_TENANT_ID`: The Directory (tenant) ID from your Azure AD.
     - `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID.
     - `AZURE_CLIENT_SECRET`: The client secret value.

## Step 7: Update GitHub Actions Workflow

Create or update your GitHub Actions workflow file (e.g., `.github/workflows/main.yml`):

```yaml
name: Azure Login

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
          client-secret: ${{ secrets.AZURE_CLIENT_SECRET }}
          enable-AzPSSession: false
          environment: azurecloud
          allow-no-subscriptions: false
          audience: api://AzureADTokenExchange
          auth-type: SERVICE_PRINCIPAL
```

<br>

# Azure Storage Account Permissions

If you encounter permission issues when accessing the storage account container pane, follow these steps to resolve them:

## Step 1: Verify Necessary Roles

Ensure the following roles are assigned to your user account:

- **Storage Blob Data Contributor**: Allows read, write, and delete access to blob data.
- **Reader**: Allows navigation through the Azure portal to view storage account resources.

Note: The "Storage Blob Data Contributor" role allows you to read, write, and delete blob data, while the "Reader" role allows you to navigate the portal and see the storage account resources.

## Step 2: Assign Roles Using Azure Portal

1. **Navigate to the Storage Account:**
   - Go to your storage account in the Azure portal.
   - Click on "Access control (IAM)".

2. **Add Role Assignment:**
   - Click on "Add role assignment".
   - Select "Storage Blob Data Contributor" and add your user account. (*Privileged administrator roles* tab)
   - Repeat the process to assign the "Reader" role. (*Job Functionroles* tab)

## Step 3: Verify Access Settings

1. **Ensure Microsoft Entra Authorization:**
   - In the Azure portal, navigate to your storage account.
   - Under "Settings", select "Configuration".
   - Ensure "Default to Microsoft Entra authorization in the Azure portal" is set to "Enabled".

## Step 4: Retry Access

After ensuring the correct roles are assigned, retry accessing the storage account container pane. Note that it may take a few minutes for the role assignments to take effect.


