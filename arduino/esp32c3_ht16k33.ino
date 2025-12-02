#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_LEDBackpack.h>
#include <WiFi.h>
#include <WiFiUdp.h>

// --- Hardware Configuration ---
// ESP32-C3 SuperMini I2C Pins
#define SDA_PIN 8
#define SCL_PIN 9
#define UDP_PORT 4210

// Matrices
// Matrix 0 (Left)
// Matrix 1 (Middle)
// Matrix 2 (Right)
Adafruit_8x8matrix matrix0 = Adafruit_8x8matrix(); 
Adafruit_8x8matrix matrix1 = Adafruit_8x8matrix(); 
Adafruit_8x8matrix matrix2 = Adafruit_8x8matrix(); 

// --- Font Definition ---
const char allowedChars[] = " -MAXT0123456789o";
const uint8_t font5x7[][7] = {
  { B00000, B00000, B00000, B00000, B00000, B00000, B00000 }, // ' '
  { B00000, B00000, B00000, B11111, B00000, B00000, B00000 }, // '-'
  { B10001, B11011, B10101, B10001, B10001, B10001, B10001 }, // 'M'
  { B01110, B10001, B10001, B11111, B10001, B10001, B10001 }, // 'A'
  { B10001, B01010, B00100, B00100, B01010, B10001, B00000 }, // 'X'
  { B11111, B00100, B00100, B00100, B00100, B00100, B00000 }, // 'T'
  { B01110, B10001, B10011, B10101, B11001, B10001, B01110 }, // '0'
  { B00100, B01100, B00100, B00100, B00100, B00100, B01110 }, // '1'
  { B01110, B10001, B00001, B00010, B00100, B01000, B11111 }, // '2'
  { B01110, B10001, B00001, B00110, B00001, B10001, B01110 }, // '3'
  { B00010, B00110, B01010, B10010, B11111, B00010, B00010 }, // '4'
  { B11111, B10000, B11110, B00001, B00001, B10001, B01110 }, // '5'
  { B00110, B01000, B10000, B11110, B10001, B10001, B01110 }, // '6'
  { B11111, B00001, B00010, B00100, B01000, B01000, B01000 }, // '7'
  { B01110, B10001, B10001, B01110, B10001, B10001, B01110 }, // '8'
  { B01110, B10001, B10001, B01111, B00001, B00010, B01100 }, // '9'
  { B00000, B01110, B10001, B10001, B10001, B01110, B00000 }  // 'o'
};

// --- Network Globals ---
WiFiUDP udp;
char packetBuffer[255]; 
bool wifiConnected = false;
IPAddress remoteIp;   // Last known sender IP
uint16_t remotePort;  // Last known sender Port

void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN); 

  // Initialize Matrices (0x70=Left, 0x72=Mid, 0x71=Right)
  matrix0.begin(0x70); matrix0.setRotation(1); matrix0.setBrightness(7);
  matrix1.begin(0x72); matrix1.setRotation(1); matrix1.setBrightness(7);
  matrix2.begin(0x71); matrix2.setRotation(1); matrix2.setBrightness(7);

  clearAll();
  Serial.println("READY_SERIAL"); 
}

void loop() {
  // 1. Check Serial Input
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.length() > 0) {
      processIncoming(input, false);
    }
  }

  // 2. Check UDP Input
  if (wifiConnected) {
    int packetSize = udp.parsePacket();
    if (packetSize) {
      // Capture sender details for the return channel
      remoteIp = udp.remoteIP();
      remotePort = udp.remotePort();

      int len = udp.read(packetBuffer, 255);
      if (len > 0) packetBuffer[len] = 0;
      String udpData = String(packetBuffer);
      
      processIncoming(udpData, true);
    }
  }
}

