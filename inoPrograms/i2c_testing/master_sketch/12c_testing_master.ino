#include <SharpIR.h>
#include <Wire.h>

#define IR_SENSOR A0
#define IR_MODEL SharpIR::GP2Y0A21YK0F
#define SLAVE_1 1  // Address for 1st slave arduino.

SharpIR sensor(IR_MODEL, IR_SENSOR);

int distance_cm;

void setup() 
{
    pinMode(LED_BUILTIN, OUTPUT);
    // Serial.begin(9600);
    Wire.begin(); // Start I2C bus as master.
}

void loop()
{
    distance_cm = sensor.getDistance();
    // Serial.println(distance_cm);
    Wire.beginTransmission(SLAVE_1);
    if (distance_cm <= 20)
    {
      Wire.write('1');
      digitalWrite(LED_BUILTIN, HIGH);
    }
    else
    {
      Wire.write('0');
      digitalWrite(LED_BUILTIN, LOW);
    }
    
    Wire.endTransmission();
}


