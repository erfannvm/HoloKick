import pygame
import random
import sys
import math
from pythonosc import udp_client
import time
import threading
import subprocess
# mike ist ein kleiner type mit grossen ambitionen
#ja man -mike
# Initialisiere Pygame
pygame.init()

# Bildschirmkonfiguration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bullseye-Spiel")

# Farben
SKY_BLUE = (135, 206, 235)  # Himmelblau
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Spielvariablen
level = 1
max_level = 10
initial_bullseye_radius = 90  # Startgröße des Bullseyes
initial_bullseye_speed = 3  # Startgeschwindigkeit des Bullseyes
game_over = False

# OSC Client initialisieren
osc_client = udp_client.SimpleUDPClient('127.0.0.1', 8000)  # Ziel-IP und Port

# Bullseye-Klasse
class Bullseye:
    def __init__(self, level):
        self.level = level  # Level speichern
        self.radius = self.set_radius()  # Größe des Bullseyes festlegen
        self.x, self.y = self.set_initial_position()  # Position des Bullseyes festlegen
        self.angle = 0
        self.image = pygame.image.load('bullseye.png')  # Bilddatei umbenannt
        self.image = pygame.transform.scale(self.image, (self.radius * 2, self.radius * 2))  # Bullseye-Größe anpassen
        self.dx, self.dy = self.set_speed()  # Geschwindigkeit setzen

    def set_initial_position(self):
        """Setze die Startposition des Bullseyes basierend auf dem aktuellen Level."""
        if self.level == 3:
            return self.radius + 10, SCREEN_HEIGHT - self.radius - 30  # Unten links, Abstand zum Rahmen
        elif self.level == 4:
            return SCREEN_WIDTH - self.radius - 30, self.radius + 10  # Oben rechts, Abstand zum Rahmen
        else:
            return (
                random.randint(self.radius + 20, SCREEN_WIDTH - self.radius - 20),
                random.randint(self.radius + 20, SCREEN_HEIGHT - self.radius - 20)
            )

    def set_radius(self):
        """Setze den Radius des Bullseyes basierend auf dem aktuellen Level."""
        if self.level < 5:
            return max(20, initial_bullseye_radius - (self.level - 1) * 10)  # Pro Level 10 Pixel kleiner, minimum 20
        else:
            return 50  # Ab Level 5 bleibt der Radius konstant

    def set_speed(self):
        """Setze die Geschwindigkeit des Bullseyes basierend auf dem aktuellen Level."""
        speed = initial_bullseye_speed if self.level < 5 else initial_bullseye_speed + (
                    self.level - 4) * 0.5  # Geschwindigkeit erhöhen ab Level 5
        angle = random.uniform(0, 2 * math.pi)  # Zufälliger Winkel
        return speed * math.cos(angle), speed * math.sin(angle)

    def draw(self):
        """Zeichne das Bullseye auf dem Bildschirm."""
        self.angle += 5
        if self.angle >= 360:
            self.angle = 0

        rotated_bullseye = pygame.transform.rotate(self.image, self.angle)
        bullseye_rect = rotated_bullseye.get_rect(center=(self.x, self.y))
        screen.blit(rotated_bullseye, bullseye_rect.topleft)

    def is_clicked(self, pos):
        """Überprüfe, ob das Bullseye geklickt wurde."""
        distance = math.sqrt((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2)
        return distance <= self.radius

    def move(self):
        """Bewege das Bullseye, überprüfe Bildschirmränder und passe die Richtung an."""
        if level >= 5:
            self.x += self.dx
            self.y += self.dy

            # Überprüfe, ob das Bullseye den Bildschirmrand berührt
            if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
                self.dx *= -1  # Umkehren der horizontalen Richtung
            if self.y <= self.radius or self.y >= SCREEN_HEIGHT - self.radius:
                self.dy *= -1  # Umkehren der vertikalen Richtung

# Funktion zum Senden der OSC-Daten
def send_osc_data():
    while True:
        if not game_over:
            osc_client.send_message("/bullseye/position", (bullseye.x, bullseye.y))
            time.sleep(0.5)  # 0,5 Sekunden warten

# Funktion zum Starten des ReceiverOSC-Programms
def start_receiver_osc():
    global receiver_process
    receiver_process = subprocess.Popen(['python', 'ReceiverOSC.py'])  # ReceiverOSC starten

# Funktion zum Beenden des ReceiverOSC-Programms
def stop_receiver_osc():
    if receiver_process:
        receiver_process.terminate()  # Beende den ReceiverOSC-Prozess

# Spiel Schleife
def main():
    global level, game_over, bullseye
    clock = pygame.time.Clock()

    # Lade den Retro-Font
    font = pygame.font.Font('PressStart2P-Regular.ttf', 28)  # Kleinere Schriftgröße für Retro-Font

    # Erstelle das erste Bullseye
    bullseye = Bullseye(level)

    # Starte den Thread zum Senden von OSC-Daten
    osc_thread = threading.Thread(target=send_osc_data)
    osc_thread.daemon = True
    osc_thread.start()

    # Starte den ReceiverOSC-Prozess
    start_receiver_osc()

    while True:
        screen.fill(SKY_BLUE)  # Fülle den Bildschirm mit himmelblau

        # Überprüfe auf Ereignisse
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_receiver_osc()  # Beende ReceiverOSC beim Schließen
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if bullseye.is_clicked(event.pos):
                    level += 1
                    if level > max_level:
                        print("Gewonnen! Du hast alle Level abgeschlossen!")
                        stop_receiver_osc()  # Beende ReceiverOSC beim Gewinnen
                        pygame.quit()
                        sys.exit()
                    bullseye = Bullseye(level)  # Erstelle ein neues Bullseye an einer zufälligen Position
                else:
                    game_over = True

            # Überprüfe auf Neustart bei Game Over
            if event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_r:
                    level = 1
                    game_over = False
                    bullseye = Bullseye(level)  # Setze das Bullseye zurück
                # Beende das Spiel, wenn die Escape-Taste gedrückt wird
                if event.key == pygame.K_ESCAPE:
                    stop_receiver_osc()  # Beende ReceiverOSC beim Beenden
                    pygame.quit()
                    sys.exit()

        # Bewege das Bullseye, wenn das Level 5 oder höher ist
        bullseye.move()

        # Zeichne das Bullseye
        bullseye.draw()

        # Zeichne den Level-Text (zentriert)
        level_text = font.render(f'Level: {level}', True, BLACK)
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))

        if game_over:
            game_over_text = font.render('Game Over!', True, BLACK)
            restart_text = font.render('Drücke R für Neustart', True, BLACK)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    receiver_process = None  # Globaler Prozess für ReceiverOSC
    main()
