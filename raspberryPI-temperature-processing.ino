#include <DS18B20.h>
int relayPin = 2;
DS18B20 ds(21);
int ntcPin = 28;
int lm35Pin = 27;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH);
}

void loop() {
  // put your main code here, to run repeatedly:
if (Serial.available() > 0) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();

    if (msg == "ON") {
      digitalWrite(relayPin, LOW);
      Serial.println("Relay: ON");
    } else if (msg == "OFF") {
      digitalWrite(relayPin, HIGH);
      Serial.println("Relay: OFF");
    }
  }
  
  double voltage_ntc = (3.3 / 4095.0) * analogRead(ntcPin); //analogRead(pin number here);
  double Tntc = (voltage_ntc + 0.0281)/0.0405; //17 a 44ºC a = 0.0405 b = -0.0281

  double voltage_lm35 = (3.3 / 4095.0) * analogRead(lm35Pin);
  double Tlm35 = (voltage_lm35 + 0.013336)/0.0425; //10 a 60ºC a = 0.0425 b = -0.013336

  double Tds18b20 = 0.0;
  while (ds.selectNext()) {
    Tds18b20 = ds.getTempC();
  }

  Serial.print(Tntc);
  Serial.print(",");
  Serial.print(voltage_ntc);
  Serial.print(",");
  Serial.print(Tlm35);
  Serial.print(",");
  Serial.print(voltage_lm35);
  Serial.print(",");
  Serial.println(Tds18b20);

  delay(1000); 
}
