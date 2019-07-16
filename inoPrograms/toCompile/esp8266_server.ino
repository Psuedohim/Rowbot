#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include "src/WiFiCredentials/WiFiCredentials.h"

// Create instances for WiFi usage.
// IPAddress ClientIP(192,168,4,2);  // Set client IP.
// IPAddress ServerIP(192,168,4,1);  // Set server IP.
WiFiCredentials credentials; // For WiFi credential retrieval.
WiFiUDP Udp;

// Variables for WiFi communication and serial communication.
byte incomingByte = 0;

char *SSID = credentials.ssid();         // Retrieve SSID from WiFiCredentials.cpp.
char *PASSWORD = credentials.password(); // Retrieve PASSWORD from WiFiCredentials.cpp.
char packetBuffer[255];                  // Buffer for incoming packets.

const int PORT = 80;        // Local port to listen on for UDP packets.
const int BAUD_RATE = 9600; // Baud Rate for serial communication.

// Define pinouts
#define DriveEn D0
#define SteerEn D1
#define DriveDir D2
#define SteerDir D3
#define DrivePWM D4
#define SteerPWM D5
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

void setupWiFi()
{
  WiFi.softAP(SSID, PASSWORD); // Setup access point from ESP8266.
  Udp.begin(PORT);             // Begin UDP on defined port.
}

void moveForwards()
{
  // Serial.println("Forwards");
  digitalWrite(DriveEn, HIGH);
  digitalWrite(DriveDir, HIGH);
  if (DrivePWMValue < 255)
    DrivePWMValue++;

  analogWrite(DrivePWM, DrivePWMValue);
  delay(DriveAcceleration);
}

void moveBackwards()
{
  // Serial.println("Backwards");
  digitalWrite(DriveEn, HIGH);
  digitalWrite(DriveDir, LOW);
  if (DrivePWMValue < 255)
    DrivePWMValue++;

  analogWrite(DrivePWM, DrivePWMValue);
  delay(DriveAcceleration);
}

void turnRight()
{
  // Serial.println("Right");
  if (analogRead(SteerPot) <= MaxSteerAngle) // If wheels not at max:
  {
    digitalWrite(SteerEn, HIGH);
    digitalWrite(SteerDir, HIGH);
    if (SteerPWMValue < 255)
      SteerPWMValue++;

    analogWrite(SteerPWM, SteerPWMValue);
    delay(SteerAcceleration);
  }
}

void turnLeft()
{
  // Serial.println("Left");
  if (analogRead(SteerPot) >= MinSteerAngle) // If wheels not at min:
  {
    digitalWrite(SteerEn, HIGH);
    digitalWrite(SteerDir, LOW);
    if (SteerPWMValue < 255)
      SteerPWMValue++;

    analogWrite(SteerPWM, SteerPWMValue);
    delay(SteerAcceleration);
  }
}

void resetSteering()
{
  if (analogRead(SteerPot) < MidSteerAngle)
    turnRight();

  else if (analogRead(SteerPot) > MidSteerAngle)
    turnLeft();
}

void resetEngine()
{
  digitalWrite(DriveEn, LOW);
  digitalWrite(DriveDir, LOW);
  analogWrite(DrivePWM, 0);
  DrivePWMValue = 0;
}

void detectKeyPresses()
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
  // Use truth values from detectKeyPresses to control motor driver.
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

void setup()
{
  // Serial.begin(BAUD_RATE); // Begin Serial communication on port 9600.
  initOutputs();
  setupWiFi();
}

void loop()
{
  int packetSize = Udp.parsePacket();
  if (packetSize)
  {
    // We've received a UDP packet.
    Udp.read(packetBuffer, packetSize);
    incomingByte = packetBuffer[0];
    // Serial.println(incomingByte);
    delay(20);
  }
  detectKeyPresses();
  handlePinOutputs();
}
