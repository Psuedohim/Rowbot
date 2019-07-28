#include <Wire.h>

// Bytes coming from RockPi or a drive-manager device.
#define ADDR 0x04 // Address for this device over I2C.

// Define pinouts
#define DriveEn 1
#define SteerEn 2
#define DriveDir 3
#define SteerDir 4
#define DrivePWM 5
#define SteerPWM 6
#define SteerPot A0

// Variables for motor control.
const int DriveAcceleration = 10; // Delay for controlling acceleration.
const int SteerAcceleration = 5;  // Delay for controlling acceleration.
int DrivePWMValue = 0;            // PWM value for speed control.
int SteerPWMValue = 0;            // PWM value for speed control.
int SteerPotValue = 0;            // potentiometer reading from steering column.
int MinSteerAngle = 514;          // Lower limit for steering pot value.
int MidSteerAngle = 882;          // Value when wheels are pointed straight.
int MaxSteerAngle = 1024;         // Upper limit for steering pot value.

bool forwardsPressed = false;
bool backwardsPressed = false;
bool rightPressed = false;
bool leftPressed = false;

// Byte communication code.
int incomingByte;
const int FORWARDS_PRESSED = 1;
const int FORWARDS_RELEASED = 2;
const int BACKWARDS_PRESSED = 3;
const int BACKWARDS_RELEASED = 4;
const int RIGHT_PRESSED = 5;
const int RIGHT_RELEASED = 6;
const int LEFT_PRESSED = 7;
const int LEFT_RELEASED = 8;

void initOutputs()
{
  // Set motor driver pinouts as output.
  pinMode(SteerEn, OUTPUT);
  pinMode(SteerDir, OUTPUT);
  pinMode(SteerPWM, OUTPUT);
  pinMode(DriveEn, OUTPUT);
  pinMode(DriveDir, OUTPUT);
  pinMode(DrivePWM, OUTPUT);
}

void increment(int valToIncrement)
{
  // Increment parameter value by one.
  if (valToIncrement < 255)
    valToIncrement++;
}

void moveForwards()
{
  // Forward signal to motor driver.
  digitalWrite(DriveEn, HIGH);
  digitalWrite(DriveDir, HIGH);
  increment(DrivePWMValue);
  analogWrite(DrivePWM, DrivePWMValue);
  delay(DriveAcceleration);
}

void moveBackwards()
{
  // Backward signal to motor driver.
  digitalWrite(DriveEn, HIGH);
  digitalWrite(DriveDir, LOW);
  increment(DrivePWMValue);
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
    increment(SteerPWMValue);
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
    increment(SteerPWMValue);
    analogWrite(SteerPWM, SteerPWMValue);
    delay(SteerAcceleration);
  }
}

void resetSteering()
{
  // Center wheels when not turning left or right.
  if (analogRead(SteerPot) < MidSteerAngle)
    turnRight();
  else if (analogRead(SteerPot) > MidSteerAngle)
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
  // Set truth value corresponding to key pressed.
  if (incomingByte == FORWARDS_PRESSED)
    forwardsPressed = true;
  else if (incomingByte == BACKWARDS_PRESSED)
    backwardsPressed = true;

  if (incomingByte == FORWARDS_RELEASED)
    forwardsPressed = false;
  else if (incomingByte == BACKWARDS_RELEASED)
    backwardsPressed = false;

  if (incomingByte == RIGHT_PRESSED)
    rightPressed = true;
  else if (incomingByte == LEFT_PRESSED)
    leftPressed = true;

  if (incomingByte == RIGHT_RELEASED)
    rightPressed = false;
  else if (incomingByte == LEFT_RELEASED)
    leftPressed = false;
}

void handlePinOutputs()
{
  // Use truth values from handleIncomingByte to control motor driver.
  if (forwardsPressed)
    moveForwards();
  else if (backwardsPressed)
    moveBackwards();
  else
    resetEngine();

  if (rightPressed)
    turnRight();
  else if (leftPressed)
    turnLeft();
  else
    resetSteering();
}

void receiveEvent()
{
  // Set value of incomingByte to the received byte when it is received.
  incomingByte = Wire.read();
}

void setup()
{
  Serial.begin(9600);
  initOutputs();                // Initiate output pins.
  Wire.begin(ADDR);             // Join I2C bus on address ADDR.
  Wire.onReceive(receiveEvent); // Function called when byte is received.
}

void loop()
{
  handleIncomingByte();
  handlePinOutputs();
}