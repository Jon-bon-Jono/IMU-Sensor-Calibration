#include <Arduino_LSM9DS1.h>
#include <ArduinoBLE.h>

char receivedChar;
float x, y, z;
char sendBuffer[100];
//initial sensor activations
boolean readAcc = false;
boolean readGyr = false;
boolean readMag = true;

BLEService calService("0000FFF0-0000-1000-8000-00805F9B34FB");
BLECharacteristic sendCharacteristic("0000FFF1-0000-1000-8000-00805F9B34FB", BLERead | BLENotify, 100);
BLECharacteristic recvCharacteristic("0000FFF2-0000-1000-8000-00805F9B34FB", BLERead | BLEWrite, 100);

void setup() {
  Serial.begin(19200);
  initIMU();
  initComms();
}

void loop() {
  BLE.poll();
  //send commands via serial to switch sensor
  if (Serial.available()) {
     receivedChar = Serial.read();
     switch (receivedChar) {
        case 'a':
           readAcc = !readAcc;
           readGyr = false;
           readMag = false;
           break;
        case 'g':
           readGyr = !readGyr;
           readGyr = false;
           readMag = false;
           break;
        case 'm':
           readMag = !readMag;
           readGyr = false;
           readMag = false;
           break;
     }
  }
  sendData();
}

void sendData(){
  if(readAcc) {
    IMU.readAcceleration(x, y, z);  
  }
  if(readGyr) {
    IMU.readGyroscope(x, y, z);
  }
  if(readMag) {
    IMU.readMagneticField(x, y, z);
  }
  static char buffer[100] = { 0 };
  snprintf(buffer, 100, "%.3f %.3f %.3f#", x, y, z);
  commsSend(buffer);
}

void initIMU() {
  IMU.begin();
  delay(1000);
  //wait for sensors to be available
  while (!IMU.accelerationAvailable() || !IMU.gyroscopeAvailable() || !IMU.magneticFieldAvailable()) {};
}

void initComms(){
  if (!BLE.begin()) Serial.println("starting BLE failed");
  BLE.setLocalName("calibration data");
  BLE.setAdvertisedService(calService);

  calService.addCharacteristic(sendCharacteristic);
  calService.addCharacteristic(recvCharacteristic);
  BLE.addService(calService);
  BLE.advertise();
}

void commsSend(const char string[]) {
  char buffer[20];
  int len = strlen(string);
  for (int i=0; i<len; i+=(20-1)) {
    snprintf(buffer, 20, "%s", &string[i]);
    sendCharacteristic.writeValue(buffer); // send copy to BLE stream
    Serial.write(buffer); //send copy to serial port
    Serial.flush(); Serial.println();
    delay(20);
  }
}
