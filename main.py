import render
import pygame
import threading


Vector2 = render.Vector2
Color = pygame.Color


def on_draw():
    render.start_frame()

    render.end_frame()


if __name__ == "__main__":
    pygame.init()
    render.init((1920, 1080))
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        on_draw()

    pygame.quit()