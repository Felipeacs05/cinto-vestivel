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

