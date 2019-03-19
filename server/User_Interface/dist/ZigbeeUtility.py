import requests
from requests.auth import HTTPBasicAuth
import json
import time

username = 'delight'
password = 'delight'

eps = {
    "getApi": "/api",
    "getLights": "/lights",
    "setLights": "/state"
}

def getApiKey(ip):
    raw_data = "{\"devicetype\":\"str\"}"
    url = "http://{}:8080{}".format(ip, eps["getApi"])
    response = requests.post(url,
                             auth=HTTPBasicAuth(username, password),
                             headers={'content-type': 'raw'},
                             data=raw_data,
                             timeout=2)
    if response is not None:
        data = response.json()
        if 'success' in data[0]:
            print(data[0]['success']['username'])
            return data[0]['success']['username']
    return None

def getAllLights(ip, key):
    url = "http://{}:8080{}/{}{}".format(ip, eps["getApi"], key, eps["getLights"])
    response = requests.get(url)
    if response is not None:
        data = response.json()
        print(data)
        lights = []
        for light in data:
            lights.append([data[str(light)]["name"], "ZIGBEE", light, data[str(light)]["manufacturername"]])
        return lights
    return None

def turnOnLight(ip, key, id):
    url = "http://{}:8080{}/{}{}/{}/{}".format(ip, eps["getApi"], key, eps["getLights"], id, eps["setLights"])
    raw_data = "{\"on\":true}"
    response = requests.put(url, headers={'content-type': 'raw'}, data=raw_data, timeout=2)
    if response is not None:
        data = response.json()
        print(data)

def turnOffLight(ip, key, id):
    url = "http://{}:8080{}/{}{}/{}/{}".format(ip, eps["getApi"], key, eps["getLights"], id, eps["setLights"])
    raw_data = "{\"on\":false}"
    response = requests.put(url, headers={'content-type': 'raw'}, data=raw_data, timeout=2)
    if response is not None:
        data = response.json()
        print(data)

def dimLight(ip, key, id, brightness, transition_time):
    url = "http://{}:8080{}/{}{}/{}/{}".format(ip, eps["getApi"], key, eps["getLights"], id, eps["setLights"])
    raw_data = "{\"on\":true, \"bri\":" + str(brightness) + ", \"transitiontime\":" + str(transition_time) + "}"
    response = requests.put(url, headers={'content-type': 'raw'}, data=raw_data, timeout=2)
    if response is not None:
        data = response.json()
        print(data)

def changeLightColor(ip, key, id, brightness, sat, hue, transition_time):
    url = "http://{}:8080{}/{}{}/{}/{}".format(ip, eps["getApi"], key, eps["getLights"], id, eps["setLights"])
    raw_data = "{\"on\":true, \"bri\":" + str(brightness) + ", \"hue\":" + str(hue) + ", \"sat\": " + str(sat) + ", \"transitiontime\":" + str(transition_time) + "}"
    response = requests.put(url, headers={'content-type': 'raw'}, data=raw_data, timeout=2)
    if response is not None:
        data = response.json()
        print(data)

if __name__ == '__main__':
    ip = "192.168.43.80"
    key = getApiKey(ip)
    lights = getAllLights(ip, key)
    print(lights)

    for light in lights:
        print(light[2])
        turnOnLight(ip, key, str(light[2]))


    changeLightColor(ip, key, "2", 100, 255, 210, 2)

    time.sleep(15)

    for light in lights:
        print(light[2])
        turnOffLight(ip, key, str(light[2]))

    time.sleep(2)

    for light in lights:
        print(light[2])
        dimLight(ip, key, light[2], 100, 30)

    time.sleep(3)

    for light in lights:
        print(light[2])
        turnOffLight(ip, key, light[2])
    
