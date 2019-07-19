#include <Wire.h>

#define ADDR 1
#define LED 3

// int ADDR = 1;
char signal;


void setup()
{
    Serial.begin(9600);
    pinMode(LED, OUTPUT);
    pinMode(LED_BUILTIN, OUTPUT);
    Wire.begin(ADDR);  // Start I2C bus as slave.
    Wire.onReceive(receiveEvent); // Function to trigger when something is received.
    digitalWrite(LED, HIGH);
    delay(2000);
    digitalWrite(LED, LOW);
}

void receiveEvent(int x)
{
    digitalWrite(LED_BUILTIN, HIGH);
    delay(100);
    digitalWrite(LED_BUILTIN, LOW);
    signal = Wire.read();
    Serial.println(signal);
    if (signal == '1')
        digitalWrite(LED, HIGH);
    else
        digitalWrite(LED, LOW);
}
void loop()
{
    delay(100);
}
