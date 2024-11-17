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
const char* TopicMotorKanan = "MotorKanan";
const char* TopicMotorKiri = "MotorKiri";

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
int ModeValue;
int ForwardValue;

int ThrottleMapValue;
int TurnMapValue;

int RightSpeed = 0;
int LeftSpeed = 0;

float TrimValue = 0.0;  // TrimValue for balancing motor speeds

// Timestamp for last MQTT data update
unsigned long LastMqttUpdate = 0;
const unsigned long MqttTimeout = 500;  // 500 ms timeout

SemaphoreHandle_t SpeedMutex;

void setup() {
  Serial.begin(115200);

  // CRSF setup
  CrsfSerial.begin(CRSF_BAUDRATE, SERIAL_8N1, ELRS_RX_PIN, ELRS_TX_PIN);
  if (!CrsfSerial) while (1) Serial.println("Invalid CrsfSerial configuration");
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
  Serial.print("Connecting to WiFi");
  WiFi.begin(SsId, Password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // MQTT setup
  MqttClient.setServer(MqttBroker, MqttPort);
  MqttClient.setCallback(MqttCallback);

  // Connect to MQTT broker
  if (!ConnectToMqtt()) {
    Serial.println("Failed to connect to MQTT broker, check broker configuration.");
    while (1) delay(1000);  // Halt the program if MQTT connection fails
  }

  // Create mutex
  SpeedMutex = xSemaphoreCreateMutex();
}

void loop() {
  Crsf.update();
  TurnValue = Crsf.getChannel(1);
  ThrottleValue = Crsf.getChannel(3);
  SafetyValue = Crsf.getChannel(5);
  ModeValue = Crsf.getChannel(6);
  ForwardValue = Crsf.getChannel(7);  // Example channel for Forward/Reverse

  ThrottleMapValue = map(ThrottleValue, 1000, 2000, 0, 200);
  TurnMapValue = map(TurnValue, 1000, 2000, -100, 100);

  // Calculate TrimValue based on regression
  TrimValue = 0.0205 * ThrottleMapValue + 0.0769;

  if (ModeValue >= 1800) {  // Mode ON
    if (!MqttClient.connected()) {
      ConnectToMqtt();
    }
    MqttClient.loop();

    // Check if MQTT data is outdated
    if (millis() - LastMqttUpdate > MqttTimeout) {
      Serial.println("No new MQTT data, using previous speeds.");
    }

    if (xSemaphoreTake(SpeedMutex, portMAX_DELAY)) {
      // Adjust RightSpeed and LeftSpeed with TrimValue
      int AdjustedRightSpeed = constrain(RightSpeed - TrimValue, 0, 255);
      int AdjustedLeftSpeed = constrain(LeftSpeed + TrimValue, 0, 255);

      ForwardRight(AdjustedRightSpeed);
      ForwardLeft(AdjustedLeftSpeed);
      xSemaphoreGive(SpeedMutex);
    }
  } else {  // Mode OFF
    if (SafetyValue >= 1800) {
      if (ForwardValue >= 1800) {  // Forward ON
        ForwardRight(constrain(ThrottleMapValue - TurnMapValue - TrimValue, 0, 250));
        ForwardLeft(constrain(ThrottleMapValue + TurnMapValue + TrimValue, 0, 250));
      } else {  // Forward OFF (Reverse)
        ReverseRight(constrain(ThrottleMapValue - TurnMapValue - TrimValue, 0, 250));
        ReverseLeft(constrain(ThrottleMapValue + TurnMapValue + TrimValue, 0, 250));
      }
    } else {
      ForwardRight(0);
      ForwardLeft(0);
    }
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
  String Message = String((char*)Payload);

  if (strcmp(Topic, TopicMotorKanan) == 0) {
    int NewRightSpeed = Message.toInt();
    if (xSemaphoreTake(SpeedMutex, portMAX_DELAY)) {
      RightSpeed = constrain(NewRightSpeed, 0, 255);
      xSemaphoreGive(SpeedMutex);
    }
  } else if (strcmp(Topic, TopicMotorKiri) == 0) {
    int NewLeftSpeed = Message.toInt();
    if (xSemaphoreTake(SpeedMutex, portMAX_DELAY)) {
      LeftSpeed = constrain(NewLeftSpeed, 0, 255);
      xSemaphoreGive(SpeedMutex);
    }
  }

  // Update timestamp for last MQTT data
  LastMqttUpdate = millis();
}

// Function to connect to the MQTT broker
bool ConnectToMqtt() {
  Serial.println("Connecting to MQTT...");
  while (!MqttClient.connected()) {
    if (MqttClient.connect("ESP32Client")) {
      Serial.println("MQTT connected");
      MqttClient.subscribe(TopicMotorKanan);
      MqttClient.subscribe(TopicMotorKiri);
      return true;
    } else {
      Serial.print("Failed to connect to MQTT, rc=");
      Serial.print(MqttClient.state());
      Serial.println(" retrying in 5 seconds...");
      delay(5000);
    }
  }
  return false;
}
