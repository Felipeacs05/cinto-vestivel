#include <Wire.h>
#include "MPU9250.h"

MPU9250 mpu;

int sdaPin = 8;
int sclPin = 9;

void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println("\n--- INICIANDO MPU-9250 ---");
  Wire.begin(sdaPin, sclPin);
  delay(500);

  // Leitura do ID do sensor
  byte c = mpu.readByte(MPU9250_ADDRESS_AD0, WHO_AM_I_MPU9250);
  Serial.print("Sensor respondeu com ID: 0x");
  Serial.println(c, HEX);

  if (c == 0x71 || c == 0x70) {
    Serial.println("Sensor online e compativel!");
    
    // 1. Calibra o sensor
    Serial.println("Calibrando... Mantenha o sensor parado.");
    mpu.calibrateMPU9250(mpu.gyroBias, mpu.accelBias);

    // 2. Inicializa o sensor
    mpu.initMPU9250();
    Serial.println("Sensor inicializado com sucesso.");

    // 3. Define a resolucao/escala
    mpu.getAres();

  } else {
    Serial.println("Erro: Nao foi possivel comunicar com o MPU-9250.");
    Serial.println("Verifique as conexoes dos pinos VCC (3.3V), GND, SDA (GPIO 8) e SCL (GPIO 9).");
    while (1) { delay(100); }
  }
}

void loop() {
  if (mpu.readByte(MPU9250_ADDRESS_AD0, INT_STATUS) & 0x01) {
    mpu.readAccelData(mpu.accelCount);
    
    mpu.ax = (float)mpu.accelCount[0] * mpu.aRes;
    mpu.ay = (float)mpu.accelCount[1] * mpu.aRes;
    mpu.az = (float)mpu.accelCount[2] * mpu.aRes;

    // Cálculo do SVM (Signal Vector Magnitude)
    float svm = sqrt(sq(mpu.ax) + sq(mpu.ay) + sq(mpu.az));

    // Exibe o valor do SVM no Monitor Serial
    Serial.print("SVM: ");
    Serial.println(svm, 3);
  }
  
  delay(100);
}
