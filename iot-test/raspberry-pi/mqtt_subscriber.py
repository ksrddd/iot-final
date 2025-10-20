import os
import time
from paho.mqtt import client as mqtt
from RPLCD.i2c import CharLCD

# ====== MQTT ======
MQTT_HOST = os.getenv("MQTT_HOST", "mqtt-dashboard.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "ks")
MQTT_USER  = os.getenv("MQTT_USER", "sukhum")
MQTT_PASS  = os.getenv("MQTT_PASS", "ks")
CLIENT_ID  = os.getenv("MQTT_CLIENT_ID", "rpi-lcd-subscriber")

# ====== LCD (I2C PCF8574) ======
# ส่วนมาก addr = 0x27 หรือ 0x3F — ปรับได้ทาง ENV
LCD_ADDR = int(os.getenv("LCD_ADDR", "0x27"), 16)
LCD_PORT = int(os.getenv("LCD_PORT", "1"))  # I2C bus ของ Pi ปกติคือ 1
lcd = CharLCD(i2c_expander='PCF8574', address=LCD_ADDR, port=LCD_PORT,
              cols=16, rows=2, charmap='A02', auto_linebreaks=True)

def lcd_boot():
    lcd.clear()
    lcd.write_string('MQTT: connecting')
    lcd.cursor_pos = (1, 0)
    lcd.write_string(MQTT_TOPIC[:16])

def on_connect(client, userdata, flags, rc):
    lcd.clear()
    lcd.write_string('MQTT connected')
    client.subscribe(MQTT_TOPIC)
    time.sleep(0.6)
    lcd.clear()
    lcd.write_string('Sub: ')
    lcd.write_string(MQTT_TOPIC[:11])

def on_message(client, userdata, msg):
    text = msg.payload.decode('utf-8', errors='ignore')
    # แสดงบรรทัดแรก: TEMP... / HUM...
    # ถ้ายาวเกิน 16 ตัวอักษร จะถูกตัดอัตโนมัติ
    lcd.clear()
    # พยายามย่อให้อยู่ในจอ 16x2
    line1 = text.replace("HUMIDITY", "HUM").replace("TEMP ", "TEMP").strip()
    lcd.write_string(line1[:16])
    # บรรทัดสองแสดงเวลา/สถานะ topic
    lcd.cursor_pos = (1, 0)
    lcd.write_string(time.strftime('%H:%M:%S ') + '  ')
    # ถ้าอยากเห็น topic ด้วย ใส่ท้าย
    # lcd.write_string((msg.topic)[-5:])  # ย่อตามต้องการ

client = mqtt.Client(client_id=CLIENT_ID, clean_session=True)
if MQTT_USER:
    client.username_pw_set(MQTT_USER, MQTT_PASS)

client.on_connect = on_connect
client.on_message = on_message

lcd_boot()
client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)

try:
    client.loop_forever()
except KeyboardInterrupt:
    lcd.clear()
    lcd.write_string('Bye')
    time.sleep(0.5)
    lcd.clear()
