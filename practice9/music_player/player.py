import pygame
import os
import sys

WIDTH, HEIGHT = 700, 300
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

MUSIC_FOLDER = os.path.join(os.path.dirname(__file__), "music", "sample_tracks")

def run_player():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Music Player")

    font = pygame.font.SysFont("Arial", 24)
    clock = pygame.time.Clock()

    playlist = []

    if os.path.exists(MUSIC_FOLDER):
        for file in os.listdir(MUSIC_FOLDER):
            if file.lower().endswith(".mp3") or file.lower().endswith(".wav"):
                playlist.append(os.path.join(MUSIC_FOLDER, file))

    playlist.sort()
    current = 0
    playing = False

    running = True
    while running:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False

                elif event.key == pygame.K_p:
                    if playlist:
                        pygame.mixer.music.load(playlist[current])
                        pygame.mixer.music.play()
                        playing = True

                elif event.key == pygame.K_s:
                    pygame.mixer.music.stop()
                    playing = False

                elif event.key == pygame.K_n:
                    if playlist:
                        current = (current + 1) % len(playlist)
                        pygame.mixer.music.load(playlist[current])
                        pygame.mixer.music.play()
                        playing = True

                elif event.key == pygame.K_b:
                    if playlist:
                        current = (current - 1) % len(playlist)
                        pygame.mixer.music.load(playlist[current])
                        pygame.mixer.music.play()
                        playing = True

        screen.fill(WHITE)

        if playlist:
            name = os.path.basename(playlist[current])
            text = font.render(f"Track: {name}", True, BLACK)
            screen.blit(text, (20, 50))

            status = "Playing" if playing else "Stopped"
            status_text = font.render(f"Status: {status}", True, BLACK)
            screen.blit(status_text, (20, 100))
        else:
            text = font.render("No music files found", True, BLACK)
            screen.blit(text, (20, 50))

        controls = font.render("P=Play  S=Stop  N=Next  B=Back  Q=Quit", True, BLACK)
        screen.blit(controls, (20, 200))

        pygame.display.flip()

    pygame.quit()
    sys.exit()