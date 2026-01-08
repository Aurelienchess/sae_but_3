import serial
import time
import json
import paho.mqtt.client as mqtt

#  CONFIGURATION A MODIFIER 
# Le port USB de la carte qui réceptionne les données
# Windows : "COM3", "COM4", "COM5"...
# Linux : "/dev/tty.usb...", "/dev/ttyACM0"
SERIAL_PORT = "COM6"  

# Vitesse de communication (DOIT être la même que l'autre)
BAUD_RATE = 115200

# Adresse IP(Broker MQTT)
MQTT_BROKER = "172.17.176.203" 
MQTT_TOPIC = "iot/mesures"

# CONNEXION MQTT 
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connecté au serveur MQTT ({MQTT_BROKER})")
    else:
        print(f"Erreur de connexion MQTT (Code: {rc})")

client.on_connect = on_connect

print("--- DEMARRAGE PASSERELLE LORA -> MQTT ---")

# Connexion au Broker
try:
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_start() # Lance le process MQTT en arrière-plan
except Exception as e:
    print(f"Impossible de joindre le Raspberry Pi à {MQTT_BROKER}")
    print(f"Erreur : {e}")
    exit()

# Ouverture du Port Série (USB)
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Écoute du port {SERIAL_PORT} à {BAUD_RATE} bauds...")
    ser.reset_input_buffer()
except Exception as e:
    print(f"Impossible d'ouvrir le port série {SERIAL_PORT}")
    print("Vérifie qu'il est bon et que le Moniteur Série Arduino est bien FERMÉ.")
    print(f"Erreur : {e}")
    exit()

# Boucle principale
while True:
    if ser.in_waiting > 0:
        try:
            # Lire une ligne depuis l'USB
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            
            # On cherche les accolades du JSON
            if "{" in line and "}" in line:
                start = line.find("{")
                end = line.rfind("}") + 1
                json_str = line[start:end]
                
                # Vérifier si c'est du JSON valide
                try:
                    data = json.loads(json_str)
                    
                    # On envoie à MQTT
                    client.publish(MQTT_TOPIC, json_str)
                    print(f"Envoyé MQTT : {json_str}")
                    
                except json.JSONDecodeError:
                    pass
            elif line:
                # Afficher les autres messages (Debug, RSSI...)
                print(f"Arduino : {line}")
                
        except Exception as e:
            print(f"Erreur lecture : {e}")
            
    time.sleep(0.01) 