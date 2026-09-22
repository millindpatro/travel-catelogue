"""
Feature 2: Azure AI Translator.

Lets a viewer translate a destination's description into another language
on demand. Useful for a travel catalogue because it can be browsed by an
international audience without maintaining multiple copies of the content.
"""

import uuid

import requests

from config import Config


def translate_text(text: str, target_lang: str) -> str:
    if not text:
        return ""
    if not Config.TRANSLATOR_KEY:
        raise RuntimeError("Translator is not configured (missing TRANSLATOR_KEY).")

    url = f"{Config.TRANSLATOR_ENDPOINT}/translate"
    params = {"api-version": "3.0", "to": target_lang}
    headers = {
        "Ocp-Apim-Subscription-Key": Config.TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": Config.TRANSLATOR_REGION,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }
    body = [{"text": text}]

    response = requests.post(url, params=params, headers=headers, json=body, timeout=10)
    response.raise_for_status()
    result = response.json()
    return result[0]["translations"][0]["text"]
