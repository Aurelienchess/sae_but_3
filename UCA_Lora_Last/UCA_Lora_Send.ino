  #include <SPI.h>
  #include <LoRa.h>
  #include "DHT.h"

  //  CONFIGURATION LORA (UCA Board) 
  #define SS_PIN    10
  #define RST_PIN   8
  #define DIO0_PIN  3

  // CONFIGURATION CAPTEURS 
  #define DHTPIN 2        
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
    Serial.println("Initialisation capteur DHT11...");
    pinMode(MQ_PIN, INPUT);

    // Init LoRa 
    Serial.println("Initialisation LoRa...");
    LoRa.setPins(SS_PIN, RST_PIN, DIO0_PIN);
    
    if (!LoRa.begin(868E6)) {
      Serial.println("ERREUR: LoRa n'a pas demarré !");
      Serial.println("Verifie le cablage ou la selection de la carte.");
      while (1); // On bloque ici si pas de LoRa
    }
    
    LoRa.setSpreadingFactor(12);
    LoRa.setSignalBandwidth(125E3);
    LoRa.enableCrc();
    
    Serial.println("LoRa OK ! Pret a envoyer.");
    Serial.println("-------------------------");
  }

  void loop() {
    // Lecture 
    float h = dht.readHumidity();
    float t = dht.readTemperature();
    int smokeValue = analogRead(MQ_PIN);

    // Affichage Serial 
    if (!isnan(h) && !isnan(t)) {
      Serial.print("Humidité: ");
      Serial.print(h);
      Serial.print("%  Température: ");
      Serial.print(t);
      Serial.println("°C");
    } else {
      Serial.println("Erreur de lecture du DHT11");
      delay(2000);
      return; // On arrête la boucle ici si le capteur est HS
    }

    Serial.print("Valeur fumée MQ: ");
    Serial.println(smokeValue);

    if (smokeValue > 600) {
      Serial.println("DANGER : fumée détectée !");
    }

    // --- Envoi LoRa ---
    // On prépare le JSON
    String message = "{";
    message += "\"deviceId\":\"" + deviceId + "\",";
    message += "\"temperature\":" + String(t) + ",";
    message += "\"humidite\":" + String(h) + ",";
    message += "\"gaz\":" + String(smokeValue);
    message += "}";

    Serial.print(">> Envoi LoRa en cours... ");
    
    LoRa.beginPacket();
    LoRa.print(message);
    LoRa.endPacket();
    
    Serial.println("Envoyé !");
    Serial.println("-------------------------");
    
    delay(5000); 
  }