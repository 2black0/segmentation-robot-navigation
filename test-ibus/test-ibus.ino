#include <IBusBM.h>

IBusBM IBus;  // IBus object

/*
  For a given ESP32 serial port. rxPin and txPin can be specified for the serial ports 1 and 2 of ESP32 architectures 
  (default to RX1=9, TX1=10, RX2=16, TX2=17).
*/

//#define RX2  16

/*
  Read the number of a given channel and convert to the range provided.
  If the channel is off, return the default value
*/

int readChannel(byte channelInput, int minLimit, int maxLimit, int defaultValue) {
  uint16_t ch = IBus.readChannel(channelInput);
  if (ch < 100) return defaultValue;
  return map(ch, 1000, 2000, minLimit, maxLimit);
}

// Read the channel and return a boolean value
bool readSwitch(byte channelInput, bool defaultValue) {
  int intDefaultValue = (defaultValue) ? 100 : 0;
  int ch = readChannel(channelInput, 0, 100, intDefaultValue);
  return (ch > 50);
}

void setup() {
  // Start serial monitor
  Serial.begin(115200);
  IBus.begin(Serial2, 1);  // iBUS object connected to serial2 RX2 pin using timer 1
}

void loop(){

}
