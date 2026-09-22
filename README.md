# Travel Catalogue — Flask + Azure

A small travel-destination catalogue built for Cloud Computing Assignment 2.

## Stack
- **Web app:** Python / Flask (Bootstrap 5 for styling)
- **Data layer:** Azure Table Storage (`storage.py`)
- **Feature 1:** Azure Blob Storage for destination photos (`blob_storage.py`)
- **Feature 2:** Azure AI Translator for on-demand description translation (`translator.py`)
- **Host:** Azure App Service (Linux, Python 3.11)

See `Assignment2_Documentation.pdf` for architecture decisions, the diagram,
and step-by-step Azure deployment commands.

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env            # fill in your Azure Storage connection
                                 # string and (optionally) Translator key
export $(cat .env | xargs)      # or use python-dotenv / your IDE's env support

python app.py                   # http://localhost:8000
```

You need at minimum an Azure Storage Account connection string for the app
to start up and list/add destinations. The Translator feature degrades
gracefully (shows an error only when you actually try to translate) if
`TRANSLATOR_KEY` is not set.

## Project layout

```
travel-catalogue/
├── app.py              # Flask routes, validation, error handlers
├── config.py           # Reads all settings from environment variables
├── storage.py          # Azure Table Storage data-access layer
├── blob_storage.py     # Azure Blob Storage image upload (Feature 1)
├── translator.py       # Azure AI Translator calls (Feature 2)
├── requirements.txt
├── .env.example
└── templates/
    ├── base.html, index.html, add.html, detail.html, error.html
```

## Deploying to Azure

Full commands are in `Assignment2_Documentation.pdf`, Section 4. In short:

1. `az group create` — resource group
2. `az storage account create` — Table + Blob storage
3. `az cognitiveservices account create --kind TextTranslation` — Translator
4. `az appservice plan create` + `az webapp create` — Linux Python web app
5. `az webapp config appsettings set` — wire up connection strings/keys
6. `az webapp config set --startup-file "gunicorn ... app:app"`
7. `az webapp deploy --type zip` — ship the code
8. `az webapp stop` / `az webapp start` between grading sessions to control cost
