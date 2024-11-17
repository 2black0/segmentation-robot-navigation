#include <WiFi.h>
#include <PubSubClient.h>
#include <AlfredoCRSF.h>
#include <HardwareSerial.h>
#include <freertos/FreeRTOS.h>
#include <freertos/semphr.h>

#define ELRS_RX_PIN 16
#define ELRS_TX_PIN 17

#define MOTOR_RIGHT_RPWM_PIN 12
#define MOTOR_RIGHT_LPWM_PIN 13

#define MOTOR_LEFT_RPWM_PIN 18
#define MOTOR_LEFT_LPWM_PIN 19

#define LED_PIN 2

// WiFi credentials
const char* SsId = "POCOF5";
const char* Password = "1234567890";

// MQTT broker
const char* MqttBroker = "192.168.100.27";
const int MqttPort = 1883;

// MQTT topics
const char* TopicTurnValue = "TurnValue";
const char* TopicThrottleValue = "ThrottleValue";
const char* TopicSafetyValue = "SafetyValue";
const char* TopicForwardValue = "ForwardValue";
const char* TopicStatusValue = "StatusValue";

// Create WiFi and MQTT clients
WiFiClient WifiClient;
PubSubClient MqttClient(WifiClient);

// CRSF setup
HardwareSerial CrsfSerial(1);
AlfredoCRSF Crsf;

// Variables
int ThrottleValue;
int TurnValue;
int SafetyValue;
int ForwardValue;
int StatusValue;

int ThrottleMapValue;
int TurnMapValue;

// Timestamp for last MQTT data update
unsigned long LastMqttUpdate = 0;
const unsigned long MqttInterval = 500;  // 500 ms interval for telemetry data

void setup() {
  // CRSF setup
  CrsfSerial.begin(CRSF_BAUDRATE, SERIAL_8N1, ELRS_RX_PIN, ELRS_TX_PIN);
  if (!CrsfSerial) while (1);  // Halt if configuration is invalid
  Crsf.begin(CrsfSerial);

  // Motor pins setup
  pinMode(MOTOR_RIGHT_RPWM_PIN, OUTPUT);
  pinMode(MOTOR_RIGHT_LPWM_PIN, OUTPUT);
  pinMode(MOTOR_LEFT_RPWM_PIN, OUTPUT);
  pinMode(MOTOR_LEFT_LPWM_PIN, OUTPUT);

  // LED pin setup
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // WiFi setup
  WiFi.begin(SsId, Password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  // MQTT setup
  MqttClient.setServer(MqttBroker, MqttPort);
  MqttClient.setCallback(MqttCallback);

  // Connect to MQTT broker
  while (!ConnectToMqtt()) {
    delay(5000);  // Retry until connected
  }
}

void loop() {
  // Update CRSF data
  Crsf.update();
  TurnValue = Crsf.getChannel(1);
  ThrottleValue = Crsf.getChannel(3);
  SafetyValue = Crsf.getChannel(5);
  ForwardValue = Crsf.getChannel(7);
  StatusValue = Crsf.getChannel(8);

  ThrottleMapValue = map(ThrottleValue, 1000, 2000, 0, 200);
  TurnMapValue = map(TurnValue, 1000, 2000, -100, 100);

  // Always publish telemetry data every 500ms
  if (millis() - LastMqttUpdate > MqttInterval) {
    if (!MqttClient.connected()) {
      ConnectToMqtt();
    }
    PublishTelemetryData();
    LastMqttUpdate = millis();
  }

  // MQTT client loop to process incoming messages
  MqttClient.loop();

  // Control logic for motors
  if (SafetyValue >= 1800) {
    if (ForwardValue >= 1800) {  // Forward ON
      ForwardRight(constrain(ThrottleMapValue - TurnMapValue, 0, 250));
      ForwardLeft(constrain(ThrottleMapValue + TurnMapValue, 0, 250));
    } else {  // Reverse
      ReverseRight(constrain(ThrottleMapValue - TurnMapValue, 0, 250));
      ReverseLeft(constrain(ThrottleMapValue + TurnMapValue, 0, 250));
    }
  } else {
    ForwardRight(0);
    ForwardLeft(0);
  }
}

void ForwardRight(int Pwm) {
  analogWrite(MOTOR_RIGHT_LPWM_PIN, Pwm);
  analogWrite(MOTOR_RIGHT_RPWM_PIN, 0);
}

void ForwardLeft(int Pwm) {
  analogWrite(MOTOR_LEFT_LPWM_PIN, Pwm);
  analogWrite(MOTOR_LEFT_RPWM_PIN, 0);
}

void ReverseRight(int Pwm) {
  analogWrite(MOTOR_RIGHT_RPWM_PIN, Pwm);
  analogWrite(MOTOR_RIGHT_LPWM_PIN, 0);
}

void ReverseLeft(int Pwm) {
  analogWrite(MOTOR_LEFT_RPWM_PIN, Pwm);
  analogWrite(MOTOR_LEFT_LPWM_PIN, 0);
}

// MQTT callback to process incoming messages
void MqttCallback(char* Topic, byte* Payload, unsigned int Length) {
  Payload[Length] = '\0';  // Null-terminate the payload
}

// Function to connect to the MQTT broker
bool ConnectToMqtt() {
  while (!MqttClient.connected()) {
    if (MqttClient.connect("ESP32Client")) {
      return true;
    } else {
      delay(5000);  // Retry every 5 seconds
    }
  }
  return false;
}

// Function to publish telemetry data
void PublishTelemetryData() {
  MqttClient.publish(TopicTurnValue, String(TurnValue).c_str());
  MqttClient.publish(TopicThrottleValue, String(ThrottleValue).c_str());
  MqttClient.publish(TopicSafetyValue, String(SafetyValue).c_str());
  MqttClient.publish(TopicForwardValue, String(ForwardValue).c_str());
  MqttClient.publish(TopicStatusValue, String(StatusValue).c_str());
}