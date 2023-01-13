#include <SPI.h>
#include <MFRC522.h>

//LED pins
#define LED_RED         5
#define LED_GREEN       6
#define LED_BLUE        7

#define BUZZER          8

//RFID pins
#define RST_PIN         9
#define SS_PIN          10

//RFID variables
byte readCard[4];
String masterTag = "";
String tagID = "";

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

//Global variables
bool result = false;
String response;

void setup() {
  Serial.begin(9600);

  //initialize RFID reader
  SPI.begin();
  mfrc522.PCD_Init();
}

void loop() {
  //get tag ID
  while(getID()) {  
    show_LED_none();

    //send to raspi through serial
    Serial.println(tagID);

    //wait for response from raspi
    //do nothing while waiting
    while(!Serial.available() > 0) {}
    
    //get response if available
    if (Serial.available()) {
      response = Serial.readStringUntil('\n');
      response.trim();

      //show output (light, buzzer, servo)
      if (response == "Granted") {
        show_LED_green();
        tone(BUZZER, 262);
      } else if (response == "Denied") {
        show_LED_red();
        tone(BUZZER, 523);
      }
    }

    //stop buzzer and turn light to blue after 2 seconds  
    delay(1000);
    noTone(BUZZER);
    show_LED_blue();

    //wait until raspi sends logout signal
    while(!Serial.available() > 0) {}
  }
}

//function to get ID
boolean getID() {
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return false;
  }

  if (!mfrc522.PICC_ReadCardSerial()) {
    return false;
  }

  tagID = "";
  for (uint8_t i=0; i < 4; i++) {
    tagID.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  tagID.toUpperCase();
  mfrc522.PICC_HaltA();

  return true;
}

//access granted
void show_LED_green() {
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_GREEN, HIGH);
  digitalWrite(LED_BLUE, LOW);
}

//access denied
void show_LED_red() {
  digitalWrite(LED_RED, HIGH);
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_BLUE, LOW);
}

//currently in use
void show_LED_blue() {
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_BLUE, HIGH);
}

//ready to take input
void show_LED_none() {
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_BLUE, LOW);
}