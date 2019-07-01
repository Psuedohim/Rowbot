#ifndef WiFiCredentials_h
#define WiFiCredentials_h

#include "Arduino.h"

class WiFiCredentials{
  public:
    WiFiCredentials();
    ~WiFiCredentials();
    char* ssid();
    char* password();
  private:
    char* _ssid;
    char* _pwd;
};

#endif