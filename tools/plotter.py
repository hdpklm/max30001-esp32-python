import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import find_peaks

# Configura el puerto serial (ajusta según sea necesario)
try:
	ser = serial.Serial('COM5', 115200, timeout=0.001)
	ser.write(b'init_max(); scan_ecg()\r\n')
except serial.SerialException as e:
	print(f"Error al abrir el puerto serial: {e}")
	exit()

# Lista para almacenar los datos
data = []

def calculate_ppm(data, sampling_rate=128):
	peaks, _ = find_peaks(data, distance=sampling_rate//1.5)  # Ajusta distance según sea necesario
	avg_time = np.mean(np.diff(peaks[-7:-2])) if len(peaks) > 8 else 0
	ppm_ms = avg_time / sampling_rate
	ppm = 60 / ppm_ms if avg_time > 0 else 0

	ppm2 = 0
	peaks, _ = find_peaks(data, distance=sampling_rate//1.5)  # Ajusta distance según sea necesario
	if (len(peaks) > 3):
		p1 = peaks[0] if len(peaks) > 0 else 0
		p2 = peaks[-2] if len(peaks) > 0 else 0
		ppm2 = (len(peaks) -2) * 60 / (len(data[p1:p2]) / sampling_rate) if len(data) > 0 else 0
	return ppm, ppm2, peaks

sec = 0
def update(frame):
	global data, sec
	# Lee una línea del puerto serial

	try:
		line = None
		while ser.in_waiting > 0:
			line = ser.readline().decode('utf-8').strip()
			if not line:
				break

			value = float(line)
			if value == 0:
				continue

			data.append(value)
			if len(data) > 25600:
				data.pop(0)

		if len(data) < 2:
			return

		if len(data) >= 500:
			data_to_plot = data[-500:]
			offset = len(data) - 500
		else:
			data_to_plot = data
			offset = 0

		ppm, ppm2, peaks, peaks_t = 0, 0, [0], [0]
		if len(data) > 128*5:
			ppm, ppm2, peaks = calculate_ppm(data)
			peaks = [p for p in peaks if p >= offset]
			peaks_t = np.array(peaks) - offset

		sec += 1
		plt.clf()
		plt.plot(data_to_plot)
		plt.plot(peaks_t, np.array(data_to_plot)[peaks_t], "x")
		plt.xlabel('Time')
		plt.ylim(0, 0.0005)
		plt.ylabel('ECG')
		plt.title(f"Pulsos por minuto (PPM): {ppm:.2f} (PPM2): {ppm2:.2f}, sec: {sec}")

	except ValueError as e:
		print(f"Error de conversión: {e}")
	except serial.SerialException as e:
		print(f"Error en la lectura del puerto serial: {e}")

fig = plt.figure()
ani = animation.FuncAnimation(fig, update, interval=100)

plt.show()
ser.close()
