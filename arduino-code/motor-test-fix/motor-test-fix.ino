#define RPWM_KA_PIN 12
#define LPWM_KA_PIN 13

#define RPWM_KI_PIN 18
#define LPWM_KI_PIN 19
 
void setup() {
  pinMode(RPWM_KA_PIN, OUTPUT);
  pinMode(LPWM_KA_PIN, OUTPUT);
  analogWrite(RPWM_KA_PIN, 0);
  analogWrite(LPWM_KA_PIN, 0);

  pinMode(RPWM_KI_PIN, OUTPUT);
  pinMode(LPWM_KI_PIN, OUTPUT);
  analogWrite(RPWM_KI_PIN, 0);
  analogWrite(LPWM_KI_PIN, 0);
}
 
void loop() {
  ForwardRight(128);
  ForwardLeft(128);
  delay(3000);
  ReverseRight(128);
  ReverseLeft(128);
  delay(3000);
}

void ForwardRight(int pwm){
  analogWrite(RPWM_KA_PIN, pwm);
  analogWrite(LPWM_KA_PIN, 0);
}

void ReverseRight(int pwm){
  analogWrite(LPWM_KA_PIN, pwm);
  analogWrite(RPWM_KA_PIN, 0);
}

void ForwardLeft(int pwm){
  analogWrite(RPWM_KI_PIN, pwm);
  analogWrite(LPWM_KI_PIN, 0);
}

void ReverseLeft(int pwm){
  analogWrite(LPWM_KI_PIN, pwm);
  analogWrite(RPWM_KI_PIN, 0);
}