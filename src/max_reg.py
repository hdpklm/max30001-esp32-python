from config import *
from machine import Pin, SPI

MAX_STATUS		= 0x01
MAX_EN_INT		= 0x02
MAX_EN_INT1		= 0x03
MAX_MNGR_INT	= 0x04
MAX_MNGR_DYN	= 0x05
MAX_SW_RST		= 0x08
MAX_SYNCH		= 0x09
MAX_FIFO_RST	= 0x0A
MAX_INFO		= 0x0F
MAX_CNFG_GEN	= 0x10
MAX_CNFG_CAL	= 0x12
MAX_CNFG_EMUX	= 0x14
MAX_CNFG_ECG	= 0x15
MAX_CNFG_BMUX	= 0x17
MAX_CNFG_BIOZ	= 0x18
MAX_CNFG_PACE	= 0x1A
MAX_CNFG_RTOR1	= 0x1D
MAX_CNFG_RTOR2	= 0x1E

class maxreg:
	def __init__(self, cs=PIN_SPI_CS, clk=PIN_SPI_CLK, mosi=PIN_SPI_MOSI, miso=PIN_SPI_MISO, freq=2000000):
		self.pin_cs = cs
		self.pin_clk = clk
		self.pin_mosi = mosi
		self.pin_miso = miso
		self.freq = freq
		
		self.spi = SPI(1, baudrate=self.freq, polarity=0, phase=0, sck=Pin(self.pin_clk), mosi=Pin(self.pin_mosi), miso=Pin(self.pin_miso))
		self.cs = Pin(self.pin_cs, Pin.OUT)
		self.cs.value(1)

		self.regs = [0 for x in range(0, 0x1F)]

	def read_reg(self, reg, count=3):
		buff = (reg << 1) | 1
		buff = buff.to_bytes(1, 0)

		self.cs.value(0)
		self.spi.write(bytearray(buff))
		data = list(self.spi.read(count))
		if reg < 0x20:
			self.regs[reg] = data
		self.cs.value(1)

		return data

	def write_reg(self, reg, data):
		if reg >= 0x20:
			return

		self.regs[reg] = data.to_bytes(3, 0)
		buff = bytearray([(reg << 1) | 0])
		buff.extend(self.regs[reg])

		self.cs.value(0)
		self.spi.write(bytearray(buff))
		self.cs.value(1)

	def write_reg_mask(self, reg, pos, mask, data):
		if reg >= 0x20:
			return

		mask = (mask << pos) & 0xFFFFFF
		self.regs[reg] &= ~mask
		self.regs[reg] |= ((data << pos) & mask) & 0xFFFFFF
		buff = bytearray([(reg << 1) | 0])
		buff.extend(self.regs[reg])

		self.cs.value(0)
		self.spi.write(bytearray(buff))
		self.cs.value(1)

	def status(self):
		return self.read_reg(MAX_STATUS)

	def en_int(self, value=None):
		if value is not None:
			self.write_reg(MAX_EN_INT, value)
		return self.read_reg(MAX_EN_INT)
	
	def en_int1(self, value=None):
		if value is not None:
			self.write_reg(MAX_EN_INT1, value)
		return self.read_reg(MAX_EN_INT1)
	
	def mngr_int(self, value=None):
		if value is not None:
			self.write_reg(MAX_MNGR_INT, value)
		return self.read_reg(MAX_MNGR_INT)
	
	def mngr_dyn(self, value=None):
		if value is not None:
			self.write_reg(MAX_MNGR_DYN, value)
		return self.read_reg(MAX_MNGR_DYN)
	
	def sw_rst(self):
		self.write_reg(MAX_MNGR_DYN, 0)

	def synch(self):
		self.write_reg(MAX_SYNCH, 0)

	def fifo_rst(self):
		self.write_reg(MAX_FIFO_RST, 0)

	def info(self):
		return self.read_reg(MAX_INFO)
	
	def cnfg_gen(self, value=None):
		if value is not None:
			self.write_reg(MAX_CNFG_GEN, value)
		return self.read_reg(MAX_CNFG_GEN)
	
	def cnfg_cal(self, value=None):
		if value is not None:
			self.write_reg(MAX_CNFG_CAL, value)
		return self.read_reg(MAX_CNFG_CAL)
	
	def cnfg_emux(self, value=None):
		if value is not None:
			self.write_reg(MAX_CNFG_EMUX, value)
		return self.read_reg(MAX_CNFG_EMUX)
	
	def cnfg_ecg(self, value=None):
		if value is not None:
			self.write_reg(MAX_CNFG_ECG, value)
		return self.read_reg(MAX_CNFG_ECG)
	
	def cnfg_bmux(self, value=None):
		if value is not None:
			self.write_reg(MAX_CNFG_BMUX, value)
		return self.read_reg(MAX_CNFG_BMUX)
	
	def cnfg_bioz(self, value=None):
		if value is not None:
			self.write_reg(MAX_CNFG_BIOZ, value)
		return self.read_reg(MAX_CNFG_BIOZ)
	
	def cnfg_pace(self, value=None):
		if value is not None:
			self.write_reg(MAX_CNFG_PACE, value)
		return self.read_reg(MAX_CNFG_PACE)
	
	def cnfg_rtor1(self, value=None):
		if value is not None:
			self.write_reg(MAX_CNFG_RTOR1, value)
		return self.read_reg(MAX_CNFG_RTOR1)
	
	def cnfg_rtor2(self, value=None):
		if value is not None:
			self.write_reg(MAX_CNFG_RTOR2, value)
		return self.read_reg(MAX_CNFG_RTOR2)
	
reg = maxreg()
