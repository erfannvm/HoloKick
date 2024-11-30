import pygame
import random
import sys
import math
import os

pygame.init()

# Bildschirmkonfiguration
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("HoloKick")

# Farben
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Variablen
level = 1
max_level = 10
initial_bullseye_radius = 90
initial_bullseye_speed = 3
game_over = False

# Lade die ArUco-Marker-Bilder
markers = [
    pygame.image.load(os.path.join("markers", f"marker_{i}.png"))
    for i in range(4)
]

# Bullseye-Klasse
class HoloKick:
    def __init__(self, level):
        self.level = level
        self.radius = self.set_radius()
        self.x, self.y = self.set_initial_position()
        self.angle = 0
        self.image = pygame.image.load('bullseye.png')
        self.image = pygame.transform.scale(self.image, (self.radius * 2, self.radius * 2))
        self.marker = pygame.image.load(os.path.join("markers", "marker_4.png"))
        self.marker = pygame.transform.scale(self.marker, (50, 50))
        self.marker_background = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(self.marker_background, SKY_BLUE, (30, 30), 30)
        self.dx, self.dy = self.set_speed()

    def set_initial_position(self):
        if self.level == 3:
            return self.radius + 10, SCREEN_HEIGHT - self.radius - 30
        elif self.level == 4:
            return SCREEN_WIDTH - self.radius - 30, self.radius + 10
        else:
            return (
                random.randint(self.radius + 20, SCREEN_WIDTH - self.radius - 20),
                random.randint(self.radius + 20, SCREEN_HEIGHT - self.radius - 20)
            )

    def set_radius(self):
        if self.level < 5:
            return max(20, initial_bullseye_radius - (self.level - 1) * 10)
        else:
            return 50

    def set_speed(self):
        speed = initial_bullseye_speed if self.level < 5 else initial_bullseye_speed + (
                    self.level - 4) * 0.5
        angle = random.uniform(0, 2 * math.pi)
        return speed * math.cos(angle), speed * math.sin(angle)

    def draw(self):
        # Rotation des Bullseye
        self.angle += 5
        if self.angle >= 360:
            self.angle = 0

        # Rotiertes Bullseye-Bild zeichnen
        rotated_bullseye = pygame.transform.rotate(self.image, self.angle)
        bullseye_rect = rotated_bullseye.get_rect(center=(self.x, self.y))
        screen.blit(rotated_bullseye, bullseye_rect.topleft)

        # Runder Hintergrund und Marker in der Mitte des Bullseyes zeichnen
        marker_bg_rect = self.marker_background.get_rect(center=(self.x, self.y))
        marker_rect = self.marker.get_rect(center=(self.x, self.y))
        screen.blit(self.marker_background, marker_bg_rect.topleft)  # Runden Hintergrund zeichnen
        screen.blit(self.marker, marker_rect.topleft)  # Marker zeichnen

    def is_clicked(self, pos):
        distance = math.sqrt((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2)
        return distance <= self.radius

    def move(self):
        if level >= 5:
            self.x += self.dx
            self.y += self.dy
            if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
                self.dx *= -1
            if self.y <= self.radius or self.y >= SCREEN_HEIGHT - self.radius:
                self.dy *= -1

def draw_corner_markers():
    """Zeichne die vier gespeicherten ArUco-Marker in den Ecken des Bildschirms."""
    marker_size = 60  # Größe der Marker in Pygame
    # Marker an den vier Ecken anzeigen
    screen.blit(pygame.transform.scale(markers[0], (marker_size, marker_size)), (0, 0))
    screen.blit(pygame.transform.scale(markers[1], (marker_size, marker_size)), (SCREEN_WIDTH - marker_size, 0))
    screen.blit(pygame.transform.scale(markers[2], (marker_size, marker_size)), (0, SCREEN_HEIGHT - marker_size))
    screen.blit(pygame.transform.scale(markers[3], (marker_size, marker_size)), (SCREEN_WIDTH - marker_size, SCREEN_HEIGHT - marker_size))

# Spiel Schleife
def main():
    global level, game_over, bullseye
    clock = pygame.time.Clock()

    # Lade den Retro-Font
    font = pygame.font.Font('PressStart2P-Regular.ttf', 28)

    # Erstelle das erste Bullseye
    bullseye = HoloKick(level)

    while True:
        screen.fill(SKY_BLUE)

        # Ereignisse
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if bullseye.is_clicked(event.pos):
                    level += 1
                    if level > max_level:
                        game_over = True  # Setze game_over auf True, wenn Level > max_level
                    else:
                        bullseye = HoloKick(level)
                else:
                    game_over = True

            if event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_r:
                    level = 1
                    game_over = False
                    bullseye = HoloKick(level)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        bullseye.move()
        bullseye.draw()

        # Zeichne die Marker
        draw_corner_markers()

        # Level-Text anzeigen
        level_text = font.render(f'Level: {level}', True, BLACK)
        if level == 11:
            level_text = font.render("Well played!", True, BLACK)
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))

        if game_over:
            if level > max_level:
                game_over_text = font.render('Gewonnen!', True, BLACK)
            else:
                game_over_text = font.render('Game Over!', True, BLACK)
            restart_text = font.render('Drücke R für Neustart', True, BLACK)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()