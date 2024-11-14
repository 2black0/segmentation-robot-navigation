from machine import UART
import time

# Konfigurasi UART pada RX2 (GPIO16)
uart = UART(2, baudrate=115200, parity=None, stop=1, tx=17, rx=16)

while True:
    frame = bytearray()
    received_data = uart.read(1)  # Baca 1 byte dari UART
    if received_data:
        int_received = int.from_bytes(received_data, 'little')
        if int_received == 32:  # Cek header
            frame.extend(received_data)  # Tambahkan header ke frame
            next_bytes = uart.read(31)  # Baca 31 byte berikutnya
            if next_bytes:
                frame.extend(next_bytes)

                # Decode setiap channel dari frame
                ch1 = int.from_bytes(frame[2:4], 'little')
                ch2 = int.from_bytes(frame[4:6], 'little')
                ch3 = int.from_bytes(frame[6:8], 'little')
                ch4 = int.from_bytes(frame[8:10], 'little')
                ch5 = int.from_bytes(frame[10:12], 'little')
                ch6 = int.from_bytes(frame[12:14], 'little')
                ch7 = int.from_bytes(frame[14:16], 'little')
                ch8 = int.from_bytes(frame[16:18], 'little')
                ch9 = int.from_bytes(frame[18:20], 'little')
                ch10 = int.from_bytes(frame[20:22], 'little')
                ch11 = int.from_bytes(frame[22:24], 'little')
                ch12 = int.from_bytes(frame[24:26], 'little')
                ch13 = int.from_bytes(frame[26:28], 'little')

                # Tampilkan nilai channel pada terminal
                print("ch1=", ch1, "ch2=", ch2, "ch3=", ch3, "ch4=", ch4, "ch5=", ch5, "ch6=", ch6, "ch7=", ch7, "ch8=", ch8, "ch9=", ch9, "ch10=", ch10, "ch11=", ch11, "ch12=", ch12, "ch13=", ch13)
