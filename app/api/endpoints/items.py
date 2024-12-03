import os
from fastapi import APIRouter, Depends, HTTPException, status, Header
from app.schemas.item import Item
from app.services.item_service import read_wifi_config, write_wifi_config

router = APIRouter()


def verify_api_key(x_api_key: str = Header(None)):
    # Get the API key from environment variables
    APIKEY = os.getenv("API_KEYS")

    if x_api_key != APIKEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )

@router.get("/led")
def get_items(api_key: str = Depends(verify_api_key)):
    return read_wifi_config()

@router.post("/")
def add_item(item: Item, api_key: str = Depends(verify_api_key)):
    write_wifi_config(item.dict())
    return item

@router.post("/led/{ssid}/{password}")
def add_item(ssid: str, password: str, api_key: str = Depends(verify_api_key)):
    data = {
        "ssid": ssid,
        "password": password
    }
    write_wifi_config(data)
    return data
