#include <MD_MAX72xx.h>
#include <SPI.h>
#include <Wire.h>
#include <RTClib.h>

#define PRINT(s, v) { Serial.print(F(s)); Serial.print(v); }

#define POT_PIN A0
#define MODE_PIN A1

// Define the number of devices we have in the chain and the hardware interface
#define HARDWARE_TYPE MD_MAX72XX::FC16_HW 
#define MAX_DEVICES 4

#define CLK_PIN   13  // or SCK
#define DATA_PIN  11  // or MOSI
#define CS_PIN    10  // or SS

// SPI hardware interface
MD_MAX72XX mx = MD_MAX72XX(HARDWARE_TYPE, CS_PIN, MAX_DEVICES);

// RTC
RTC_DS3231 rtc;

// Text parameters
#define CHAR_SPACING  1 // pixels between characters

// Global message buffers shared by Serial and Scrolling functions
#define BUF_SIZE  75
char message[BUF_SIZE] = "";
bool newMessageAvailable = true;

void readSerial(void)
{
  static uint8_t putIndex = 0;

  while (Serial.available())
  {
    message[putIndex] = (char)Serial.read();
    if ((message[putIndex] == '\n') || (putIndex >= BUF_SIZE - 3))  // end of message character or full buffer
    {
      message[putIndex] = '\0';
      putIndex = 0;
      newMessageAvailable = true;
    }
    else
      putIndex++;
  }
}

void printText(uint8_t modStart, uint8_t modEnd, char *pMsg)
{
  uint8_t   state = 0;
  uint8_t   curLen;
  uint16_t  showLen;
  uint8_t   cBuf[8];
  int16_t   col = ((modEnd + 1) * COL_SIZE) - 1;

  mx.control(modStart, modEnd, MD_MAX72XX::UPDATE, MD_MAX72XX::OFF);

  do
  {
    switch(state)
    {
      case 0: // Load the next character from the font table
        if (*pMsg == '\0')
        {
          showLen = col - (modEnd * COL_SIZE);  // padding characters
          state = 2;
          break;
        }
        showLen = mx.getChar(*pMsg++, sizeof(cBuf)/sizeof(cBuf[0]), cBuf);
        curLen = 0;
        state++;
        // fall through to next state to start displaying

      case 1: // display the next part of the character
        mx.setColumn(col--, cBuf[curLen++]);

        if (curLen == showLen)
        {
          showLen = CHAR_SPACING;
          state = 2;
        }
        break;

      case 2: // initialize state for displaying empty columns
        curLen = 0;
        state++;
        // fall through

      case 3:  // display inter-character spacing or end of message padding (blank columns)
        mx.setColumn(col--, 0);
        curLen++;
        if (curLen == showLen)
          state = 0;
        break;

      default:
        col = -1;  // this ends the do loop
    }
  } while (col >= (modStart * COL_SIZE));

  mx.control(modStart, modEnd, MD_MAX72XX::UPDATE, MD_MAX72XX::ON);
}

void setup()
{
  mx.begin();
  pinMode(MODE_PIN, INPUT);
  pinMode(POT_PIN, INPUT);
  Serial.begin(57600);
  Serial.print("\n[MD_MAX72XX Message Display]\nType a message for the display\nEnd message line with a newline");

  // Initialize RTC
  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }

  if (rtc.lostPower()) {
    Serial.println("RTC lost power, setting the time");
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));  // Set RTC to compile time
  }
}

void loop()
{
  int potValue = analogRead(POT_PIN);  // Read raw value (0-1023)
  int mappedValue = map(potValue, 0, 1023, 0, 15);  // Scale to 0-15 (for LED)
  mx.control(MD_MAX72XX::INTENSITY, mappedValue); // Set brightness based on potentiometer value

  if (digitalRead(MODE_PIN) == LOW)
  {
    // Show message from Serial Monitor
    readSerial();
    if (newMessageAvailable)
    {
      PRINT("\nProcessing new message: ", message);
      printText(0, MAX_DEVICES - 1, message);
      newMessageAvailable = false;
    }
  }
  else
  {
    // Fetch current time from RTC
    DateTime now = rtc.now();
    
    // Sync time: Adjust time accuracy by checking the current time before displaying it
    static uint32_t lastMillis = 0;
    uint32_t currentMillis = millis();
    
    if (currentMillis - lastMillis >= 1000) // Update every second without delay drift
    {
      lastMillis = currentMillis;
      
      // Format time as HH:MM (no seconds)
      char timeString[6];
      snprintf(timeString, sizeof(timeString), "%02d:%02d", now.hour(), now.minute());
      
      // Print time on the LED matrix display
      printText(0, MAX_DEVICES - 1, timeString);
    }
  }
}
