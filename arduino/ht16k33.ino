// 3 HT16K33, 5*7 common cathode led matrix
#include <Wire.h>
#include <Adafruit_LEDBackpack.h>

// Matrices with correct addresses
Adafruit_8x8matrix matrix0 = Adafruit_8x8matrix(); // 0x71
Adafruit_8x8matrix matrix1 = Adafruit_8x8matrix(); // 0x72
Adafruit_8x8matrix matrix2 = Adafruit_8x8matrix(); // 0x70

// Font definitions stay the same
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
  { B00000, B01110, B10001, B10001, B10001, B01110, B00000 } // 'o'
};

void setup() {
  Serial.begin(9600);

  matrix0.begin(0x70);
  matrix1.begin(0x72);
  matrix2.begin(0x71);

  matrix0.setRotation(1);
  matrix1.setRotation(1);
  matrix2.setRotation(1);

  clearAll();
  Serial.println("Ready!");
}

void loop() {
  static uint8_t matrixIndex = 0;

  if (Serial.available()) {
    char c = Serial.read();

    clearAll();

    switch (matrixIndex) {
      case 0: displayChar(matrix0, c); break;
      case 1: displayChar(matrix1, c); break;
      case 2: displayChar(matrix2, c); break;
    }

    matrixIndex = (matrixIndex + 1) % 3;
  }
}

void displayChar(Adafruit_8x8matrix &matrix, char c) {
  matrix.clear();

  int8_t index = -1;
  for (uint8_t i = 0; i < sizeof(allowedChars) - 1; i++) {
    if (allowedChars[i] == c) {
      index = i;
      break;
    }
  }

  if (index < 0) {
    matrix.writeDisplay();
    return;
  }

  // Draw flipped (vertically) character
  for (uint8_t row = 0; row < 7; row++) {
    uint8_t rowData = font5x7[index][6 - row];  // ← Flip here
    for (uint8_t col = 0; col < 5; col++) {
      if (rowData & (1 << (4 - col))) {
        matrix.drawPixel(col, row, LED_ON);
      }
    }
  }

  matrix.writeDisplay();
}

void clearAll() {
  matrix0.clear();
  matrix1.clear();
  matrix2.clear();
}
