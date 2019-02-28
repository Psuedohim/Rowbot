using namespace std;
int mo1 = 7;
int mo2 = 8;
int mot3 = 6;
int mot4 = 5;
void setup() {
  // put your setup code here, to run once:

pinMode(8, OUTPUT);
pinMode(7, OUTPUT);
pinMode(6,OUTPUT);
pinMode(5,OUTPUT);
Serial.begin(9600);
char input = Serial.read();
}

void loop() {
  // put your main code here, to run repeatedly:
digitalWrite(8,LOW);
digitalWrite(7,LOW);
digitalWrite(6,HIGH);
digitalWrite(5,HIGH);
delay(10);

digitalWrite(8,HIGH);
digitalWrite(7,LOW);
digitalWrite(6,HIGH);
digitalWrite(5,LOW);
delay(10);

digitalWrite(8,HIGH);
digitalWrite(7,HIGH);
digitalWrite(6,LOW);
digitalWrite(5,LOW);
delay(10);

digitalWrite(8,LOW);
digitalWrite(7,HIGH);
digitalWrite(6,LOW);
digitalWrite(5,HIGH);
delay(10);
}