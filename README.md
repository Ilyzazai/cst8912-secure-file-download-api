# CST8912 Final Project - Secure File Download API

## Student Role

**Student 4: Backend Function Developer (Download)**

This repository contains the Azure Function backend API for the download side of the Secure File Upload & Download System project.

The purpose of this API is to list files from Azure Blob Storage and generate temporary secure download links using Shared Access Signature (SAS) URLs.

---

## Project Overview

The full project is a cloud-native small business portal that allows customers to upload documents securely and download processed files later without using email attachments.

This part focuses on the secure download workflow. The frontend application calls the Azure Function API. The Azure Function connects to a private Azure Blob Storage container, lists available files, and generates temporary SAS download URLs for secure access.

---

## My Responsibility

As **Student 4: Backend Function Developer (Download)**, my responsibility was to build the backend download API.

My work included:

- Creating the Azure Function App for the download API.
- Connecting the function to Azure Blob Storage.
- Listing files stored in the private blob container.
- Generating temporary SAS download links.
- Returning clean JSON responses for the frontend.
- Testing the API using `curl`.
- Deploying the Python Azure Function to Azure.
- Documenting the API request and response formats.

---

## Architecture Flow

```text
Frontend Browser
      ↓
HTTP Request
      ↓
Azure Function API
      ↓
Azure Blob Storage Private Container
      ↓
Temporary SAS Download URL
      ↓
Frontend/User Downloads File
```

---

## Architecture Explanation

The frontend does not access Azure Blob Storage directly using account keys. Instead, the frontend sends an HTTP request to the Azure Function API.

The Azure Function acts as the secure backend layer. It connects to the private Blob Storage container using configuration stored in Azure Function App Settings. When a file needs to be downloaded, the function generates a temporary SAS URL.

The SAS URL allows temporary read-only access to a specific blob file. In this project, the download URL expires after **15 minutes**.

This design keeps the storage container private and prevents exposing sensitive storage account credentials to the frontend or users.

---

## Azure Resources Used

| Resource | Value |
|---|---|
| Azure Function App | `secure-file-api-12711` |
| Azure Storage Account | `securefiles3276610836` |
| Blob Container | `customer-uploads` |
| Runtime | Python Azure Functions |
| Security | Private Blob container + temporary SAS URLs |
| Authentication Method | Storage connection string stored in Function App Settings |
| API Access Method | HTTP-triggered Azure Functions |

---

## Main Azure Services

### Azure Function App

Azure Function App hosts the backend API. It receives HTTP requests from the frontend and runs the Python function code.

In this project, the Function App is responsible for:

- Receiving API requests.
- Connecting to Blob Storage.
- Listing uploaded files.
- Generating SAS download URLs.
- Returning JSON responses.

### Azure Blob Storage

Azure Blob Storage is used to store customer-uploaded files.

In this project, the blob container is private, which means files cannot be accessed directly by the public unless a valid temporary SAS URL is generated.

### Shared Access Signature SAS

A SAS URL is a secure temporary URL that gives limited access to a file in Blob Storage.

For this project:

- SAS permission: read-only
- SAS duration: 15 minutes
- SAS scope: individual blob file
- SAS purpose: secure temporary file download

---

## API Base URL

```text
https://secure-file-api-12711.azurewebsites.net
```

---

# API Endpoints

## 1. List Files API

This API lists files stored in the Azure Blob Storage container and returns a temporary secure download URL for each file.

### Request

```http
GET https://secure-file-api-12711.azurewebsites.net/api/list-files
```

### Request Format

| Field | Value |
|---|---|
| Method | `GET` |
| Endpoint | `/api/list-files` |
| Query Parameters | None |
| Body Required | No |

### Example Request Using Curl

```bash
curl "https://secure-file-api-12711.azurewebsites.net/api/list-files"
```

### Example Response

```json
{
  "container": "customer-uploads",
  "count": 1,
  "files": [
    {
      "filename": "sample.txt",
      "size": 41,
      "downloadUrl": "https://securefiles3276610836.blob.core.windows.net/customer-uploads/sample.txt?...SAS_TOKEN...",
      "expiresInMinutes": 15
    }
  ]
}
```

### Response Fields

