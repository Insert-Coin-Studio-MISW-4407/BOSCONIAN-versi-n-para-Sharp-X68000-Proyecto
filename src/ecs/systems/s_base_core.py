import esper

from src.ecs.components.c_base_core import CBaseCore
from src.ecs.components.c_surface import CSurface


def system_base_core(world: esper.World, delta_time: float) -> None:
    """Ciclo del nucleo: cerrado -> abriendose -> abierto -> cerrandose -> cerrado.

    Mientras se abre o se cierra avanza un cuadro cada `frame_time`; abierto y cerrado
    duran `open_time` y `closed_time`.
    """
    c_core: CBaseCore
    c_s: CSurface
    for _, (c_core, c_s) in world.get_components(CBaseCore, CSurface):
        c_core.timer -= delta_time
        if c_core.timer > 0:
            continue
        last = len(c_core.frames) - 1
        if c_core.state == CBaseCore.CLOSED:
            c_core.state = CBaseCore.OPENING
        elif c_core.state == CBaseCore.OPEN:
            c_core.state = CBaseCore.CLOSING

        if c_core.state == CBaseCore.OPENING:
            c_core.frame -= 1
            if c_core.frame <= 0:
                c_core.frame = 0
                c_core.state = CBaseCore.OPEN
                c_core.timer = c_core.open_time
            else:
                c_core.timer = c_core.frame_time
        elif c_core.state == CBaseCore.CLOSING:
            c_core.frame += 1
            if c_core.frame >= last:
                c_core.frame = last
                c_core.state = CBaseCore.CLOSED
                c_core.timer = c_core.closed_time
            else:
                c_core.timer = c_core.frame_time
        c_s.surf = c_core.frames[c_core.frame]
