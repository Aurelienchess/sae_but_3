from SX127x.LoRa import *
from SX127x.board_config import BOARD
import time

BOARD.setup()

class LoRaNode(LoRa):
    def __init__(self):
        super(LoRaNode, self).__init__(do_calibration=False)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0,0,0,0,0,0])
        self.received = None

    # Cette fonction est appelée automatiquement à la réception

    def on_rx_done(self):

        self.clear_irq_flags(RxDone=1)
        payload = bytes(self.read_payload(nocheck=True)).decode("utf-8","ignore")
        self.received = payload
        print("📥 MESSAGE REÇU :", payload)
        print("RSSI :", self.get_pkt_rssi_value())
        print("SNR  :", self.get_pkt_snr_value())
        print("-----------------------------")
        self.set_mode(MODE.RXCONT)  # repasser en réception continue

lora = LoRaNode()
lora.set_freq(868)
lora.set_spreading_factor(7)
lora.set_bw(7)
lora.set_rx_crc(True)

try:
    while True:
        # --- Émission ---
        msg = "Hello depuis la même carte"
        lora.write_payload([ord(c) for c in msg])
        lora.set_mode(MODE.TX)
        while lora.get_mode() == MODE.TX:
            time.sleep(0.01)
        print("📡 Message envoyé :", msg)

        # --- Réception ---
        lora.received = None
        lora.set_mode(MODE.RXCONT)
        print("⏳ En attente de réception...")
        start = time.time()
        timeout = 5  # secondes
        while (lora.received is None) and (time.time() - start < timeout):

            time.sleep(0.1)
        if lora.received is None:
            print("⚠️ Pas de message reçu pendant le délai")
        else:
            print("✅ Réception OK :", lora.received)
        time.sleep(2)

except KeyboardInterrupt:
    BOARD.teardown()
    print("🔴 Arrêt du module")


