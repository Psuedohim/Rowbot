#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include "src/WiFiCredentials/WiFiCredentials.h"

WiFiCredentials credentials;  // For WiFi credential retrieval.
WiFiUDP Udp;
IPAddress ServerIP(192,168,4,1);  // Set server IP.
IPAddress ClientIP(192,168,4,2);  // Set client IP.

/*
Variables for WiFi communication and serial communication.
*/
byte incomingByte = 0;

char* SSID = credentials.ssid();  // Retrieve SSID from library.
char* PASSWORD = credentials.password();  // Retrieve PASSWORD from library.
char packetBuffer[255];  // Buffer for incoming packets.

const int PORT = 80;  // local port to listen on for UDP packets.
const int BAUD_RATE;  // Baud Rate for serial communication.

// Define pinouts
#define DriveEn D0
#define DriveDir D1
#define DrivePWM D2
#define SteerEn D3
#define SteerDir D4
#define SteerPWM D5

// Variables for motor control.
const int Acceleration = 10;  // Delay for controlling acceleration.
int DrivePWMValue = 0;  // PWM value for speed control.

bool forwardsPressed = false;
bool backwardsPressed = false;
bool rightPressed = false;
boot leftPressed = false;

const int FORWARDS_PRESSED = 1;
const int FORWARDS_RELEASED = 2;
const int BACKWARDS_PRESSED = 3;
const int BACKWARDS_RELEASED = 4;
const int RIGHT_PRESSED = 5;
const int RIGHT_RELEASED = 6;
const int LEFT_PRESSED = 7;
const int LEFT_RELEASED = 8;


void initOutputs() {
  // Set motor driver pinouts as output.
  pinMode(SteerIn1, OUTPUT);
  pinMode(SteerIn2, OUTPUT);
  pinMode(SteerIn3, OUTPUT);
  pinMode(SteerIn4, OUTPUT);
  pinMode(DriveEn, OUTPUT);
  pinMode(DriveDir, OUTPUT);
  pinMode(DrivePWM, OUTPUT);
}


void setupWiFi() {
  // Setup access point from ESP8266.
  // Set SSID, Password from src/WiFiCredentials/WiFiCredentials.h.
  WiFi.softAP(SSID, PASSWORD); 
  Udp.begin(PORT);  // Begin UDP on PORT.
}


void moveForwards() {  //dir high, en high
  digitalWrite(DriveEn, HIGH);
  digitalWrite(DriveDir, HIGH);
  if (DrivePWMValue < 255)
    DrivePWMValue += 1;
  analogWrite(DrivePWM, DrivePWMValue);
  delay(Acceleration);
}


void moveBackwards() {  //dir low, en high
  digitalWrite(DriveEn, HIGH);
  digitalWrite(DriveDir, LOW);
  if (DrivePWMValue< 255)
    DrivePWMValue += 1;
  analogWrite(DrivePWM, DrivePWMValue);
  delay(Acceleration);
}


void turnRight() {

}


void turnLeft() {

}


void resetSteering() {

}


void resetEngine() {

}


void detectKeyPresses() {
  // Set truth value corresponding to key pressed.
  if (incomingByte == FORWARDS_PRESSED) forwardsPressed = true;
  else if (incomingByte == BACKWARDS_PRESSED) backwardsPressed = true;

  if (incomingByte == FORWARDS_RELEASED) forwardsPressed = false;
  else if (incomingByte == BACKWARDS_RELEASED) backwardsPressed = false;

  if (incomingByte == RIGHT_PRESSED) rightPressed = true;
  else if (incomingByte == LEFT_PRESSED) leftPressed = true;

  if (incomingByte == RIGHT_RELEASED) rightPressed = false;
  else if (incomingByte == LEFT_RELEASED) leftPressed = false;
}


void handlePinOutputs() {
  // Use truth values from detectKeyPresses to control motor driver.
  if (forwardsPressed) moveForwards();
  else if (backwardsPressed) moveBackwards();
  else resetEngine();

  if (rightPressed) turnRight();
  else if (leftPressed) turnLeft();
  else resetSteering();
}


void setup()
{
  Serial.begin(9600);  // Begin Serial communication on port 9600.
  setupWiFi();
}


void loop()
{
  int packetSize = Udp.parsePacket();
  if (packetSize) {  // We've received a UDP packet.
    // read the packet into the buffer, we are reading only one byte
    Udp.read(packetBuffer, packetSize);
    incomingByte = packetBuffer[0];
    delay(20);
  }
  detectKeyPresses();
  handlePinOutputs();
}
