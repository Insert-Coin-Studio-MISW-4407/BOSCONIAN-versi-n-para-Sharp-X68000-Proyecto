import pygame


class CText:
    """Texto dibujado en coordenadas de PANTALLA (menus y HUD).

    `align` acepta "left", "center" y "right" y se resuelve en el sistema de render.
    """

    def __init__(self, text: str, font_path: str, size: int, color: pygame.Color,
                 pos: pygame.Vector2, align: str = "left") -> None:
        self.text = text
        self.font_path = font_path
        self.size = size
        self.color = color
        self.pos = pygame.Vector2(pos)
        self.align = align
