
#include <SPI.h>
#include <MFRC522.h>      //MFRC522 library by Miki Balboa
#include <ArduinoJson.h>  //ArduinoJson library by Benoit Blanchon
#include <Servo.h>
#include <Ultrasonic.h>         // Ultrasonic library by Erick Simoes
#include <LiquidCrystal_I2C.h>  // LiquidCrystal I2C library by Frank de Brabander

#define RST_PIN 9
#define SS_PIN 10
#define TRIG_PIN 7
#define ECHO_PIN 6
#define RAIN_SENSOR_PIN A3
#define SERVO_PIN 8
#define CUSTOMERID_BLOCK 54
#define PASSWORD_BLOCK 53
#define NAME_BLOCK 57

LiquidCrystal_I2C lcd(0x27, 20, 4);
Ultrasonic ultrasonic(TRIG_PIN, ECHO_PIN);
StaticJsonDocument<200> doc;
MFRC522 mfrc522(SS_PIN, RST_PIN);
Servo servo1;
int numberOfSlot;  // The number of available parking slots in the parking area.
int waterVal = 0;

void setup() {
  Serial.begin(9600);
  SPI.begin();
  lcd.init();
  lcd.backlight();
  mfrc522.PCD_Init();
  servo1.attach(SERVO_PIN);
  servo1.write(0);
  lcd.clear();
}


bool readData(byte blockNumber, byte buffer1[]) {
  // This function reads the data on the blockNumber of the Mifare card and copy the data into a buffer
  // blockNumber: The block number on the Mifare card
  // buffer1: The buffer that the data will be copied into
  MFRC522::MIFARE_Key key;
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;
  MFRC522::StatusCode status;
  byte len = 18;

  status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, blockNumber, &key, &(mfrc522.uid));  // authenticate
  if (status != MFRC522::STATUS_OK) {
    return false;
  }

  status = mfrc522.MIFARE_Read(blockNumber, buffer1, &len);  // read the data on the blockNumber and copy the data into buffer
  if (status != MFRC522::STATUS_OK) {
    return false;
  }

  return true;
}


void loop() {
  waterVal = analogRead(RAIN_SENSOR_PIN);  // Read the data of the water sensor
  lcd.setCursor(0, 1);
  if (waterVal > 100) {
    lcd.print("Grab an umbrella");  // Display the text if the value is larger than 100
  } else {
    lcd.print("                  ");  // Clear the text
  }

  int distance = ultrasonic.read();  // Read the value of the ultrasonic sensor

  if (distance < 10) {  // If there is a vehicle in less than 10cm
    numberOfSlot = 0;
  } else {
    numberOfSlot = 1;
  }

  lcd.setCursor(0, 0);
  lcd.print("There is: " + String(numberOfSlot) + " slots");  // Display the number of available slots on the screen
  if (Serial.available() > 0) {                               // Read from the serial line
    String a = Serial.readString();
    a.trim();
    if (a == "open") {
      servo1.write(90);  // Open the gate if it receive command "open"
      delay(2000);       // Hold the gate for 2 seconds
      servo1.write(0);   // Close the gate
    }
  }


  if (!mfrc522.PICC_IsNewCardPresent()) {  // If the RFID reader detects a Mifare card
    return;
  }


  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }


  byte nameBuffer[18];
  byte passwordBuffer[18];
  byte customerIDBuffer[18];


  if (readData(NAME_BLOCK, nameBuffer) && readData(PASSWORD_BLOCK, passwordBuffer) && readData(CUSTOMERID_BLOCK, customerIDBuffer)) {  // Read Customer name, Customer ID, and password
    String name;
    for (uint8_t i = 0; i < 16; i++) {  // Convert data into string
      name += char(nameBuffer[i]);
    }
    name.trim();

    String customerID;
    for (uint8_t i = 0; i < 16; i++) {
      customerID += char(customerIDBuffer[i]);
    }

    customerID.trim();

    String password;
    for (uint8_t i = 0; i < 16; i++) {

      password += char(passwordBuffer[i]);
    }
    password.trim();

    // Serializing the data into JSON format
    doc["password"] = password;
    doc["name"] = name;
    doc["customerID"] = customerID;
    serializeJson(doc, Serial);  // Send the data to Serial line
    Serial.println();
  }


  mfrc522.PICC_HaltA();  // Stop reading the card
  mfrc522.PCD_StopCrypto1();
}