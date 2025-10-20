/*
 * UNO R4 WiFi + SHT31 → MQTT
 * Serial & MQTT payload: "TEMP : xx.xx    HUMIDITY : yy.yy"
 * Wiring (ตามรูป):
 *   SHT31 VIN→5V, GND→GND, SDA→A4, SCL→A5
 * Note: I2C addr = 0x44 (หรือ 0x45 ถ้า ADR→VCC)
 */

#include <WiFiS3.h>
#include <MQTTClient.h>
#include <Wire.h>
#include "Adafruit_SHT31.h"

// ========= CONFIG =========
const char WIFI_SSID[]      = "teederm";
const char WIFI_PASS[]      = "11335577";

const char MQTT_HOST[]      = "mqtt-dashboard.com"; // เปลี่ยนเป็น broker ของคุณได้
const int  MQTT_PORT        = 1883;                 // non-TLS
const char MQTT_USER[]      = "";                   // ใส่ถ้ามี
const char MQTT_PASSWORD[]  = "";                   // ใส่ถ้ามี
const char MQTT_CLIENT_ID[] = "uno-r4-sht31";

const char MQTT_TOPIC[]     = "ks";
const unsigned long PUBLISH_INTERVAL_MS = 5000;

#define SHT31_ADDR 0x44   // เปลี่ยนเป็น 0x45 ถ้า ADR→VCC
// ==========================

Adafruit_SHT31 sht31;
WiFiClient net;
MQTTClient mqtt(256);

unsigned long lastPub = 0;

void connectWiFi() {
  Serial.print("Connecting WiFi: "); Serial.println(WIFI_SSID);
  int status = WL_IDLE_STATUS;
  while (status != WL_CONNECTED) {
    status = WiFi.begin(WIFI_SSID, WIFI_PASS);
    for (int i = 0; i < 20 && status != WL_CONNECTED; i++) {
      delay(500);
      status = WiFi.status();
      Serial.print(".");
    }
    Serial.println();
  }
  Serial.print("WiFi OK, IP: "); Serial.println(WiFi.localIP());
}

void connectMQTT() {
  mqtt.begin(MQTT_HOST, MQTT_PORT, net);
  Serial.print("Connecting MQTT: "); Serial.print(MQTT_HOST);
  Serial.print(":"); Serial.println(MQTT_PORT);

  while (!mqtt.connect(
    MQTT_CLIENT_ID,
    (strlen(MQTT_USER) ? MQTT_USER : nullptr),
    (strlen(MQTT_PASSWORD) ? MQTT_PASSWORD : nullptr)
  )) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\nMQTT connected.");
  mqtt.publish(MQTT_TOPIC, "{\"status\":\"online\"}");
}

void ensureConnections() {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();
  if (!mqtt.connected()) connectMQTT();
}

void setup() {
  Serial.begin(115200);
  while (!Serial) {}

  Serial.println("UNO R4 WiFi + SHT31 → MQTT (plain payload)");

  // I2C ใช้ขา A4/A5 ตามรูปอยู่แล้ว ไม่ต้อง setPins
  if (!sht31.begin(SHT31_ADDR)) {
    Serial.println("ERROR: SHT31 not found (0x44/0x45). Check wiring.");
    while (1) delay(1000);
  }

  connectWiFi();
  connectMQTT();
}

void loop() {
  mqtt.loop();
  ensureConnections();

  unsigned long now = millis();
  if (now - lastPub >= PUBLISH_INTERVAL_MS) {
    lastPub = now;

    float t = sht31.readTemperature(); // °C
    float h = sht31.readHumidity();    // %RH
    if (isnan(t) || isnan(h)) {
      Serial.println("Failed to read SHT31.");
      return;
    }

    char line[64];
    snprintf(line, sizeof(line), "TEMP : %.2f    HUMIDITY : %.2f", t, h);

    Serial.println(line);
    mqtt.publish(MQTT_TOPIC, line);
  }
}
