import pygame


class CTransform:
    """Posicion de la entidad en coordenadas de MUNDO (no de pantalla).

    El mundo es mas grande que la pantalla y da la vuelta en ambos ejes; la conversion
    a pantalla la hace el sistema de render usando la camara.
    """

    def __init__(self, pos: pygame.Vector2) -> None:
        self.pos = pygame.Vector2(pos)
