import pygame


class CAnimation:
    """Animacion por cuadros: cada cuadro es un recorte del atlas.

    - frames: superficies de cada cuadro (todas del mismo tamano, asi el centro no salta).
    - frame_time: segundos que dura cada cuadro.
    - loop: True repite la animacion; False se queda en el ultimo cuadro y marca `finished`.
    - delete_on_end: la entidad se borra al terminar (explosiones).
    """

    def __init__(self, frames: list[pygame.Surface], frame_time: float, loop: bool = True,
                 delete_on_end: bool = False) -> None:
        self.frames = frames
        self.frame_time = frame_time
        self.loop = loop
        self.delete_on_end = delete_on_end
        self.current = 0
        self.timer = frame_time
        self.finished = False
        self.paused = False

    def set_frame(self, index: int) -> None:
        self.current = index
        self.timer = self.frame_time