| Field | Description |
|---|---|
| `container` | Name of the Azure Blob Storage container |
| `count` | Number of files returned |
| `files` | Array of file objects |
| `filename` | Name of the file in Blob Storage |
| `size` | File size in bytes |
| `downloadUrl` | Temporary secure SAS download URL |
| `expiresInMinutes` | Number of minutes before the SAS URL expires |

---

## 2. Single File Download API

This API generates a temporary secure download URL for one specific file.

### Request

```http
GET https://secure-file-api-12711.azurewebsites.net/api/download?filename=sample.txt
```

### Request Format

| Field | Value |
|---|---|
| Method | `GET` |
| Endpoint | `/api/download` |
| Query Parameter | `filename` |
| Body Required | No |

### Query Parameter

| Parameter | Required | Description |
|---|---|---|
| `filename` | Yes | Name of the file to generate a download link for |

### Example Request Using Curl

```bash
curl "https://secure-file-api-12711.azurewebsites.net/api/download?filename=sample.txt"
```

### Example Response

```json
{
  "filename": "sample.txt",
  "downloadUrl": "https://securefiles3276610836.blob.core.windows.net/customer-uploads/sample.txt?...SAS_TOKEN...",
  "expiresInMinutes": 15
}
```

### Response Fields

| Field | Description |
|---|---|
| `filename` | Name of the requested file |
| `downloadUrl` | Temporary secure SAS download URL |
| `expiresInMinutes` | Number of minutes before the SAS URL expires |

---

# Error Responses

## Missing Filename

If the `filename` query parameter is missing, the API returns an error.

### Request

```http
GET https://secure-file-api-12711.azurewebsites.net/api/download
```

### Response

```json
{
  "error": "Missing filename. Use /api/download?filename=sample.txt"
}
```

---

## File Not Found

If the requested file does not exist in the Blob Storage container, the API returns an error.

### Request

```http
GET https://secure-file-api-12711.azurewebsites.net/api/download?filename=wrongfile.pdf
```

### Response

```json
{
  "error": "File not found",
  "filename": "wrongfile.pdf"
}
```

---

# Request and Response Summary

## List Files API

### Request

```http
GET /api/list-files
```

### Response Format

```json
{
  "container": "container-name",
  "count": 1,
  "files": [
    {
      "filename": "file-name",
      "size": 41,
      "downloadUrl": "temporary-secure-sas-url",
      "expiresInMinutes": 15
    }
  ]
}
```

---

## Single File Download API

### Request

```http
GET /api/download?filename=sample.txt
```

### Response Format

```json
{
  "filename": "sample.txt",
  "downloadUrl": "temporary-secure-sas-url",
  "expiresInMinutes": 15
}
```

---

# Security Design

The download API was designed with secure access in mind.

## Security Controls Used

- The Blob Storage container is private.
- The frontend does not receive the storage account key.
- The Azure Function generates temporary SAS URLs.
- SAS URLs are read-only.
- SAS URLs expire after 15 minutes.
- Storage connection settings are stored in Azure Function App Settings.
- Sensitive values are not hardcoded in the source code.
- The source code does not expose storage keys or connection strings.

---

## Why This Design Is Secure

A private Blob Storage container prevents public users from directly accessing files.

The Azure Function acts as a controlled backend service. It decides which files can be listed or downloaded. The frontend only receives temporary download links, not permanent credentials.

The SAS URL expires after a short time, which reduces the risk if a link is copied or shared.

---

# Configuration

The Azure Function requires storage configuration in Azure Function App Settings.

Example settings:

```text
AzureWebJobsStorage=<storage-connection-string>
STORAGE_ACCOUNT_NAME=securefiles3276610836
CONTAINER_NAME=customer-uploads
```

Sensitive values such as storage connection strings should be stored in Azure Function App Settings and should not be pushed to GitHub.

---

# Local Development

## Prerequisites

To run or deploy this project, the following tools are required:

- Python
- Azure Functions Core Tools
- Azure CLI
- Azure subscription
- Azure Storage Account
- Azure Function App

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Locally

```bash
func start
```

When running locally, local settings should be stored in `local.settings.json`.

Important: `local.settings.json` should not be pushed to GitHub because it can contain secrets.

---

# Deployment

The function was deployed using Azure Functions Core Tools.

```bash
func azure functionapp publish secure-file-api-12711 --python
```

