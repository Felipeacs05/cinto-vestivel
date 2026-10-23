#include <Wire.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include "MPU9250.h"

// Fornece informações para o processo de geração de token do Firebase
#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

// ==========================================
// 1. CREDENCIAIS DE REDE E FIREBASE (PREENCHA AQUI)
// ==========================================
#define WIFI_SSID "LANE_ZRL2"
#define WIFI_PASSWORD "65679405"

#define API_KEY "AIzaSyCGICFsj_b7tEwknOjU5oOZJE_ujkGBxUA"
#define DATABASE_URL "esp32-inercial-default-rtdb.firebaseio.com" 

// ==========================================
// 2. OBJETOS GLOBAIS
// ==========================================
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

MPU9250 mpu;
int sdaPin = 8;
int sclPin = 9;

// Controle de tempo para envio (Nuvem)
unsigned long sendDataPrevMillis = 0;
unsigned long timerDelay = 5000; // Envia para o Firebase a cada 5000ms (5 segundos)
float ultimoSVM = 0.0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  // --- INICIALIZAÇÃO WI-FI ---
  Serial.println("\n----------------------------------");
  Serial.print("Conectando ao Wi-Fi: ");
  Serial.println(WIFI_SSID);
  
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\nWi-Fi Conectado!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // --- INICIALIZAÇÃO FIREBASE ---
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;

  config.signer.test_mode = true;
  
  // Otimiza o buffer para envios rápidos
  fbdo.setBSSLBufferSize(1024, 1024);
  fbdo.setResponseSize(1024);

  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
  Serial.println("Firebase inicializado.");

  // --- INICIALIZAÇÃO I2C E MPU-9250 ---
  Wire.end(); 
  Wire.begin(sdaPin, sclPin);
  Wire.setTimeOut(3000);
  delay(500);

  byte c = mpu.readByte(MPU9250_ADDRESS_AD0, WHO_AM_I_MPU9250);
  if (c == 0x71 || c == 0x70) {
    Serial.println("MPU-9250 detectado. Calibrando...");
    mpu.calibrateMPU9250(mpu.gyroBias, mpu.accelBias);
    mpu.initMPU9250();
    mpu.getAres();
    Serial.println("Sensor pronto para leitura.");
  } else {
    Serial.println("Erro MPU-9250: Verifique conexoes I2C.");
  }
  Serial.println("----------------------------------");
}

void loop() {
  // 1. LEITURA CONSTANTE DO SENSOR
  if (mpu.readByte(MPU9250_ADDRESS_AD0, INT_STATUS) & 0x01) {
    mpu.readAccelData(mpu.accelCount);
    
    mpu.ax = (float)mpu.accelCount[0] * mpu.aRes;
    mpu.ay = (float)mpu.accelCount[1] * mpu.aRes;
    mpu.az = (float)mpu.accelCount[2] * mpu.aRes;

    // Atualiza a variável global com o cálculo mais recente
    ultimoSVM = sqrt(sq(mpu.ax) + sq(mpu.ay) + sq(mpu.az));
  }
  
  // 2. ROTINA DE ENVIO PERIÓDICO PARA O FIREBASE
  if (Firebase.ready() && (millis() - sendDataPrevMillis > timerDelay || sendDataPrevMillis == 0)) {
    sendDataPrevMillis = millis();

    Serial.print("Enviando SVM para nuvem: ");
    Serial.println(ultimoSVM, 3);

    // Salva o valor no nó "Sensores/Inercial/SVM" do banco de dados
    if (Firebase.RTDB.setFloat(&fbdo, "Sensores/Inercial/SVM", ultimoSVM)) {
      Serial.println("-> Sucesso: Dado salvo no Firebase!");
    } else {
      Serial.print("-> Erro no envio: ");
      Serial.println(fbdo.errorReason());
    }
  }
  
  // Pequeno delay para estabilidade do loop
  delay(50);
}
