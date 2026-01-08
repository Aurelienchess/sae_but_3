#include <SPI.h>
#include <LoRa.h>

// --- PINS (UCA Board) ---
#define SS_PIN    10
#define RST_PIN   8
#define DIO0_PIN  3

void setup() {
  // On se met en 115200 comme ton émetteur
  Serial.begin(115200);
  while (!Serial);

  Serial.println("--- RECEPTEUR PRET ---");

  LoRa.setPins(SS_PIN, RST_PIN, DIO0_PIN);

  if (!LoRa.begin(868E6)) {
    Serial.println("Erreur : LoRa non détecté !");
    while (1);
  }

  // Parametres de l'emetteur
  LoRa.setSpreadingFactor(12);
  LoRa.setSignalBandwidth(125E3);
  // Pas de CRC ici car tu ne l'as pas mis dans l'émetteur

  Serial.println("En attente de donnees...");
}

void loop() {
  // Vérifier si un paquet arrive
  int packetSize = LoRa.parsePacket();

  if (packetSize) {
    // Lire le message
    String message = "";
    while (LoRa.available()) {
      message += (char)LoRa.read();
    }

    // Afficher le résultat brut
    Serial.print("Recu : ");
    Serial.println(message);

    // Afficher la puissance du signal (RSSI)
    Serial.print("RSSI : ");
    Serial.println(LoRa.packetRssi());
    Serial.println("--------------------------------");
  }
}