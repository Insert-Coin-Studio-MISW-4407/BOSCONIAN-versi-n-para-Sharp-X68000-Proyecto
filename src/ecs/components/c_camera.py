import pygame


class CCamera:
    """Ventana del mundo que se esta viendo.

    `topleft` esta en coordenadas de mundo y `view` es el area de pantalla donde se
    dibuja el juego (el resto de la pantalla es el panel lateral).
    `delta` es cuanto se movio la camara en el ultimo frame por el camino mas corto:
    las estrellas lo usan para el parallax sin sufrir saltos al cruzar la costura.
    """

    def __init__(self, view: pygame.Rect) -> None:
        self.topleft = pygame.Vector2(0, 0)
        self.view = pygame.Rect(view)
        self.delta = pygame.Vector2(0, 0)
