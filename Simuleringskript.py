import paho.mqtt.publish as publish
import time
import json
import random

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/data"

while True:
    # Skapa simulerad sensordata
    sensor_value = random.randint(100, 1000)  # Exempel på en slumpmässig sensorvärde
    payload = json.dumps({'Antal lysnare': sensor_value})

    # Skriv ut payload för felsökning
    print(f"Skickar payload: {payload}")

    # Skicka data till MQTT-brokern
    publish.single(MQTT_TOPIC, payload=payload, hostname=MQTT_BROKER, port=MQTT_PORT)

    # Vänta en stund innan nästa sändning
    time.sleep(5)
