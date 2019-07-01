#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include "src/WiFiCredentials/WiFiCredentials.h"

WiFiCredentials credentials;
WiFiUDP Udp;


char SSID = credentials.ssid();
char PASSWORD = credentials.password();

unsigned int PORT = PORT;  // local port to listen on
char incomingPacket[255];  // buffer for incoming packets
char  replyPacket[] = "Hi there! Got the message :-)";  // a reply string to send back


void setup()
{
  Serial.begin(115200);
  Serial.println();

  WiFi.softAP(SSID, PASSWORD);
  IPAddress ip = WiFi.softAPIP();
  // Serial.printf("Connecting to %s ", ssid);
  // WiFi.begin(SSID, PASSWORD);
  // while (WiFi.status() != WL_CONNECTED)
  // {
  //   delay(500);
  //   Serial.print(".");
  // }
  // Serial.println(" connected");

  Udp.begin(PORT);
  Serial.printf("Now listening at IP %s, UDP port %d\n", WiFi.localIP().toString().c_str(), PORT);
}


void loop()
{
  int packetSize = Udp.parsePacket();
  if (packetSize)
  {
    // receive incoming UDP packets
    Serial.printf("Received %d bytes from %s, port %d\n", packetSize, Udp.remoteIP().toString().c_str(), Udp.remotePort());
    int len = Udp.read(incomingPacket, 255);
    if (len > 0)
    {
      incomingPacket[len] = 0;
    }
    Serial.printf("UDP packet contents: %s\n", incomingPacket);

    // send back a reply, to the IP address and port we got the packet from
    Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
    Udp.write(replyPacket);
    Udp.endPacket();
  }
}
