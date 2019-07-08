#include "Arduino.h"
#include "WiFiCredentials.h"

WiFiCredentials::WiFiCredentials(){
    _ssid="YOUR_SSID_HERE";
    _pwd="YOUR_WIFI_PASSWORD_HERE";
}
WiFiCredentials::~WiFiCredentials(){
  _ssid="";
  _pwd="";
}
char* WiFiCredentials::ssid(){
  return _ssid;
}

char* WiFiCredentials::password(){
  return _pwd;
}