import pygame


class CSurface:
    """Textura de la entidad.

    `area` es el recorte de la textura que se dibuja (el cuadro actual si la textura
    es un spritesheet animado) y define el tamaño de la entidad para colisiones.
    """

    def __init__(self, surface: pygame.Surface) -> None:
        self.surf = surface
        self.area = surface.get_rect()

    @staticmethod
    def get_area_relative(area: pygame.Rect, pos_topleft: pygame.Vector2) -> pygame.Rect:
        return pygame.Rect(pos_topleft.x, pos_topleft.y, area.w, area.h)
