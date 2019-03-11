#include <SoftwareSerial.h>
/*
 * We need to plug in the BT TX/RX into
 * different ports from the default
 * Arduino TX/RX ports because the code
 * uploader gets confused and errors
 * out for some reason.
 */
SoftwareSerial bluetoothSerial(7, 8); // Rx, Tx

int red_led = 11;
int green_led = 12;
int blue_led = 13;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  Serial.begin(9600); // Default communication rate of the Serial module
  Serial.println("serial start");
  Serial.write(LED_BUILTIN);

  bluetoothSerial.begin(9600);
  bluetoothSerial.println("bt start");
}

void loop() {
  // Keep reading from HC-05 and send to Arduino Serial Monitor
  if (bluetoothSerial.available()) {
    Serial.println(bluetoothSerial.readString());
  }

  // Keep reading from Arduino Serial Monitor and send to HC-05
  if (Serial.available()) {
    bluetoothSerial.println(Serial.readStringUntil('\n'));
  }
}

