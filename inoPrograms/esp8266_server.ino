#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>


int SERVER_PORT = 80;  // Match port on client side.

byte incomingByte = 0;
byte packetBuffer[512];

ESP8266WebServer server(SERVER_PORT);  // Init server.


void parseInstructions() {
    if (server.hasArg("direction")) {  // Variable sent from client.
        char directionRead = server.arg("direction");
        Serial.print(directionRead);
    }
}

void setup() {
    Serial.begin(9600);
    delay(1000);

    WiFi.softAP(ssid, password);
    IPAddress ip = WiFi.softAPIP();
    // When server recieves a direction, call parse instruction method.
    server.on("/direction/", HTTP_GET, parseInstructions);
    server.begin();
}

void loop() {
    server.handleClient();
}