from micropython import const

# Configuration for ESP32-D0
# for other boards, please copy this file from config/config-esp32-XX.py
# then rename it to ~/config.py

PIN_UART_TX = const(1)
PIN_UART_RX = const(3)
PIN_MAX_PWR = const(12)
PIN_SPI_CS = const(27)
PIN_SPI_CLK = const(14)
PIN_SPI_MOSI = const(13)
PIN_SPI_MISO = const(9)
PIN_MAX_INT1 = const(11)
PIN_MAX_INT2 = const(10)
PIN_MAX_FCLK = const(21)
PIN_KEITO_RX = const(3)
PIN_KEITO_TX = const(1)
PIN_DEBUG = const(23)


