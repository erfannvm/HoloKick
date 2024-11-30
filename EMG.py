import serial

ser = serial.Serial(
    port='/dev/tty.usbserial-A8003MY1',  # Ersetze 'COM1' mit deinem Portnamen (z.B. '/dev/ttyUSB0' auf Linux)
    baudrate=57600,  # Baudrate
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1  # Timeout für Leseoperationen
)


def read_and_parse_data():
    buffer = b""  # Zwischenspeicher für eingehende Daten
    while True:
        # Daten von der seriellen Schnittstelle lesen
        data = ser.read(100)  # Liest bis zu 100 Bytes (angepasst an deine Datenrate)
        if not data:
            continue

        buffer += data  # Neue Daten an den Zwischenspeicher anhängen

        # Auf das Trennzeichen '#' synchronisieren
        while b'#' in buffer:
            # Paket vor dem Trennzeichen extrahieren
            packet, _, buffer = buffer.partition(b'#')

            # Prüfen, ob das Paket 6 Werte (12 Bytes) enthält
            if len(packet) == 12:
                # Werte extrahieren (2 Bytes pro Wert, Little Endian)
                values = [int.from_bytes(packet[i:i + 2], byteorder='little', signed=False) for i in range(0, 12, 2)]
                print("Empfangene Werte:", values)
            else:
                print("Ungültiges Paket empfangen:", packet)


try:
    read_and_parse_data()
except KeyboardInterrupt:
    print("Programm beendet.")
finally:
    ser.close()