After deployment, the APIs were available through the Azure Function App URL:

```text
https://secure-file-api-12711.azurewebsites.net
```

---

# Testing

The API was tested using `curl`.

## Test List Files API

```bash
curl "https://secure-file-api-12711.azurewebsites.net/api/list-files"
```

## Test Single File Download API

```bash
curl "https://secure-file-api-12711.azurewebsites.net/api/download?filename=sample.txt"
```

Both APIs successfully returned JSON responses with secure temporary SAS download URLs.

---

# Example Successful Test Result

The list files API returned one file from the private Blob Storage container.

```json
{
  "container": "customer-uploads",
  "count": 1,
  "files": [
    {
      "filename": "sample.txt",
      "size": 41,
      "downloadUrl": "https://securefiles3276610836.blob.core.windows.net/customer-uploads/sample.txt?...SAS_TOKEN...",
      "expiresInMinutes": 15
    }
  ]
}
```

This confirms that:

- The Azure Function deployed successfully.
- The function can connect to Azure Blob Storage.
- The private blob container can be read by the backend.
- The API can list files.
- The API can generate secure SAS download URLs.
- The frontend can use the returned URL to download the file temporarily.

---

# Files in This Repository

| File | Description |
|---|---|
| `function_app.py` | Main Azure Function code |
| `host.json` | Azure Functions host configuration |
| `requirements.txt` | Python dependencies |
| `README.md` | Project documentation |
| `.gitignore` | Git ignore rules |

---

# Files Not Pushed to GitHub

The following files should not be committed to GitHub because they may contain secrets or local environment settings:

```text
local.settings.json
.env
.venv/
__pycache__/
.python_packages/
*.pyc
```

---

# Recommended `.gitignore`

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.venv/
venv/

# Azure Functions
local.settings.json
.python_packages/

# Environment files
.env
*.env

# OS/editor files
.vscode/
.DS_Store
```

---

# GitHub Push Steps

After confirming that secret files are ignored, the project can be pushed to GitHub.

## Check Git Status

```bash
git status
```

## Add Safe Files

```bash
git add function_app.py host.json requirements.txt README.md .gitignore
```

## Commit Changes

```bash
git commit -m "Add secure file download Azure Function API"
```

## Push to GitHub

```bash
git push origin main
```

---

# Important GitHub Security Note

Do not push the following information to GitHub:

- Azure Storage account key
- Azure Storage connection string
- SAS token
- `local.settings.json`
- Any file containing passwords, secrets, or access keys

Only the source code, documentation, dependency file, and configuration template should be pushed.

---

# Design Decisions

## Private Blob Container

The blob container was kept private to prevent public access to uploaded customer files.

## Azure Function as Backend API

Azure Function was used because it is serverless, lightweight, and suitable for small API endpoints.

## Temporary SAS URLs

Temporary SAS URLs were used to allow secure file downloads without exposing the storage account key.

## 15-Minute Expiry

The SAS URL expiry time was set to 15 minutes to limit the access window.

## JSON API Responses

The API returns JSON because it is easy for frontend applications to consume and display.

---

# Challenges Faced

During this project, some challenges included:

- Understanding how Azure Functions connect to Blob Storage.
- Making sure the Blob Storage container stayed private.
- Generating SAS URLs correctly.
- Testing the API response using `curl`.
- Ensuring secrets were not hardcoded in the source code.
- Preparing clean request and response formats for frontend integration.

---

# Future Improvements

Future improvements for this project could include:

- Use Managed Identity and User Delegation SAS for stronger production security.
- Add user authentication with Microsoft Entra ID or Azure AD B2C.
- Add file metadata tracking using Azure Table Storage or Cosmos DB.
- Add virus scanning before allowing downloads.
- Add logging and monitoring with Application Insights.
- Add role-based access control for different users.
- Add pagination if the container contains many files.
- Add file type filtering.
- Add frontend integration for displaying files and download buttons.

---

# Final Result

The Secure File Download API was successfully implemented and deployed using Azure Functions.

The backend can:

- Connect to Azure Blob Storage.
- List files from the private container.
- Generate temporary secure SAS download links.
- Return clean JSON responses for frontend use.
- Keep storage credentials secure by using Azure Function App Settings.

This completes the download backend part of the Secure File Upload & Download System.

---

*AI is used for documentation*