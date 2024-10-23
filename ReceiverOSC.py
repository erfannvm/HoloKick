from pythonosc import dispatcher
from pythonosc import osc_server


# Callback-Funktion zum Verarbeiten der empfangenen Daten
def position_handler(unused_addr, x, y):
    print(f"Target Position: x={x}, y={y}")


def main():
    # Dispatcher erstellen
    disp = dispatcher.Dispatcher()
    disp.map("/bullseye/position", position_handler)  # OSC-Adresse registrieren

    # OSC-Server initialisieren
    server = osc_server.BlockingOSCUDPServer(("127.0.0.1", 8000), disp)  # IP und Port anpassen
    print("Starte OSC-Server... (drücke Strg+C zum Beenden)")

    # Server starten
    server.serve_forever()


if __name__ == "__main__":
    main()
