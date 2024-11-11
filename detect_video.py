import cv2
import numpy as np
import sounddevice as sd

# Parameter für die Audioüberwachung
AUDIO_THRESHOLD = 0.3  # Schwellenwert für das Audiosignal
SAMPLE_RATE = 44100  # Abtastrate des Mikrofons
DURATION = 0.5  # Dauer der Audioaufnahme in Sekunden

# ArUco Dictionary und Marker-IDs
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_1000)
parameters = cv2.aruco.DetectorParameters()  # DetectorParameter initialisieren
corner_marker_ids = [0, 1, 2, 3]  # Marker-IDs für die Ecken
target_marker_id = 4  # Marker-ID für das Ziel

# Statusvariablen
target_visible = False  # Speichert, ob das Ziel erkannt wurde

# Videoaufnahme initialisieren (Standardkamera verwenden)
cap = cv2.VideoCapture(0)


# Funktion zur Überwachung des Audiosignals
def check_audio_level():
    # Audio für eine kurze Dauer aufnehmen
    audio_data = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()  # Warten, bis die Aufnahme beendet ist
    # Berechnen des maximalen Pegels im Audiosignal
    max_level = np.max(np.abs(audio_data))
    # Rückgabe, ob der Pegel über dem Schwellenwert liegt
    return max_level > AUDIO_THRESHOLD


while cap.isOpened():
    # Frame von der Kamera lesen
    ret, frame = cap.read()
    if not ret:
        print("Fehler beim Lesen des Frames")
        break

    # ArUco Marker im Frame erkennen
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    # Wenn Marker gefunden wurden
    if ids is not None:
        ids = ids.flatten()  # IDs in eine flache Liste konvertieren
        detected_target = target_marker_id in ids  # Überprüfen, ob das Ziel-Marker erkannt wird

        # Marker zeichnen
        for i, marker_id in enumerate(ids):
            # Überprüfen, ob die erkannte ID eine der Eck-IDs oder die Ziel-ID ist
            if marker_id in corner_marker_ids or marker_id == target_marker_id:
                color = (0, 0, 255) if marker_id in corner_marker_ids else (0, 255, 0)
                # Umrandung um die erkannten Marker zeichnen
                cv2.polylines(frame, [corners[i].astype(int)], isClosed=True, color=color, thickness=2)

                # ID-Text neben dem Marker anzeigen
                center = tuple(corners[i][0].mean(axis=0).astype(int))
                cv2.putText(frame, f"ID: {marker_id}", (center[0], center[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Audiopegel prüfen
    if check_audio_level():
        # Momentaufnahme und Zielerkennung bei überschrittenem Audio-Schwellenwert
        if ids is not None and target_marker_id not in ids:
            print("Ziel getroffen")  # Ausgabe, wenn das Ziel verdeckt ist und Audiopegel überschritten wird
        else:
            print("Ziel sichtbar")  # Ausgabe, wenn das Ziel im Moment sichtbar ist

    # Frame anzeigen
    cv2.imshow('ArUco Marker Detection', frame)

    # Mit 'q' das Programm beenden
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Ressourcen freigeben
cap.release()
cv2.destroyAllWindows()
