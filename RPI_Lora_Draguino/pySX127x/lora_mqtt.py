from SX127x.LoRa import *
from SX127x.board_config import BOARD
import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime

# ---- CONFIGURATION MQTT ----
MQTT_BROKER = "10.63.96.14" 
MQTT_PORT = 1883
MQTT_TOPIC = "iot/mesures" 

# ---- INIT MQTT ----
client = mqtt.Client()
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    print("✅ Connecté au Broker MQTT")
except Exception as e:
    print(f"❌ Erreur connexion MQTT : {e}")

# ---- CONFIGURATION LORA ----
BOARD.setup()

class LoRaReceiver(LoRa):
    def __init__(self):
        super(LoRaReceiver, self).__init__(do_calibration=False)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0,0,0,0,0,0])

    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)
        try:
            # Lecture du message brut
            payload_bytes = bytes(self.read_payload(nocheck=True))
            payload_str = payload_bytes.decode("utf-8", "ignore")
            
            # Affichage console (Debug)
            rssi = self.get_pkt_rssi_value()
            print(f"📥 REÇU LoRa brut : {payload_str}")
            print(f"   (RSSI: {rssi})")
            
            # On vérifie si c'est du JSON
            if payload_str.startswith("{") and payload_str.endswith("}"):
                try:
                    # On convertit le texte en dictionnaire Python
                    data = json.loads(payload_str)
                    
                    # On ajoute l'heure
                    now = datetime.now()
                    data["date"] = now.strftime("%Y-%m-%d")
                    data["heure"] = now.strftime("%H:%M:%S")
                    
                    if "latitude" not in data:
                        data["latitude"] = 43.61 
                        data["longitude"] = 7.07

                    # On reconvertit en JSON pour l'envoyer
                    final_payload = json.dumps(data)
                    
                    client.publish(MQTT_TOPIC, final_payload)
                    print(f"🚀 Transmis MQTT : {final_payload}")
                    
                except json.JSONDecodeError:
                    print("⚠️ Erreur : JSON malformé")
            else:
                print("⚠️ Ignoré (Format invalide)")

        except Exception as e:
            print(f"Erreur de traitement : {e}")

        print("-----------------------------")
        self.set_mode(MODE.RXCONT)

# ---- LANCEMENT ----
lora = LoRaReceiver()
lora.set_freq(868)
lora.set_spreading_factor(7)
lora.set_bw(7)
lora.set_rx_crc(True)
lora.set_mode(MODE.RXCONT)

print("📡 PASSERELLE LORA -> MQTT (Avec formatage) DÉMARRÉE...")

try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    BOARD.teardown()
    print("🔴 Arrêt du récepteur")
