"""
Feature 1: Azure Blob Storage image hosting.

Lets users attach a photo to a destination. Images are uploaded straight to
a Blob Storage container and the public blob URL is saved alongside the
destination record in Table Storage. Useful for a travel catalogue because
photos are the main thing that sells a destination to a browsing user.
"""

import uuid

from azure.storage.blob import BlobServiceClient, ContentSettings

from config import Config

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_image(file_storage) -> str:
    """
    Uploads a Werkzeug FileStorage object to Blob Storage and returns the
    public URL. Raises ValueError on invalid file types.
    """
    if not file_storage or file_storage.filename == "":
        return ""

    if not allowed_file(file_storage.filename):
        raise ValueError("Unsupported image type. Use png, jpg, jpeg, gif or webp.")

    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    blob_name = f"{uuid.uuid4()}.{ext}"

    service = BlobServiceClient.from_connection_string(
        Config.AZURE_STORAGE_CONNECTION_STRING
    )
    container = service.get_container_client(Config.BLOB_CONTAINER_NAME)
    try:
        container.create_container(public_access="blob")
    except Exception:
        pass  # already exists

    content_type = file_storage.mimetype or "application/octet-stream"
    container.upload_blob(
        name=blob_name,
        data=file_storage.stream,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type),
    )
    return container.get_blob_client(blob_name).url
