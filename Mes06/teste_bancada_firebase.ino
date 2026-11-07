#include <Wire.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include "MPU9250.h"

// Fornece informações para o processo de geração de token do Firebase
#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

// ==========================================
// 1. CREDENCIAIS DE REDE E FIREBASE
// ==========================================
#define WIFI_SSID "LANE_ZRL2"
#define WIFI_PASSWORD "65679405"

#define API_KEY "AIzaSyCGICFsj_b7tEwknOjU5oOZJE_ujkGBxUA"
#define DATABASE_URL "esp32-inercial-default-rtdb.firebaseio.com" 

// ==========================================
// 2. OBJETOS GLOBAIS E DETECTOR DE PICO / INTEGRADOR
// ==========================================
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

MPU9250 mpu;
int sdaPin = 8;
int sclPin = 9;

// Controle de janela temporal para envio ao Firebase (5000 ms = 5 segundos)
unsigned long sendDataPrevMillis = 0;
unsigned long timerDelay = 5000;

// Variáveis do Detector de Pico Digital (Peak-Hold) e Integrador (Média na Janela)
float ultimoSVM = 0.0;
float picoMaximoSVM = 0.0;
float valeMinimoSVM = 99.0;
float somaIntegradoraSVM = 0.0;
unsigned long contadorAmostras = 0;

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
    Serial.println("Sensor pronto para ensaio de bancada (50 Hz).");
  } else {
    Serial.println("Erro MPU-9250: Verifique conexoes I2C.");
  }
  Serial.println("----------------------------------");
}

void loop() {
  // 1. AMOSTRAGEM RÁPIDA (50 Hz / a cada 20 ms) COM DETECTOR DE PICO E INTEGRADOR
  if (mpu.readByte(MPU9250_ADDRESS_AD0, INT_STATUS) & 0x01) {
    mpu.readAccelData(mpu.accelCount);
    
    mpu.ax = (float)mpu.accelCount[0] * mpu.aRes;
    mpu.ay = (float)mpu.accelCount[1] * mpu.aRes;
    mpu.az = (float)mpu.accelCount[2] * mpu.aRes;

    ultimoSVM = sqrt(sq(mpu.ax) + sq(mpu.ay) + sq(mpu.az));

    // Detector de Pico Digital (Peak-Hold): retém o maior impacto ocorrido na janela
    if (ultimoSVM > picoMaximoSVM) {
      picoMaximoSVM = ultimoSVM;
    }
    // Detector de Vale (Queda Livre): retém o menor valor ocorrido na janela
    if (ultimoSVM < valeMinimoSVM) {
      valeMinimoSVM = ultimoSVM;
    }
    // Acumulador Integrador para cálculo da média da janela
    somaIntegradoraSVM += ultimoSVM;
    contadorAmostras++;
  }
  
  // 2. ROTINA DE ENVIO PERIÓDICO PARA O FIREBASE (Descarrega o Pico Retido e reinicia a janela)
  if (Firebase.ready() && (millis() - sendDataPrevMillis > timerDelay || sendDataPrevMillis == 0)) {
    sendDataPrevMillis = millis();

    float mediaIntegradaSVM = (contadorAmostras > 0) ? (somaIntegradoraSVM / contadorAmostras) : ultimoSVM;
    float picoParaEnvio = (contadorAmostras > 0) ? picoMaximoSVM : ultimoSVM;

    Serial.print("Amostras na janela: ");
    Serial.print(contadorAmostras);
    Serial.print(" | SVM Medio (Integrado): ");
    Serial.print(mediaIntegradaSVM, 3);
    Serial.print(" g | SVM Pico Retido (Peak-Hold): ");
    Serial.print(picoParaEnvio, 3);
    Serial.println(" g");

    // Envia o Pico Máximo retido na janela e a Média Integrada para o Firebase RTDB
    FirebaseJson json;
    json.set("SVM_Instantaneo", ultimoSVM);
    json.set("SVM_Pico_Janela", picoParaEnvio);
    json.set("SVM_Media_Integrada", mediaIntegradaSVM);
    json.set("SVM_Vale_Minimo", (contadorAmostras > 0) ? valeMinimoSVM : ultimoSVM);
    json.set("Amostras_Janela", contadorAmostras);

    if (Firebase.RTDB.setJSON(&fbdo, "Sensores/Inercial", &json)) {
      Serial.println("-> Sucesso: Pico e Media Integrada salvos no Firebase!");
    } else {
      Serial.print("-> Erro no envio: ");
      Serial.println(fbdo.errorReason());
    }

    // Reinicia o Detector de Pico e o Integrador para a próxima janela
    picoMaximoSVM = 0.0;
    valeMinimoSVM = 99.0;
    somaIntegradoraSVM = 0.0;
    contadorAmostras = 0;
  }
  
  // Intervalo de 20 ms (~50 Hz conforme Plano de Trabalho)
  delay(20);
}
