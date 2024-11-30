import sounddevice as sd
import numpy as np
import cv2
import time
import sys
import os
import tempfile
import subprocess

# Parameter für Audioerkennung
SAMPLE_RATE = 44100
CHANNELS = 1
THRESHOLD = 0.1  # Schwellwert für Audioerkennung (je höher, desto empfindlicher)


# Funktionsdefinition zur Audioaufnahme
def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    volume_norm = np.linalg.norm(indata) * 10
    if volume_norm > THRESHOLD:
        print("[INFO] Geräusch erkannt, Aufnahme wird gestartet...")
        capture_image()


# Funktionsdefinition zum Aufnehmen eines Bildes
def capture_image():
    # Kamera öffnen
    cap = cv2.VideoCapture(0)  # 0 ist die Standardkamera
    if not cap.isOpened():
        print("[ERROR] Kamera konnte nicht geöffnet werden!")
        return

    ret, frame = cap.read()  # Bildaufnahme
    if ret:
        # Temporäre Datei erstellen
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        image_path = temp_file.name
        cv2.imwrite(image_path, frame)  # Bild speichern
        print(f"[INFO] Bild gespeichert: {image_path}")

        # ArUco-Skript aufrufen und Bild übergeben
        run_aruco_script(image_path)

    cap.release()


# Funktionsdefinition zum Ausführen des ArUco-Erkennungs-Skripts
def run_aruco_script(image_path):
    script_path = 'VideoDetection.py'  # Pfad zum ArUco Erkennungs-Skript
    if not os.path.isfile(script_path):
        print("[ERROR] ArUco-Skript nicht gefunden!")
        return

    # Befehl zum Ausführen des ArUco-Skripts mit dem Bildpfad als Argument
    command = ['python', script_path, '-i', image_path, '-t', 'DICT_ARUCO_ORIGINAL']
    subprocess.run(command)
    print(f"[INFO] ArUco-Skript mit Bild {image_path} ausgeführt.")


# Hauptprogramm, das den Audio-Stream startet
def main():
    print("[INFO] Warten auf Audioeingabe...")
    with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=SAMPLE_RATE):
        while True:
            time.sleep(1)  # Warten auf Audioereignisse


if __name__ == "__main__":
    main()
