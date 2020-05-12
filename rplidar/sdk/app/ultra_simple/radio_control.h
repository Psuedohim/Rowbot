// #include "header.h"

// Max size of this struct is 32 bytes - NRF24L01 buffer limit
struct Data_Package {
  uint8_t j1PotX;
  uint8_t j1PotY;
  uint8_t j1Button;
  uint8_t j2PotX;
  uint8_t j2PotY;
  uint8_t j2Button;
  uint8_t pot1;
  uint8_t pot2;
  uint8_t tSwitch1;
  uint8_t tSwitch2;
  uint8_t button1;
  uint8_t button2;
  uint8_t button3;
  uint8_t button4;
};

void setup_radio();
void radio_rx();
void read_radio();
void reset_data();