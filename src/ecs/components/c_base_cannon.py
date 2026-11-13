import pygame


class CBaseCannon:
    """Uno de los seis canones de una estacion.

    - base_entity: entidad del nucleo (la que tiene CBase).
    - frames: reposo, cargando y disparando.
    - destroyed: textura que queda en su lugar al destruirlo.
    """

    def __init__(self, base_entity: int, frames: list[pygame.Surface],
                 destroyed: pygame.Surface) -> None:
        self.base_entity = base_entity
        self.frames = frames
        self.destroyed = destroyed