// --- Core Logic ---
void processIncoming(String input, bool isUdp) {
  // 1. Check for Commands (Start with '!')
  if (input.startsWith("!")) {
    handleCommand(input.substring(1));
    return;
  }

  // 2. Filter Text (Remove unwanted characters)
  String cleanText = "";
  for (int i = 0; i < input.length(); i++) {
    char c = input.charAt(i);
    // Scan allowedChars array
    for (int j = 0; j < sizeof(allowedChars) - 1; j++) {
      if (allowedChars[j] == c) {
        cleanText += c;
        break;
      }
    }
  }

  // 3. Logic: Centering
  // If input is exactly "o" or "0", pad it to center on the middle matrix
  if (cleanText == "o" || cleanText == "0") {
    cleanText = " " + cleanText + " ";
  }

  // 4. Logic: Truncate to Max 3 Chars
  if (cleanText.length() > 3) {
    cleanText = cleanText.substring(0, 3);
  }

  // 5. Logic: Reverse String
  // (e.g. "123" becomes "321")
  String processedText = "";
  for (int i = cleanText.length() - 1; i >= 0; i--) {
    processedText += cleanText.charAt(i);
  }

  // 6. Update Display
  if (processedText.length() > 0) {
    updateDisplay(processedText);
  }
}

void handleCommand(String cmd) {
  if (cmd.startsWith("SETUP:WIFI:")) {
    // Format: !SETUP:WIFI:SSID:PASS
    String credentials = cmd.substring(11); 
    int splitIndex = credentials.indexOf(':');
    if (splitIndex == -1) return;

    String ssid = credentials.substring(0, splitIndex);
    String pass = credentials.substring(splitIndex + 1);

    Serial.print("Connecting to "); Serial.println(ssid);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid.c_str(), pass.c_str());

    // Timeout logic
    int retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 20) {
      delay(500); retries++;
    }

    if (WiFi.status() == WL_CONNECTED) {
      wifiConnected = true;
      udp.begin(UDP_PORT); 
      Serial.print("SUCCESS:"); Serial.println(WiFi.localIP()); 
    } else {
      Serial.println("ERROR:CONNECTION_FAILED");
    }
  } 
  else if (cmd.startsWith("DISABLE:WIFI")) {
    WiFi.disconnect();
    wifiConnected = false;
    Serial.println("WIFI_DISABLED");
  }
  else if (cmd.startsWith("SETUP:WIRED:")) {
    // Just an acknowledgement
    Serial.println("MODE:WIRED");
  }
}

// --- Return Channel ---
// Call this function to send data back to the Python app
void sendDataBack(String data) {
  if (wifiConnected && remotePort != 0) {
    // Send via UDP to the last known sender
    udp.beginPacket(remoteIp, remotePort);
    udp.print(data);
    udp.endPacket();
  } else {
    // Fallback to Serial
    Serial.println(data);
  }
}

// --- Display Helpers ---
void updateDisplay(String text) {
  clearAll();
  int len = text.length();
  
  for (int i = 0; i < len; i++) {
    char c = text.charAt(i);
    // Standard mapping: 0=Left, 1=Mid, 2=Right
    switch(i) {
      case 0: displayChar(matrix0, c); break; 
      case 1: displayChar(matrix1, c); break; 
      case 2: displayChar(matrix2, c); break; 
    }
  }
}

void displayChar(Adafruit_8x8matrix &matrix, char c) {
  int8_t index = -1;
  for (uint8_t i = 0; i < sizeof(allowedChars) - 1; i++) {
    if (allowedChars[i] == c) { index = i; break; }
  }

  if (index < 0) { matrix.writeDisplay(); return; }

  matrix.clear();
  // Vertical Flip Logic
  for (uint8_t row = 0; row < 7; row++) {
    uint8_t rowData = font5x7[index][6 - row]; 
    for (uint8_t col = 0; col < 5; col++) {
      if (rowData & (1 << (4 - col))) {
        matrix.drawPixel(col, row, LED_ON);
      }
    }
  }
  matrix.writeDisplay();
}

void clearAll() {
  matrix0.clear(); matrix0.writeDisplay();
  matrix1.clear(); matrix1.writeDisplay();
  matrix2.clear(); matrix2.writeDisplay();
}
