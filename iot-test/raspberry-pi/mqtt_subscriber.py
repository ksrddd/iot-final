import os
import sys
from paho.mqtt import client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "mqtt-dashboard.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "ks")
MQTT_USER  = os.getenv("MQTT_USER", "")
MQTT_PASS  = os.getenv("MQTT_PASS", "")
CLIENT_ID  = os.getenv("MQTT_CLIENT_ID", "rpi-subscriber")

def on_connect(client, userdata, flags, rc):
    print(f"Connected rc={rc}")
    client.subscribe(MQTT_TOPIC)
    print(f"Subscribed to {MQTT_TOPIC}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8", errors="ignore")
    print(f"[{msg.topic}] {payload}")

client = mqtt.Client(client_id=CLIENT_ID, clean_session=True)
if MQTT_USER:
    client.username_pw_set(MQTT_USER, MQTT_PASS)

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nBye!")
    sys.exit(0)
