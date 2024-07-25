

import os
import gc
import time
# import sys
# import json
# import math
from machine import Timer, reset, freq, reset

from config import *
from max import mx

freq(80000000)


class Struct:
	pass


def boot():
	os.remove('/boot.py')

def reg_hex(reg, padding=3):
	reg = bytearray(reg)
	pad = padding - len(reg)
	if pad > 0:
		reg = bytearray([0] * pad) + reg
	msg = '0x' + "".join(["{:02X}".format(x) for x in reg])
	return msg

def init_max():
	mx.reset()
	mx.reg.en_int(0x000003)
	mx.reg.en_int1(0x000003)
	mx.reg.mngr_int(0x7F0014)
	mx.reg.mngr_dyn(0x3FFFFF)
	mx.reg.cnfg_gen(0x000017)	# 0x0C0017
	mx.reg.cnfg_cal(0x004800)
	mx.reg.cnfg_emux(0x000000)
	mx.reg.cnfg_ecg(0x805000)
	mx.reg.cnfg_bmux(0x001040)
	mx.reg.cnfg_bioz(0x201130)
	mx.reg.cnfg_pace(0x000055)
	mx.reg.cnfg_rtor1(0x3FA300)
	mx.reg.cnfg_rtor2(0x202400)
	# mx.reg.cnfg_gen(0x0C0017)

	print("MAX30009 > Initialized")
	print("MAX30009 > status: " + str(reg_hex(mx.reg.status())))
	print("MAX30009 > info: " + str(reg_hex(mx.reg.info())))
	print("MAX30009 > cnfg_gen: " + str(reg_hex(mx.reg.cnfg_gen())))
	print("MAX30009 > cnfg_cal: " + str(reg_hex(mx.reg.cnfg_cal())))
	print("MAX30009 > cnfg_emux: " + str(reg_hex(mx.reg.cnfg_emux())))
	print("MAX30009 > cnfg_ecg: " + str(reg_hex(mx.reg.cnfg_ecg())))
	print("MAX30009 > cnfg_bmux: " + str(reg_hex(mx.reg.cnfg_bmux())))
	print("MAX30009 > cnfg_bioz: " + str(reg_hex(mx.reg.cnfg_bioz())))
	print("MAX30009 > cnfg_pace: " + str(reg_hex(mx.reg.cnfg_pace())))
	print("MAX30009 > cnfg_rtor1: " + str(reg_hex(mx.reg.cnfg_rtor1())))
	print("MAX30009 > cnfg_rtor2: " + str(reg_hex(mx.reg.cnfg_rtor2())))
	print("MAX30009 > en_int: " + str(reg_hex(mx.reg.en_int())))
	print("MAX30009 > en_int1: " + str(reg_hex(mx.reg.en_int1())))
	print("MAX30009 > mngr_int: " + str(reg_hex(mx.reg.mngr_int())))
	print("MAX30009 > mngr_dyn: " + str(reg_hex(mx.reg.mngr_dyn())))



def stop():
	mx.abort()

def scan_ecg():
	mx.on()
	time.sleep(0.1)

	mx.reg.cnfg_gen(0x080017)
	mx.reg.fifo_rst()
	time.sleep(0.1)

	while True:
		time.sleep(0.001)
		if mx.ecg_update() == False:
			continue

		# print("\n".join([str(x) for x in mx.ecg_arr]))
		arr = [mx.ecg_volt(x) for x in mx.ecg_arr]
		arr = [str(x) for x in arr]
		print("\n".join(arr))

def scan_bioz():
	mx.on()
	time.sleep(0.1)

	mx.reg.cnfg_gen(0x040017)
	mx.reg.fifo_rst()
	time.sleep(0.1)

	while True:
		time.sleep(0.003)
		state = mx.reg.status()
		if (state[0] & 0x08) == 0:
			continue
		
		reads = mx.reg.read_reg(0x04, 1)
		count = (reads[0] & 0x07) + 1
		data = mx.reg.read_reg(0x22, 3 * count)
		arr = [mx.conv_bioz(data[i:i+3]) for i in range(0, len(data), 3)]
		arr = [str(x) for x in arr]
		print("\n".join(arr))


gc.collect()
# tim = Timer(-1)
# tim.init(period=1, mode=Timer.PERIODIC, callback=timer_update)

# mx.off()

# init_max(); scan_ecg()