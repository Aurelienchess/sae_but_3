from SX127x.LoRa import *
from SX127x.board_config import BOARD

BOARD.setup()

class TestTX(LoRa):

    def __init__(self):
        super(TestTX, self).__init__(do_calibration=False)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([1,0,0,0,0,0])

lora = TestTX()
lora.set_freq(868)
lora.set_pa_config(pa_select=1)
lora.set_spreading_factor(7)
lora.set_bw(7)
lora.set_coding_rate(1)
lora.set_sync_word(0x34)
print("📡 Envoi en cours...")
payload = "TEST DRAGINO OK"
lora.write_payload(list(payload.encode()))

while lora.get_mode() == MODE.TX:
    pass

print("✅ Transmission terminée (TX DONE détecté)")

BOARD.teardown()


