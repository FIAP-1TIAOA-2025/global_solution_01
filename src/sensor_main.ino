#include <Arduino.h>

#define TRIG_PIN 16
#define ECHO_PIN 17

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

void loop() {
  // Envia pulso para o sensor
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Lê o tempo do pulso de retorno
  long duration = pulseIn(ECHO_PIN, HIGH);
  // Calcula a distância em centímetros
  long distance = duration * 0.0343 / 2;

  if (distance < 300) {
    Serial.println("ALERTA: Nível de água alto! Risco de enchente!");
  }

  delay(5000); // Mede a cada 5 segundos
}