import os
from fastapi import APIRouter, Depends, HTTPException, status, Header
from app.schemas.item import Item
from app.services.item_service import (
    read_wifi_config,
    write_wifi_config,
    read_led_config,
    write_led_config,
)

router = APIRouter()


def verify_api_key(x_api_key: str = Header(None)):
    # Get the API key from environment variables
    APIKEY = os.getenv("API_KEYS")
    print(APIKEY, x_api_key)

    if x_api_key != APIKEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
        )


@router.get("/led/wifi")
def get_items(api_key: str = Depends(verify_api_key)):
    return read_wifi_config()


@router.post("/led/wifi/data")
def add_item(item: Item, api_key: str = Depends(verify_api_key)):
    write_wifi_config(item.dict())
    return item


@router.post("/led/wifi/{ssid}/{password}")
def add_item(ssid: str, password: str, api_key: str = Depends(verify_api_key)):
    data = {"ssid": ssid, "password": password}
    write_wifi_config(data)
    return data


@router.post("/led/config/on/{seed}")
def get_items(seed: int, api_key: str = Depends(verify_api_key)):
    data = {"led": 1, "seed": seed}
    write_led_config(data)
    return data


@router.post("/led/off")
def get_items(api_key: str = Depends(verify_api_key)):
    data = {"led": 0, "seed": 0}
    write_led_config(data)
    return data


@router.get("/led/status")
def get_items(api_key: str = Depends(verify_api_key)):
    return read_led_config()
