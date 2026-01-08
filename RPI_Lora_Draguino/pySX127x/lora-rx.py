from SX127x.LoRa import *
from SX127x.board_config import BOARD
import time

# Configuration des GPIO du Dragino
BOARD.setup()

class LoRaReceiver(LoRa):

    def __init__(self):

        # Désactiver la calibration automatique pour éviter le KeyError
        super(LoRaReceiver, self).__init__(do_calibration=False)
        self.set_mode(MODE.SLEEP)
        # Mapping des DIOs : DIO0 pour RxDone
        self.set_dio_mapping([0,0,0,0,0,0])
    # Fonction appelée automatiquement à la réception
    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)
        payload = bytes(self.read_payload(nocheck=True)).decode("utf-8","ignore")
        print("📥 MESSAGE REÇU :", payload)
        print("RSSI :", self.get_pkt_rssi_value())
        print("SNR  :", self.get_pkt_snr_value())
        print("-----------------------------")
        # Repasser en réception continue
        self.set_mode(MODE.RXCONT)

# Création de l'objet LoRa
lora = LoRaReceiver()
lora.set_freq(868)        # Fréquence Europe 868 MHz
lora.set_spreading_factor(7)
lora.set_bw(7)            # 125 kHz
lora.set_rx_crc(True)
lora.set_mode(MODE.RXCONT)
print("📡 RÉCEPTEUR LORA PRÊT...")

try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    BOARD.teardown()
    print("🔴 Arrêt du récepteur")
