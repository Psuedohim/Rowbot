
int motor1 = A0;
int motor2 = A1;

motor1 = constrain(motor1,0,1023);
motor2 = constrain(motor2, 0, 1023);

void setup()
{
Serial.begin(9600);

}

void loop()
{
analogWrite(motor1,HIGH);
analogWrite(motor2,HIGH);
}