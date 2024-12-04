import cv2
import numpy as np
import sounddevice as sd

# Einstellbare Schwellenwerte
VOLUME_THRESHOLD = 0.3  # Lautstärkeschwellenwert
WHITE_THRESHOLD = 0.01   # Schwellenwert für den Weißanteil (Prozent)

# Hauptmethode
def analyze_audio_and_image():
    # Kamera öffnen
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Fehler: Kamera konnte nicht geöffnet werden.")
        return

    print("Drücke 'q', um das Programm zu beenden. Sprich laut genug, um die Analyse auszulösen.")

    # Funktion zur Audioverarbeitung
    def audio_callback(indata, frames, time, status):
        if status:
            print(f"Audio-Fehler: {status}")
        # Lautstärke berechnen
        volume = np.sqrt(np.mean(indata ** 2))
        if volume > VOLUME_THRESHOLD:
            analyze_frame()

    # Funktion zur Bildverarbeitung und Weißanteilsberechnung
    def analyze_frame():
        ret, frame = camera.read()
        if not ret:
            print("Fehler: Konnte kein Bild von der Kamera lesen.")
            return

        # Bild in HSV umwandeln
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Masken für roten Bereich erstellen
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)
        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        # Kombinieren der Masken
        red_mask = cv2.bitwise_or(mask1, mask2)

        # Weißanteil berechnen (Rot im Originalbild)
        white_pixels = np.sum(red_mask > 0)
        total_pixels = red_mask.size
        white_percentage = white_pixels / total_pixels

        # Schwellenwert überprüfen
        if white_percentage >= WHITE_THRESHOLD:
            print(f"Roter Bereich erkannt. Weißanteil: {white_percentage:.2%}. Rückgabewert: True")
        else:
            print(f"Kein signifikanter roter Bereich. Weißanteil: {white_percentage:.2%}. Rückgabewert: False")

    # Audiostream und Schleife starten
    with sd.InputStream(callback=audio_callback):
        while True:
            # Kamerabild anzeigen
            ret, frame = camera.read()
            if ret:
                cv2.imshow("Live-Ansicht", frame)
            else:
                print("Fehler: Konnte kein Bild anzeigen.")

            # Überprüfen, ob der Benutzer 'q' drückt
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Programm beendet.")
                break

    # Ressourcen freigeben
    camera.release()
    cv2.destroyAllWindows()

# Methode ausführen
analyze_audio_and_image()
