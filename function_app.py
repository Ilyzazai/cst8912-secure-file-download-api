import os
import json
import datetime
import azure.functions as func

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

CONTAINER_NAME = os.getenv("BLOB_CONTAINER", "customer-uploads")
EXPIRY_MINUTES = 15


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }


def json_response(data, status_code=200):
    return func.HttpResponse(
        json.dumps(data),
        status_code=status_code,
        mimetype="application/json",
        headers=cors_headers()
    )


def get_storage_info():
    conn = os.getenv("AzureWebJobsStorage")
    parts = {}

    for item in conn.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            parts[key] = value

    return conn, parts.get("AccountName"), parts.get("AccountKey")


def create_sas_url(blob_name):
    conn, account_name, account_key = get_storage_info()

    blob_service = BlobServiceClient.from_connection_string(conn)
    blob_client = blob_service.get_blob_client(
        container=CONTAINER_NAME,
        blob=blob_name
    )

    expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=EXPIRY_MINUTES)

    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=CONTAINER_NAME,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=expiry
    )

    return f"{blob_client.url}?{sas_token}"


@app.route(route="list-files", methods=["GET", "OPTIONS"])
def list_files(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=cors_headers())

    try:
        conn, account_name, account_key = get_storage_info()
        blob_service = BlobServiceClient.from_connection_string(conn)
        container_client = blob_service.get_container_client(CONTAINER_NAME)

        files = []

        for blob in container_client.list_blobs():
            files.append({
                "filename": blob.name,
                "size": blob.size,
                "downloadUrl": create_sas_url(blob.name),
                "expiresInMinutes": EXPIRY_MINUTES
            })

        return json_response({
            "container": CONTAINER_NAME,
            "count": len(files),
            "files": files
        })

    except Exception as e:
        return json_response({
            "error": "Failed to list files",
            "details": str(e)
        }, 500)


@app.route(route="download", methods=["GET", "OPTIONS"])
def download(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=cors_headers())

    filename = req.params.get("filename")

    if not filename:
        return json_response({
            "error": "Missing filename. Use /api/download?filename=sample.txt"
        }, 400)

    try:
        conn, account_name, account_key = get_storage_info()
        blob_service = BlobServiceClient.from_connection_string(conn)
        blob_client = blob_service.get_blob_client(
            container=CONTAINER_NAME,
            blob=filename
        )

        if not blob_client.exists():
            return json_response({
                "error": "File not found",
                "filename": filename
            }, 404)

        return json_response({
            "filename": filename,
            "downloadUrl": create_sas_url(filename),
            "expiresInMinutes": EXPIRY_MINUTES
        })

    except Exception as e:
        return json_response({
            "error": "Failed to create download link",
            "details": str(e)
        }, 500)
