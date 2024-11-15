#include <AlfredoCRSF.h>
#include <HardwareSerial.h>

#define ELRS_RX_PIN 16
#define ELRS_TX_PIN 17

#define MOTOR_RIGHT_RPWM_PIN 12
#define MOTOR_RIGHT_LPWM_PIN 13

#define MOTOR_LEFT_RPWM_PIN 18
#define MOTOR_LEFT_LPWM_PIN 19

// Set up a new Serial object
HardwareSerial crsfSerial(1);
AlfredoCRSF crsf;

int ThrottleValue;
int TurnValue;
int SafetyValue;
int ModeValue;

int ThrottleMapValue;
int TurnMapValue;

void setup() {
  Serial.begin(115200);
  crsfSerial.begin(CRSF_BAUDRATE, SERIAL_8N1, ELRS_RX_PIN, ELRS_TX_PIN);
  if (!crsfSerial) while (1) Serial.println("Invalid crsfSerial configuration");
  crsf.begin(crsfSerial);
}

void loop() {
    crsf.update();
    ThrottleValue = crsf.getChannel(3);
    TurnValue = crsf.getChannel(1);
    SafetyValue = crsf.getChannel(5);
    ModeValue = crsf.getChannel(6);

    if (SafetyValue >= 1800){
      ThrottleMapValue = map(ThrottleValue, 1000, 2000, 0, 200);
      TurnMapValue = map(TurnValue, 1000, 2000, -100, 100);

      ForwardRight(constrain(ThrottleMapValue - TurnMapValue, 0, 250));
      ForwardLeft(constrain(ThrottleMapValue + TurnMapValue, 0, 250));
    } else {
      ForwardRight(0);
      ForwardLeft(0);
    }

    delay(50);
}

void ForwardRight(int pwm){
  analogWrite(MOTOR_RIGHT_LPWM_PIN, pwm);
  analogWrite(MOTOR_RIGHT_RPWM_PIN, 0);
}

void ReverseRight(int pwm){
  analogWrite(MOTOR_RIGHT_RPWM_PIN, pwm);
  analogWrite(MOTOR_RIGHT_LPWM_PIN, 0);
}

void ReverseLeft(int pwm){
  analogWrite(MOTOR_LEFT_RPWM_PIN, pwm);
  analogWrite(MOTOR_LEFT_LPWM_PIN, 0);
}

void ForwardLeft(int pwm){
  analogWrite(MOTOR_LEFT_LPWM_PIN, pwm);
  analogWrite(MOTOR_LEFT_RPWM_PIN, 0);
}