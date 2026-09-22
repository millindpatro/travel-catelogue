"""
Configuration for the Travel Catalogue app.
All secrets/connection strings are read from environment variables so that
nothing sensitive is hard-coded in source control. When deployed to Azure
App Service, these are set as Application Settings (see README.md).
"""

import os


class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # Azure Table Storage (Data layer)
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get(
        "AZURE_STORAGE_CONNECTION_STRING", ""
    )
    TABLE_NAME = os.environ.get("TABLE_NAME", "destinations")

    # Azure Blob Storage (Feature 1: image hosting)
    BLOB_CONTAINER_NAME = os.environ.get("BLOB_CONTAINER_NAME", "destination-images")

    # Azure AI Translator (Feature 2: on-demand description translation)
    TRANSLATOR_KEY = os.environ.get("TRANSLATOR_KEY", "")
    TRANSLATOR_ENDPOINT = os.environ.get(
        "TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com"
    )
    TRANSLATOR_REGION = os.environ.get("TRANSLATOR_REGION", "")

    # Valid categories used for filtering + form validation
    CATEGORIES = ["Beach", "Mountain", "City", "Cultural", "Adventure", "Wildlife"]

    # Languages offered for the translate feature (code, label)
    LANGUAGES = [
        ("hi", "Hindi"),
        ("fr", "French"),
        ("es", "Spanish"),
        ("de", "German"),
        ("ja", "Japanese"),
        ("zh-Hans", "Chinese (Simplified)"),
    ]
