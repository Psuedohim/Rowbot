#include <MPU6050_tockn.h>
#include <Wire.h>
MPU6050 mpu6050(Wire);

int fl = 3;
int fr = 6;
int bl = 10;
int br = 11;
int thrust;
int fl_thrust, fr_thrust, bl_thrust, br_thrust;
double angx, angy, less_angx, less_angy, more_angx, more_angy, start_angx, start_angy, var;
int desired_height = 12;
int trigPin = 4;
int echoPin = 5;
int array[10][7];
int i = 0;

void setup() {
 Serial.begin(9600);
fl_thrust = 130;
fr_thrust = 130;
bl_thrust = 130;
br_thrust = 130;
 pinMode(echoPin, INPUT);
 pinMode(trigPin,OUTPUT);
 Wire.begin();
int height = 0;
init_esc();
Serial.print("HI");
 mpu6050.begin();
 mpu6050.calcGyroOffsets(true);

 const double start_angx = mpu6050.getAngleX();
 const double start_angy = mpu6050.getAngleY();
 delay(1000);
  var = 40;
  less_angx = start_angx - var;
  more_angx = start_angx + var;
  less_angy = start_angy - var;
  more_angy = start_angy + var;

}


void loop() {  
   mpu6050.update();

  angx = mpu6050.getAngleX();
  array[i][0] = angx;
  angy = mpu6050.getAngleY();
  array[i][1] = angy;
  delay(500);
  digitalWrite(trigPin, LOW);
  delayMicroseconds(100);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(100);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH);
  double inches = (duration/2) / 74; 
  Serial.println(inches);
  array[i,7];
  if (inches < desired_height)
   { 
  Serial.println("+");
//  fl_thrust = fl_thrust + 1;
//  fr_thrust = fr_thrust + 1;
//  bl_thrust = bl_thrust + 1;
//  br_thrust = br_thrust + 1;
  analogWrite(fl, fl_thrust);
  analogWrite(fr, fr_thrust);
  analogWrite(bl, bl_thrust);
  analogWrite(br, br_thrust);
    array[i][2];
   }
  if (inches > desired_height)
  {
    Serial.print("-");
  fl_thrust = fl_thrust - 1;
  fr_thrust = fr_thrust - 1;
  bl_thrust = bl_thrust - 1;
  br_thrust = br_thrust - 1;
  analogWrite(fl, fl_thrust);
  analogWrite(fr, fr_thrust);
  analogWrite(bl, bl_thrust);
  analogWrite(br, br_thrust);
    array[i][2];
  }
 if (angy< less_angy) {
    Serial.println("Lift left:" + String(angy));
  fl_thrust = fl_thrust - 1;
  bl_thrust = bl_thrust - 1;
//    analogWrite(fr, fr_thrust);
//    analogWrite(br, br_thrust);
    analogWrite(fl, fr_thrust);
    analogWrite(bl, br_thrust);
  array[i][3];
  }
  
  if (angy > more_angy) {
    Serial.println("Lift right:" + String(angy));

  fr_thrust = fr_thrust + 1;
  br_thrust = br_thrust + 1;
//    analogWrite(fl, fr_thrust);
//    analogWrite(bl, bl_thrust);
    analogWrite(fr, fr_thrust);
    analogWrite(br, br_thrust);
  array[i][3];
  }

   if (angx < less_angx) {
     Serial.println("Lift For:" + String(angx));   
  fl_thrust = fl_thrust + 1;
  fr_thrust = fr_thrust + 1;
     analogWrite(fr, fr_thrust);
     analogWrite(fl, fl_thrust);
//     analogWrite(br, br_thrust);
//     analogWrite(bl, bl_thrust);
 array[i][4];
  }
   if (angx > more_angx) {
     Serial.println("Lift Back:" + String(angx));
  bl_thrust = bl_thrust + 1;
  br_thrust = br_thrust + 1;
     analogWrite(br, br_thrust);
     analogWrite(bl, bl_thrust);
     analogWrite(fr, fr_thrust);
     analogWrite(fl, fl_thrust);
 array[i][4];
   }
  Serial.println(String(fl_thrust));
  Serial.println(String(fr_thrust));
  Serial.println(String(bl_thrust));
  Serial.println(String(br_thrust));
   if( i <= 9)
   i++;
   else
   i = 0;
}

void init_esc(){
 delay(3000);
 thrust = 254;
 Serial.println(thrust);
 analogWrite(fl, thrust);
 analogWrite(fr, thrust);
 analogWrite(bl, thrust);
 analogWrite(br, thrust);
 delay(1000);
 
 thrust = 1;
 Serial.println(thrust);
 analogWrite(fl, thrust);
 analogWrite(fr, thrust);
 analogWrite(bl, thrust);
 analogWrite(br, thrust);
 delay(1000);
}
//bool is_thrust_max(){
//  return (fl_thrust < 255 && fr_thrust < 255 && bl_thrust < 255 && br_thrust < 255);
//}
//
//bool is_thrust_min(){
//  return (fl_thrust > 0 && fr_thrust > 0 && bl_thrust > 0 && br_thrust > 0);
//}
