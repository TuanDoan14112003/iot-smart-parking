
#include <SPI.h>
#include <MFRC522.h>
#include <ArduinoJson.h>
#include <Servo.h>
#include <Ultrasonic.h>
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27,20,4);
#define RST_PIN 9
#define SS_PIN 10
#define TRIG_PIN 7
#define ECHO_PIN 6
Ultrasonic ultrasonic(TRIG_PIN, ECHO_PIN);
StaticJsonDocument<200> doc;

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance
Servo servo1;
//*****************************************************************************************//
void setup() {
  Serial.begin(9600);
  SPI.begin();
  lcd.init();
  lcd.backlight();
  mfrc522.PCD_Init();
  servo1.attach(8);
  servo1.write(0);
  lcd.clear();

  // Serial.println(F("Read personal data on a MIFARE PICC:"));
}

//*****************************************************************************************//
bool readData(byte blockNumber, byte buffer1[]) {
  MFRC522::MIFARE_Key key;
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;
  MFRC522::StatusCode status;
  byte len = 18;

  //------------------------------------------- GET FIRST NAME
  status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, blockNumber, &key, &(mfrc522.uid));  //line 834 of MFRC522.cpp file
  if (status != MFRC522::STATUS_OK) {
    // Serial.print(F("Authentication failed: "));
    // Serial.println(mfrc522.GetStatusCodeName(status));
    return false;
  }

  status = mfrc522.MIFARE_Read(blockNumber, buffer1, &len);
  if (status != MFRC522::STATUS_OK) {
    // Serial.print(F("Reading failed: "));
    // Serial.println(mfrc522.GetStatusCodeName(status));
    return false;
  }

  return true;
}
int numberOfSlot;
void loop() {
  int distance = ultrasonic.read();
  if (distance < 10) {
    numberOfSlot = 0;
  } else {
    numberOfSlot = 1;
  }
  lcd.setCursor(0, 0);
  lcd.print("There is: " + String(numberOfSlot) + " slots");
  //  if (Serial.available()>0) {
  //   String a = Serial.readString();
  //   a.trim();
  //   if (a == "open") {
  //     servo1.write(90);
  //     delay(2000);
  //     servo1.write(0);
  //   }
  //  }
  

  // if (!mfrc522.PICC_IsNewCardPresent()) {
  //   return;
  // }


  // if (!mfrc522.PICC_ReadCardSerial()) {
  //   return;
  // }


  // byte nameBuffer[18];
  // byte phoneBuffer[18];
  // byte modelBuffer[18];
  // byte plateBuffer[18];
  // byte passwordBuffer[18];
  // if (readData(57, nameBuffer) && readData(58, phoneBuffer) && readData(61, modelBuffer) && readData(62, plateBuffer) && readData(53,passwordBuffer)) {
  //   String name;
  //   for (uint8_t i = 0; i < 16; i++) {
  //     // if (buffer[i] != 32) {
  //     name += char(nameBuffer[i]);
  //     // }
  //   }
  //   name.trim();



  //   String phone;
  //   for (uint8_t i = 0; i < 16; i++) {

  //     phone += char(phoneBuffer[i]);
  //   }
  //   phone.trim();

  //   String model;
  //   for (uint8_t i = 0; i < 16; i++) {

  //     model += char(modelBuffer[i]);
  //   }
  //   model.trim();


  //   String plate;
  //   for (uint8_t i = 0; i < 16; i++) {

  //     plate += char(plateBuffer[i]);
  //   }
  //   plate.trim();

  //   String password;
  //   for (uint8_t i = 0; i < 16; i++) {

  //     password += char(passwordBuffer[i]);
  //   }
  //   password.trim();

  //   doc["password"] = password;
  //   doc["name"] = name;
  //   doc["phone"] = phone;
  //   doc["model"] = model;
  //   doc["plate"] = plate;
  //   serializeJson(doc, Serial);
  //   Serial.println();
  // }
  // // delay(1000);  //change value if you want to read cards faster

  // mfrc522.PICC_HaltA();
  // mfrc522.PCD_StopCrypto1();
}
//*****************************************************************************************//
