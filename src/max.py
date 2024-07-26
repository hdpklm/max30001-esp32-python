
import gc
import time
import math
import machine
from config import *
from max_reg import reg, Pin

def send_cmd(str):
	print(str+"\n")

# https://www.analog.com/media/en/technical-documentation/data-sheets/max30001.pdf
# read fifo page 65 

class Max:
	VREF = 1.0			# fixed by hardware

	# reg: 0x15(CNFG_ECG)
	# page: 53
	# bits: [17:16]
	# default: 0x00
	# values: 0x00(20V/V), 0x01(40V/V), 0x02(80V/V), 0x03(160V/V)
	ECG_GAIN = 0
	ECG_GAIN_ARR = [20, 40, 80, 160]
	ECG_GAIN_VAL = ECG_GAIN_ARR[ECG_GAIN]
	ecg_arr = []

	# reg: 0x18(CNFG_BIOZ)
	# page: 57
	# bits: [17:16]
	# default: 0x00
	# values: 0x00(10V/V), 0x01(20V/V), 0x02(40V/V), 0x03(80V/V)
	BIOZ_GAIN = 0
	BIOZ_GAIN_ARR = [10, 20, 40, 80]
	BIOZ_GAIN_VAL = BIOZ_GAIN_ARR[BIOZ_GAIN]
	bioz_arr = []

	# reg: 0x18(CNFG_BIOZ)
	# page: 58
	# bits: [6:4]
	# default: 0x00
	# values: 0x00(off), 0x01(8μA), 0x02(16μA), 0x03(32μA), 0x04(48μA), 0x05(64μA), 0x06(80μA), 0x07(96μA)
	BIOZ_CGMAG = 0x03
	BIOZ_CGMAG_ARR = [0, 8, 16, 32, 48, 64, 80, 96]
	BIOZ_CGMAG_VAL = BIOZ_CGMAG_ARR[BIOZ_CGMAG] * 10**-6

	def __init__(self):
		self.pwr = Pin(PIN_MAX_PWR, Pin.OUT)
		self.pwr.on()

		self._sleep = False
		self.reg = reg

		self.reset()

	def on(self):
		self.pwr.on()

	def off(self):
		self.pwr.off()

	def reset(self):
		try:
			self.reg.sw_rst()
			self.reg.synch()
			self.reg.fifo_rst()
			time.sleep(0.1)

		except Exception as e:
			send_cmd("MAX30009 > reset: " + str(e))

	def freq(self, _freq):
		self._freq = int(_freq)

	def state_update(self):
		state = reg.status()
		# 0x40: ECG FIFO Overrun
		# 0x04: BIOZ FIFO Overrun
		if (state[0] & 0x44) != 0:
			reg.fifo_rst()
			return False
		
		if (state[0] & 0x80) != 0:
			self.ecg_update()
		
		if (state[0] & 0x08) != 0:
			self.bioz_update()

		return True

	def conv_bioz(self, data):
		# page 67
		adc = ((data[0] << 16) | (data[1] << 8) | data[2]) >> 3
		volt = (adc * self.VREF) / (2**19 * self.BIOZ_CGMAG_VAL * self.BIOZ_GAIN_VAL)
		return volt

	def bioz_update(self):
		data = reg.read_reg(0x22, 3)
		self.bioz_arr = [self.bioz_value_tag(data)[0]]
		return True

	def bioz_volt(self, adc):
		if adc & 0x080000:
			adc =  adc - 0x100000
		
		volt = (adc * self.VREF) / (2**19 * self.BIOZ_CGMAG_VAL * self.BIOZ_GAIN_VAL)
		return volt

	def bioz_value_tag(self, data):
		# page 67
		tag = data[2] & 0x03
		adc = ((data[0] << 16) | (data[1] << 8) | data[2]) >> 3
		return adc, tag

	def ecg_update(self):
		reads = reg.read_reg(0x04, 1)
		count = ((reads[0] >> 3) & 0x1F) + 1
		data = reg.read_reg(0x20, 3 * count)
		self.ecg_arr = [self.ecg_value_tag(data[i:i+3])[0] for i in range(0, len(data), 3)]
		return True

	def ecg_volt(self, adc):
		if adc & 0x020000:
			adc =  adc - 0x040000
		
		volt = (adc * self.VREF) / (2**17 * self.ECG_GAIN_VAL)
		return volt

	def ecg_value_tag(self, data):
		# page 65
		tag = (data[2] >> 3) & 0x03
		adc = ((data[0] << 16) | (data[1] << 8) | data[2]) >> 6
		return adc, tag

mx = Max()
