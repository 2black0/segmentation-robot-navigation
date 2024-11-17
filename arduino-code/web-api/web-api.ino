/*
Program by Ardy Seto

IP ESP32: http://192.168.115.24/

untuk mengirim data kecepatan motor kanan dan kiri dengan http request get:
http://192.168.115.24/setSpeed?RightSpeed=122&LeftSpeed=123
*/

#include <AlfredoCRSF.h>
#include <HardwareSerial.h>
#include <WiFi.h>
#include <WebServer.h>

#define ELRS_RX_PIN 16
#define ELRS_TX_PIN 17

#define MOTOR_RIGHT_RPWM_PIN 12
#define MOTOR_RIGHT_LPWM_PIN 13

#define MOTOR_LEFT_RPWM_PIN 18
#define MOTOR_LEFT_LPWM_PIN 19

#define LED_PIN 2

// Set up a new Serial object
HardwareSerial crsfSerial(1);
AlfredoCRSF crsf;

// WiFi credentials
const char* SsId = "POCOF5";
const char* Password = "1234567890";

// WebServer object
WebServer Server(80);

// Variables
int ThrottleValue;
int TurnValue;
int SafetyValue;
int ModeValue;

int ThrottleMapValue;
int TurnMapValue;

int RightSpeed = 0;  // Default motor speed for right motor
int LeftSpeed = 0;   // Default motor speed for left motor

void setup() {
  Serial.begin(115200);

  // CRSF setup
  crsfSerial.begin(CRSF_BAUDRATE, SERIAL_8N1, ELRS_RX_PIN, ELRS_TX_PIN);
  if (!crsfSerial) while (1) Serial.println("Invalid crsfSerial configuration");
  crsf.begin(crsfSerial);

  // Motor pins setup
  pinMode(MOTOR_RIGHT_RPWM_PIN, OUTPUT);
  pinMode(MOTOR_RIGHT_LPWM_PIN, OUTPUT);
  pinMode(MOTOR_LEFT_RPWM_PIN, OUTPUT);
  pinMode(MOTOR_LEFT_LPWM_PIN, OUTPUT);

  // LED pin setup
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // WiFi setup
  //Serial.print("Connecting to WiFi");
  WiFi.begin(SsId, Password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    //Serial.print(".");
  }
  //Serial.println("\nConnected to WiFi");
  //Serial.print("IP Address: ");
  //Serial.println(WiFi.localIP());

  // Web server setup
  Server.on("/", handleRoot);                      // Main page with robot data
  Server.on("/setSpeed", handleSetSpeed);          // Endpoint to set motor speed
  Server.begin();
  //Serial.println("HTTP server started");
}

void loop() {
    crsf.update();
    ThrottleValue = crsf.getChannel(3);
    TurnValue = crsf.getChannel(1);
    SafetyValue = crsf.getChannel(5);
    ModeValue = crsf.getChannel(6);

    ThrottleMapValue = map(ThrottleValue, 1000, 2000, 0, 200);
    TurnMapValue = map(TurnValue, 1000, 2000, -100, 100);

    // Print the values for debugging
    /*String SafetyStatus = (SafetyValue >= 1800) ? "ON" : "OFF";
    String ModeStatus = (ModeValue >= 1800) ? "ON" : "OFF";
    Serial.print("ThrottleValue: ");
    Serial.print(ThrottleValue);
    Serial.print(" | TurnValue: ");
    Serial.print(TurnValue);
    Serial.print(" | SafetyValue: ");
    Serial.print(SafetyStatus);
    Serial.print(" | ModeValue: ");
    Serial.print(ModeStatus);
    Serial.print(" | ThrottleMapValue: ");
    Serial.print(ThrottleMapValue);
    Serial.print(" | TurnMapValue: ");
    Serial.print(TurnMapValue);
    Serial.print(" | RightSpeed: ");
    Serial.print(RightSpeed);
    Serial.print(" | LeftSpeed: ");
    Serial.println(LeftSpeed);*/

    // Jika Mode ON, gunakan kecepatan yang dikirim melalui HTTP request
    if (ModeValue >= 1800) {
        // Mode ON: Gunakan nilai dari HTTP request untuk mengatur kecepatan motor
        ForwardRight(constrain(RightSpeed, 0, 255));
        ForwardLeft(constrain(LeftSpeed, 0, 255));
    } else {
        // Mode OFF: Menggunakan kontrol manual
        if (SafetyValue >= 1800) {
          ForwardRight(constrain(ThrottleMapValue - TurnMapValue, 0, 250));
          ForwardLeft(constrain(ThrottleMapValue + TurnMapValue, 0, 250));
        } else {
          ForwardRight(0);
          ForwardLeft(0);
        }
    }

    // Update the web server
    Server.handleClient();
    delay(50);
}

