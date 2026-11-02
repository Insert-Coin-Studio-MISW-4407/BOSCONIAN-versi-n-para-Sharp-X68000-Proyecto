import pygame


class CStar:
    """Estrella del fondo.

    `pos` esta en coordenadas de la VISTA (no del mundo): el fondo es infinito y se
    repite, asi que basta con desplazar cada estrella y envolverla en la vista.
    `parallax` < 1 hace que las capas lejanas se muevan mas despacio que la camara.
    """

    def __init__(self, pos: pygame.Vector2, color: pygame.Color, parallax: float,
                 blink_interval: float) -> None:
        self.pos = pygame.Vector2(pos)
        self.color = color
        self.parallax = parallax
        self.blink_interval = blink_interval
        self.blink_timer = blink_interval
        self.visible = True
