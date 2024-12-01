from pydantic import BaseModel

class Item(BaseModel):
    ssid: str
    password: str
    description: str = None
    apikey: str
