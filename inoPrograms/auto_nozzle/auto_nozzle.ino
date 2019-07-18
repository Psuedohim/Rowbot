#include <Servo.h>

int valx,valy,led1;


Servo motor1,motor2;

void gox(int valx)
{
  motor1.write(valx);
}

void goy(int valy)
{
 motor2.write(valy);
}
void led(int led1)
{
 digitalWrite(led1,HIGH);
 delay(500);
 digitalWrite(led1,LOW);
}


void setup() 
{
  pinMode(12,OUTPUT);
  motor1.attach(8);
  motor2.attach(9);
//  valx = map(valx,0,180,0,1300);
//  valy = map(valy,0,180,0,600);
Serial.begin(9600);
  Serial.setTimeout(-1);
}

void loop() {
  Serial.println("Enter in a X and Y value: ");
  while (Serial.available() == 0) {}
  valx =Serial.parseInt();
    valx = map(valx,0,180,0,1300);
  while (Serial.available() == 0) {}
 valy= Serial.parseInt();
 valy = map(valy,0,180,0,600);
  gox(valx);
  goy(valy);
  delay(750);
  led(12);
  Serial.println("Val X = " +String(valx));
  Serial.println("Val Y = " +String(valy));
}