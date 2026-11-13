import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_surface import CSurface


def system_animation(world: esper.World, delta_time: float) -> None:
    """Avanza los cuadros de las animaciones y copia el actual a CSurface.

    Las animaciones que no se repiten se quedan en el ultimo cuadro; si piden
    `delete_on_end` (explosiones) la entidad se borra al terminar.
    """
    c_a: CAnimation
    c_s: CSurface
    for entity, (c_a, c_s) in world.get_components(CAnimation, CSurface):
        if not c_a.paused and not c_a.finished:
            c_a.timer -= delta_time
            while c_a.timer <= 0 and not c_a.finished:
                c_a.timer += c_a.frame_time
                if c_a.current + 1 < len(c_a.frames):
                    c_a.current += 1
                elif c_a.loop:
                    c_a.current = 0
                else:
                    c_a.finished = True
        if c_a.finished and c_a.delete_on_end:
            world.delete_entity(entity)
            continue
        c_s.surf = c_a.frames[c_a.current]
        c_s.area = c_s.surf.get_rect()
