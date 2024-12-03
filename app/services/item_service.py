import json


def read_wifi_config():
    with open("./app/static/wifi_config.json", "r") as f:
        return json.load(f)

def write_wifi_config(data):
    with open("./app/static/wifi_config.json", "w") as f:
        json.dump(data, f)
        
def read_led_config():
    with open("./app/static/led_config.json", "r") as f:
        return json.load(f)

def write_led_config(data):
    with open("./app/static/led_config.json", "w") as f:
        json.dump(data, f)
