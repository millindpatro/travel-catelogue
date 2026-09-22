"""
Data-access layer.

Data layer requirement: destinations are persisted in Azure Table Storage,
a low-cost NoSQL key/value store that is a good fit for a simple catalogue
of independent records with a handful of filterable attributes.

This module isolates all Azure SDK calls so the rest of the app never talks
to the SDK directly (easier to test / swap out later).
"""

import uuid
from datetime import datetime, timezone

from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import TableServiceClient, TableClient

from config import Config

PARTITION_KEY = "destination"


def _get_table_client() -> TableClient:
    service = TableServiceClient.from_connection_string(
        Config.AZURE_STORAGE_CONNECTION_STRING
    )
    # create_table_if_not_exists keeps first-run setup simple
    return service.create_table_if_not_exists(table_name=Config.TABLE_NAME)


def add_destination(data: dict) -> dict:
    """Insert a new destination entity. Returns the stored entity as a dict."""
    table = _get_table_client()
    entity = {
        "PartitionKey": PARTITION_KEY,
        "RowKey": str(uuid.uuid4()),
        "name": data["name"],
        "country": data["country"],
        "city": data.get("city", ""),
        "category": data["category"],
        "price": float(data["price"]),
        "description": data.get("description", ""),
        "image_url": data.get("image_url", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    table.create_entity(entity=entity)
    return entity


def list_destinations(filters: dict | None = None) -> list[dict]:
    """
    Return all destinations, optionally filtered by country, category,
    and/or a max price. Filtering happens after the (cheap) full-partition
    read since the catalogue is expected to stay small; for a very large
    dataset this would instead be pushed into an OData $filter query.
    """
    table = _get_table_client()
    entities = list(table.query_entities(f"PartitionKey eq '{PARTITION_KEY}'"))

    if filters:
        country = (filters.get("country") or "").strip().lower()
        category = (filters.get("category") or "").strip().lower()
        max_price = filters.get("max_price")

        if country:
            entities = [e for e in entities if country in e.get("country", "").lower()]
        if category:
            entities = [e for e in entities if e.get("category", "").lower() == category]
        if max_price not in (None, ""):
            try:
                max_price_val = float(max_price)
                entities = [e for e in entities if e.get("price", 0) <= max_price_val]
            except ValueError:
                pass  # invalid input is ignored gracefully, no crash

    entities.sort(key=lambda e: e.get("created_at", ""), reverse=True)
    return entities


def get_destination(row_key: str) -> dict | None:
    table = _get_table_client()
    try:
        return table.get_entity(partition_key=PARTITION_KEY, row_key=row_key)
    except ResourceNotFoundError:
        return None


def delete_destination(row_key: str) -> bool:
    table = _get_table_client()
    try:
        table.delete_entity(partition_key=PARTITION_KEY, row_key=row_key)
        return True
    except ResourceNotFoundError:
        return False
