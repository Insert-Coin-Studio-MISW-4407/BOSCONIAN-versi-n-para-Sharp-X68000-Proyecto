import pygame


class CHeading:
    """Hacia donde apunta la nave: uno de los 8 sentidos (vector unitario).

    La nave dispara hacia adelante y hacia atras a lo largo de este vector, y el
    sprite se gira para mostrarlo. Empieza apuntando hacia arriba.
    """

    def __init__(self, direction: pygame.Vector2 | None = None) -> None:
        self.direction = pygame.Vector2(direction) if direction else pygame.Vector2(0, -1)