void ForwardRight(int Pwm) {
  analogWrite(MOTOR_RIGHT_LPWM_PIN, Pwm);
  analogWrite(MOTOR_RIGHT_RPWM_PIN, 0);
}

void ReverseRight(int Pwm) {
  analogWrite(MOTOR_RIGHT_RPWM_PIN, Pwm);
  analogWrite(MOTOR_RIGHT_LPWM_PIN, 0);
}

void ReverseLeft(int Pwm) {
  analogWrite(MOTOR_LEFT_RPWM_PIN, Pwm);
  analogWrite(MOTOR_LEFT_LPWM_PIN, 0);
}

void ForwardLeft(int Pwm) {
  analogWrite(MOTOR_LEFT_LPWM_PIN, Pwm);
  analogWrite(MOTOR_LEFT_RPWM_PIN, 0);
}

// Web server handlers

// Root handler that shows robot data
void handleRoot() {
  String SafetyStatus = (SafetyValue >= 1800) ? "ON" : "OFF";
  String ModeStatus = (ModeValue >= 1800) ? "ON" : "OFF";

  String Html = "<html>"
                "<head>"
                "<title>ESP32 Robot Control</title>"
                "<meta http-equiv=\"refresh\" content=\"4\">"
                "</head>"
                "<body>"
                "<h1>ESP32 Robot Data</h1>"
                "<p><strong>Throttle Value:</strong> " + String(ThrottleMapValue) + "</p>"
                "<p><strong>Turn Value:</strong> " + String(TurnMapValue) + "</p>"
                "<p><strong>Safety Value:</strong> " + SafetyStatus + "</p>"
                "<p><strong>Mode Value:</strong> " + ModeStatus + "</p>"
                "<h2>Control Motor Speed:</h2>"
                "<form action=\"/setSpeed\" method=\"get\">"
                "<label for=\"RightSpeed\">Right Motor Speed (0-255):</label>"
                "<input type=\"number\" id=\"RightSpeed\" name=\"RightSpeed\" min=\"0\" max=\"255\" value=\"" + String(RightSpeed) + "\"><br><br>"
                "<label for=\"LeftSpeed\">Left Motor Speed (0-255):</label>"
                "<input type=\"number\" id=\"LeftSpeed\" name=\"LeftSpeed\" min=\"0\" max=\"255\" value=\"" + String(LeftSpeed) + "\"><br><br>"
                "<input type=\"submit\" value=\"Set Speed\">"
                "</form>"
                "</body>"
                "</html>";

  Server.send(200, "text/html", Html);
}

// Handler to receive motor speed via HTTP request
void handleSetSpeed() {
  if (Server.hasArg("RightSpeed") && Server.hasArg("LeftSpeed")) {
    RightSpeed = Server.arg("RightSpeed").toInt();
    LeftSpeed = Server.arg("LeftSpeed").toInt();
    //Serial.print("Received Speed: ");
    //Serial.print("Right: ");
    //Serial.print(RightSpeed);
    //Serial.print(", Left: ");
    //Serial.println(LeftSpeed);
  }
  Server.sendHeader("Location", "/");  // Redirect back to the root page
  Server.send(303);                    // HTTP status code for redirect
}