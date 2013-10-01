#include <Arduino.h>
void setup();
void loop();
#line 1 "src/serialBridge.ino"
#include <SoftwareSerial.h>

SoftwareSerial GSM(7,8);

void setup()
{
  Serial.begin(19200);
  GSM.begin(19200);
}

void loop()
{
  if(Serial.available()>0)
    GSM.write(Serial.read());
  if(GSM.available()>0)
    Serial.write(GSM.read());
}