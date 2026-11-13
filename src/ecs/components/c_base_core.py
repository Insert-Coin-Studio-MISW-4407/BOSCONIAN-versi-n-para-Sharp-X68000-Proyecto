import pygame


class CBaseCore:
    """Nucleo de una estacion: se abre y se cierra en ciclo.

    Solo es vulnerable mientras esta abierto (cuadro 0); cerrado absorbe las balas.
    `frames` va de abierto (0) a cerrado (ultimo).
    """

    OPENING = "OPENING"
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"

    def __init__(self, base_entity: int, frames: list[pygame.Surface], frame_time: float,
                 open_time: float, closed_time: float, start_timer: float) -> None:
        self.base_entity = base_entity
        self.frames = frames
        self.frame_time = frame_time
        self.open_time = open_time
        self.closed_time = closed_time
        self.state = self.CLOSED
        self.frame = len(frames) - 1
        self.timer = start_timer

    @property
    def is_open(self) -> bool:
        return self.state == self.OPEN
