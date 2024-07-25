import gc
import time
import math
from NCT75 import Temp
from send import send
from calib import calib
from max import mx
from paciente import paciente
from measure_state import measure_state, MeasureState
from micropython import const


PI2 = math.pi * 2
measure_len = const(256)
measure_steps = const(1)
measure_trigger = const(2250)

gc.collect()


def __print(show):
    if show == -1:      # status
        s0 = mx.reg.read_reg(0x00)
        s1 = mx.reg.read_reg(0x01)
        s = s0 << 8 | s1
        print("Status: 0x%04X" % s)
        return

    if show == 1:     # bioz real, imaginary
        send.cmd("r:%.2f,i:%.2f,index:%d" % (mx.imp_i, mx.imp_q, measure_state.index))
        return

    if show == 2:     # bioz magnitude, angle, basic calibration
        mag = math.sqrt(mx.imp_i * mx.imp_i + mx.imp_q * mx.imp_q)
        ang = math.atan2(mx.imp_q, mx.imp_i)
        mag_c = mag * calib.mag_a + calib.mag_b
        ang_c = ang - calib.ang
        send.cmd("mag:%.2f,ang:%.2f,index:%d,freq_%d" % (mag_c, ang_c, measure_state.index, mx._freq))
        return

    mag, ang = calib.decode(measure_state.index, mx.imp_i, mx.imp_q)
    if show == 0:     # bioz send to machine
        send.cmd("bioz:ep=%d,freq=%d,mag=%.2f,ang=%.2f,r=%.2f,i=%.2f" % (measure_state.epoch, mx._freq, mag, ang, mx.imp_i, mx.imp_q))
        send.keito(send.WITO.READ, [int(mx._freq), mag*10, (PI2+ang) % PI2])
        perc = int(((measure_state.index + 1) * 100 / measure_len) / 10)
        if perc != measure_state.last_perc:
            measure_state.last_perc = perc
            send.cmd("perc:%d" % (perc * 10))
            time.sleep(.1)
            send.keito(send.WITO.PERC, [perc * 10])
        return

    if show == 3:     # bioz magnitude, angle calibrated
        send.cmd("mag:%.2f,ang:%.2f,index:%d" % (mag, ang, measure_state.index))
        return

    if show == 4:     # bioz Resistor, Capacitor
        r = mag * math.cos(ang)
        c = mag * math.sin(ang)
        send.cmd("R:%.2f,C:%.2f,index:%d" % (r, c, measure_state.index))
        return


# """
# from paciente import paciente
# from measures import paciente
# paciente.set_data([37, 1, 70, 170, 80, 36.5, 98])
# paciente.R50K = 300
# paciente.Fat()
# """


class Measure:
    avr = 5
    err = 5
    show = 0
    epoch = 1
    raw_stable = 1
    freq_index = 0
    trigger = 2250
    running = False
    read_error_count = 0

    def __init__(self) -> None:
        pass

    def scan(self, epoch=None, trigger=None, show=None):
        if epoch is not None:
            self.epoch = epoch

        if show is not None:
            self.show = show

        self.trigger = trigger if trigger else int(calib.data['trigger'])

        mx.on()

        # send temperature
        try:
            t = Temp.read_temp()
            send.cmd("temp:%.2f" % t)
            paciente.TempAmb = t
        except Exception as e:
            paciente.TempAmb = 10
            print("Error reading temperature: %s" % e)

        # init & send bioz
        # mx.init()
        measure_state.index = 0
        measure_state.last_perc = 0
        mx.freq(calib.data['freq'][measure_state.index])
        send.cmd("init:1")
        send.keito(send.WITO.PERC, [0])

        measure_state.start()

    def abort(self):
        measure_state.reset()
        self.running = False
        mx.stop()
        mx.off()
        gc.collect()

    def once(self):
        mx.on()

        readed = mx.read(avg=self.avr, stable=self.raw_stable)
        if not readed:
            print("Read error")
            return

        __print(self.show)

    def raw(self, freq_index=None):
        if freq_index is not None:
            self.freq(freq_index)

        mx.on()
        self.freq_index = 127
        self.freq(self.freq_index)
        mx.freq(50000)

        # mx.wait_stable(err_perc=err)
        self.running = True
        measure_state.raw()

    def freq(self, _freq=20):
        global freq_index

        freq_index = _freq
        _freq = calib.data['freq'][freq_index]
        mx.avg_a = calib.data['calib'][freq_index]['a']
        mx.avg_b = calib.data['calib'][freq_index]['b']
        mx.clear()
        mx.freq(_freq)

    def stop(self):
        self.running = False
        mx.off()

    def __measure_freq_raw(self):
        if self.running:
            readed = mx.read(avg=self.avr, stable=self.raw_stable)
            if not readed:
                self.read_error_count += 1
                if self.read_error_count > 100:
                    print("Read error")
                    self.read_error_count = 0
                return

        __print(self.show)

    def __measure_step_adapting(self):
        mx.read()
        mx.read()
        mx.read()
        measure_state.index = 0
        mag, ang = calib.decode(measure_state.index, mx.imp_i, mx.imp_q)

        if mag < self.trigger:
            measure_state.state = MeasureState.Measuring
        else:
            # # send every 5 seconds
            # measure_state.measure_err_index += 1
            # if (measure_state.measure_err_index > 5):
            #     send.cmd("loff:%.2f" % mag)
            #     send.keito(send.WITO.WAIT)
            #     measure_state.measure_err_index = 0

            # send every 1 second
            send.cmd("loff:%.2f" % mag)
            send.keito(send.WITO.WAIT)

            time.sleep(.9)

    def __measure_step_measuring(self):
        mx.freq(calib.data['freq'][measure_state.index])
        if mx.read():
            mag, ang = calib.decode(measure_state.index, mx.imp_i, mx.imp_q)

            if mag > self.trigger:
                measure_state.state = MeasureState.Adapting
                print("Lead off detected: %.2f, limit(%d)" % (mag, self.trigger))
                return

            if measure_state.index == 127:
                paciente.R50K = mag

            if measure_state.index == 158:
                paciente.R100K = mag

            __print(self.show)
            measure_state.index += 1

            if measure_state.index >= len(calib.data['freq']):
                measure_state.state = MeasureState.Stop
                measure_state.index = 0
                if not self.running:
                    mx.off()

                time.sleep(.1)
                send.keito(send.WITO.END)
                send.cmd("end:1")
                return 0

    def update(self, state=0):
        if measure_state.state == measure_state.NULL and not self.running:
            return

        if measure_state.state == MeasureState.Stop:
            measure_state.state = MeasureState.NULL
            return

        if mx.is_ready() == False:
            measure_state.lock = False
            measure_state.state = measure_state.NULL
            time.sleep(.1)
            send.KEITO(send.WITO.ERROR, [send.ERROR.MX_NOT_READY], "MX not ready")
            return

        if measure_state.is_locked():
            return

        measure_state.lock = True
        if measure_state.state == MeasureState.Adapting:
            self.__measure_step_adapting()
            measure_state.lock = False
            return

        if measure_state.state == MeasureState.Measuring:
            self.__measure_step_measuring()
            measure_state.lock = False
            return

        if self.running:
            self.__measure_freq_raw()

        measure_state.lock = False


gc.collect()
measure = Measure()
