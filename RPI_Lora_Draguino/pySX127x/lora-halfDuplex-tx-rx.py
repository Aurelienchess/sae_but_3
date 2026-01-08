from SX127x.LoRa import *
from SX127x.board_config import BOARD
import time

BOARD.setup()

class LoRaNode(LoRa):
    def __init__(self):
        super(LoRaNode, self).__init__(do_calibration=False)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0,0,0,0,0,0])

     
lora = LoRaNode()
lora.set_freq(868)
lora.set_spreading_factor(7)
lora.set_bw(7)
lora.set_rx_crc(True)

try:
    while True:
        # --- Émission ---
        msg = "Salut depuis la même carte"
        lora.write_payload([ord(c) for c in msg])
        lora.set_mode(MODE.TX)
        while lora.get_mode() == MODE.TX:
            time.sleep(0.01)
        print("📡 Message envoyé :", msg)

        # --- Réception ---
        lora.set_mode(MODE.RXCONT)
        print("⏳ En attente de réponse...")
        start = time.time()
        timeout = 10  # secondes
        while time.time() - start < timeout:
            # on attend la réception via l'interruption on_rx_done
            time.sleep(0.1)
except KeyboardInterrupt:
    BOARD.teardown()


