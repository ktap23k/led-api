import os
from fastapi import APIRouter, HTTPException, status
from app.schemas.item import Item
from app.services.item_service import read_wifi_config, write_wifi_config

router = APIRouter()


def verify_api_key(apikey: str):
    # Get the x-api-key from the request headers
    APIKEY = os.getenv("API_KEYS")
    api_key = apikey
    
    if api_key != APIKEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )

@router.get("/<apikey>")
def get_items(apikey: str):
    verify_api_key(apikey)
    return read_wifi_config()

@router.post("/")
def add_item(item: Item):
    verify_api_key(item.apikey)
    write_wifi_config(item.dict())
    return item

@router.post("/params/<apikey>/<ssid>/<password>")
def add_item(apikey: str, ssid: str, password: str):
    verify_api_key(apikey)
    data = {
        "ssid": ssid,
        "password": password
    }
    write_wifi_config(data)
    return data
