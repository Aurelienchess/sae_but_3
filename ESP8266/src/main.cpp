#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include "DHT.h"

// CONFIGURATION WIFI 
const char* WIFI_SSID = "LeSmolde";       
const char* WIFI_PASSWORD = "legoat123";    

//  CONFIGURATION SERVEUR RASPBERRY PI 
const char* SERVER_URL = "http://172.17.176.124:5000/data";

//  CONFIGURATION CAPTEURS 
#define DHTPIN D1 
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define MQ_PIN A0 

// ID de l'appareil
String deviceId = "ESP8266_Zone_B"; 

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Init Capteurs
  dht.begin();
  pinMode(MQ_PIN, INPUT);
  Serial.println("\nInitialisation capteurs terminée.");

  // Connexion WiFi 
  Serial.print("Connexion au WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  // On attend la connexion
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connecté !");
  Serial.print("Adresse IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Lecture des capteurs
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  int smokeValue = analogRead(MQ_PIN);

  // Vérification des erreurs de lecture
  if (isnan(h) || isnan(t)) {
    Serial.println("Erreur de lecture du DHT11 !");
    delay(2000);
    return;
  }

  // Affichage Moniteur Série 
  Serial.print("Hum: "); Serial.print(h);
  Serial.print("% | Temp: "); Serial.print(t);
  Serial.print("C | Gaz: "); Serial.println(smokeValue);

  // 2. Vérification de la connexion WiFi
  if (WiFi.status() == WL_CONNECTED) {
    
    WiFiClient client;
    HTTPClient http;

    // Début de la connexion au serveur Flask
    http.begin(client, SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    // Création du JSON 
    String jsonPayload = "{";
    jsonPayload += "\"deviceId\":\"" + deviceId + "\",";
    jsonPayload += "\"temperature\":" + String(t) + ",";
    jsonPayload += "\"humidite\":" + String(h) + ",";
    jsonPayload += "\"gaz\":" + String(smokeValue) + ",";
    jsonPayload += "\"latitude\": 0.0,";
    jsonPayload += "\"longitude\": 0.0";
    jsonPayload += "}";

    Serial.println("Envoi HTTP vers RPI...");
    
    // Envoi de la requête POST
    int httpResponseCode = http.POST(jsonPayload);

    // Gestion de la réponse
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("Code réponse HTTP: ");
      Serial.println(httpResponseCode);
      Serial.print("Réponse du serveur: ");
      Serial.println(response);
    } else {
      Serial.print("Erreur lors de l'envoi HTTP: ");
      Serial.println(httpResponseCode);
    }

    http.end();

  } else {
    Serial.println("Erreur: WiFi déconnecté ! tentative de reconnexion...");
    WiFi.reconnect();
  }

  delay(5000);
}