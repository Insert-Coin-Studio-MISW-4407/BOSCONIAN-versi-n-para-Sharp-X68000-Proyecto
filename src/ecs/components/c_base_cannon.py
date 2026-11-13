import pygame


class CBaseCannon:
    """Uno de los seis canones de una estacion.

    - base_entity: entidad del nucleo (la que tiene CBase).
    - frames: reposo, cargando y disparando.
    - destroyed: textura que queda en su lugar al destruirlo.
    - state/timer: ciclo REST -> CHARGING -> FIRING -> REST. En reposo espera `timer`
      y solo carga si la nave esta a su alcance.
    """

    REST = 0
    CHARGING = 1
    FIRING = 2

    def __init__(self, base_entity: int, frames: list[pygame.Surface],
                 destroyed: pygame.Surface, start_timer: float) -> None:
        self.base_entity = base_entity
        self.frames = frames
        self.destroyed = destroyed
        self.state = self.REST
        self.timer = start_timer
