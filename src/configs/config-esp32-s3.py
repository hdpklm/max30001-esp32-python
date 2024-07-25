from micropython import const

# Configuration for ESP32-S3
# for other boards, please copy this file from config/config-esp32-XX.py
# then rename it to ~/config.py

PIN_MAX_PWR = const(1)
PIN_SPI_CS = const(42)
PIN_SPI_CLK = const(14)
PIN_SPI_MOSI = const(13)
PIN_SPI_MISO = const(12)
PIN_MAX_INT1 = const(40)
PIN_MAX_INT2 = const(41)
PIN_MAX_FCLK = const(21)
PIN_KEITO_RX = const(44)
PIN_KEITO_TX = const(43)
