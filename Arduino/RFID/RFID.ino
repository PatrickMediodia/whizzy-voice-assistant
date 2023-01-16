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
bool logged_in = false;
String current_ID = "";

void setup() {
  Serial.begin(9600);

  //initialize RFID reader
  SPI.begin();
  mfrc522.PCD_Init();
}

void loop() {
  //if logged in, check for logout message from raspi
  if (logged_in && Serial.available() > 0) {
    //get message and check if message is "Logout"
    response = Serial.readStringUntil('\n'); 
    if (response == "Logout") {
      show_LED_none();
      current_ID = "";
      logged_in = false;
    }
  } else {
    if(getID()) {  
      //send to raspi through serial
      Serial.println(tagID);

      //wait for response from raspi
      //do nothing while waiting
      while(Serial.available() <= 0) {}

      //get response if available
      if (Serial.available() > 0) {
        response = Serial.readStringUntil('\n');
        response.trim();

        //show output (light, buzzer, servo)
        if (response == "Granted") {
          show_LED_green();
          delay(2000);
          show_LED_blue();

          current_ID = tagID;
          logged_in = true;

          //stop buzzer and turn light to blue after 2 seconds 
          /*
          tone(BUZZER, 262, 500);  
          show_LED_blue();
          */
        } else if (response == "Denied") {
          show_LED_red();

          //tone(BUZZER, 523, 500);
        }
      }
    }
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