#include <Wire.h>

// Bytes coming from RockPi or a drive-manager device.
#define ADDR 0x04 // Address for this device over I2C.

// Define pinouts
#define DriveEn 2
#define SteerEn 3
#define DriveDir 4
#define SteerDir 5
#define DrivePWM 10
#define SteerPWM 11
#define SteerPot A0

// Variables for motor control.
const int DriveAcceleration = 10; // Delay for controlling acceleration.
const int SteerAcceleration = 5;  // Delay for controlling acceleration.
int DrivePWMValue = 0;            // PWM value for speed control.
int SteerPWMValue = 0;            // PWM value for speed control.
int SteerPotValue;                // potentiometer reading from steering column.
const int MinSteerAngle = 514;    // Lower limit for steering pot value.
const int MidSteerAngle = 882;    // Value when wheels are pointed straight.
const int MaxSteerAngle = 1024;   // Upper limit for steering pot value.

// bool forwardsPressed = false;
// bool backwardsPressed = false;
// bool rightPressed = false;
// bool leftPressed = false;

// Byte communication code.
int incomingByte;
#define FORWARD_FLAG 1
#define BACKWARD_FLAG 2
#define STOP_FLAG 3
#define LEFT_FLAG 4
#define RIGHT_FLAG 5
#define CENTER_FLAG 6
// const int FORWARDS_PRESSED = 1;
// const int FORWARDS_RELEASED = 2;
// const int BACKWARDS_PRESSED = 3;
// const int BACKWARDS_RELEASED = 4;
// const int RIGHT_PRESSED = 5;
// const int RIGHT_RELEASED = 6;
// const int LEFT_PRESSED = 7;
// const int LEFT_RELEASED = 8;

void initOutputs()
{
  // Set motor driver pinouts as output.
  pinMode(SteerEn, OUTPUT);
  pinMode(SteerDir, OUTPUT);
  // pinMode(SteerPWM, OUTPUT);
  pinMode(DriveEn, OUTPUT);
  pinMode(DriveDir, OUTPUT);
  // pinMode(DrivePWM, OUTPUT);
  // Analog pin as input. Not necessary, just as reference.
  // pinMode(SteerPot, INPUT);
}

int increment(int valToIncrement)
{
  // Increment parameter value by one.
  if (valToIncrement < 255)
    valToIncrement++;
  return valToIncrement;
}

void moveForwards()
{
  // Forward signal to motor driver.
  digitalWrite(DriveEn, HIGH);
  digitalWrite(DriveDir, HIGH);
  DrivePWMValue = increment(DrivePWMValue);
  analogWrite(DrivePWM, DrivePWMValue);
  delay(DriveAcceleration);
}

void moveBackwards()
{
  // Backward signal to motor driver.
  digitalWrite(DriveEn, HIGH);
  digitalWrite(DriveDir, LOW);
  DrivePWMValue = increment(DrivePWMValue);
  analogWrite(DrivePWM, DrivePWMValue);
  delay(DriveAcceleration);
}

void turnRight()
{
  // Right turn signal to motor driver.
  if (analogRead(SteerPot) <= MaxSteerAngle) // If wheels not at max:
  {
    digitalWrite(SteerEn, HIGH);
    digitalWrite(SteerDir, HIGH);
    SteerPWMValue = increment(SteerPWMValue);
    analogWrite(SteerPWM, SteerPWMValue);
    delay(SteerAcceleration);
  }
}

void turnLeft()
{
  // Left turn signal to motor driver.
  if (analogRead(SteerPot) >= MinSteerAngle) // If wheels not at min:
  {
    digitalWrite(SteerEn, HIGH);
    digitalWrite(SteerDir, LOW);
    SteerPWMValue = increment(SteerPWMValue);
    analogWrite(SteerPWM, SteerPWMValue);
    delay(SteerAcceleration);
  }
}

void resetSteering()
{
  // Center wheels when not turning left or right.
  SteerPWMValue = 0;
  int SteerPotReading = analogRead(SteerPot);
  if (SteerPotReading < MidSteerAngle)
    turnRight();
  else if (SteerPotReading > MidSteerAngle)
    turnLeft();
}

void resetEngine()
{
  // Stop drive motor when not going forwards or backwards.
  digitalWrite(DriveEn, LOW);
  digitalWrite(DriveDir, LOW);
  analogWrite(DrivePWM, 0);
  DrivePWMValue = 0;
}

void handleIncomingByte()
{
  // Use truth values from handleIncomingByte to control motor driver.
  if (incomingByte == FORWARD_FLAG)
    moveForwards();
  else if (incomingByte == BACKWARD_FLAG)
    moveBackwards();
  else //if (incomingByte == STOP_FLAG)
    resetEngine();

  if (incomingByte == LEFT_FLAG)
    turnLeft();
  else if (incomingByte == RIGHT_FLAG)
    turnRight();
  else //if (incomingByte == CENTER_FLAG)
    resetSteering();

  // Set truth value corresponding to key pressed.
  // if (incomingByte == FORWARDS_PRESSED)
  //   forwardsPressed = true;
  //   backwardsPressed = false;
  // else if (incomingByte == BACKWARDS_PRESSED)
  //   backwardsPressed = true;
  //   forwardsPressed = false;

  // if (incomingByte == FORWARDS_RELEASED)
  //   forwardsPressed = false;
  // else if (incomingByte == BACKWARDS_RELEASED)
  //   backwardsPressed = false;

  // if (incomingByte == RIGHT_PRESSED)
  //   rightPressed = true;
  //   leftPressed = false;
  // else if (incomingByte == LEFT_PRESSED)
  //   leftPressed = true;
  //   rightPressed = false;

  // if (incomingByte == RIGHT_RELEASED)
  //   rightPressed = false;
  // else if (incomingByte == LEFT_RELEASED)
  //   leftPressed = false;
}

// void handlePinOutputs()
// {
// if (forwardsPressed)
//   moveForwards();
// else if (backwardsPressed)
//   moveBackwards();
// else
//   resetEngine();

// if (rightPressed)
//   turnRight();
// else if (leftPressed)
//   turnLeft();
// else
//   resetSteering();
// }

void receiveEvent()
{
  // Set value of incomingByte to the received byte.
  if (Wire.available())
    incomingByte = Wire.read();
}

void setup()
{
  Serial.begin(9600);
  initOutputs();                // Initiate output pins.
  Wire.begin(ADDR);             // Join I2C bus on address ADDR.
  Wire.onReceive(receiveEvent); // Function to call when byte is received.
}

void loop()
{
  Serial.println(incomingByte);
  handleIncomingByte();
  // handlePinOutputs();
}
