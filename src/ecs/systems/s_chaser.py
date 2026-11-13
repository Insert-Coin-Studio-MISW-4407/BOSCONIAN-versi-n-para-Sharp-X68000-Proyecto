import esper
import pygame

from src.ecs.components.c_chaser import CChaser
from src.ecs.components.c_heading import CHeading
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.engine.world_math import signed_delta


def system_chaser(world: esper.World, delta_time: float, target: pygame.Vector2 | None,
                  world_size: pygame.Vector2, despawn_distance: float) -> None:
    """Las naves enemigas giran hacia la nave del jugador a velocidad limitada.

    El rumbo real es continuo, pero el sprite (CHeading) solo mira en `directions`
    sentidos, como en el arcade. Las que quedan muy lejos se retiran para no
    acumular enemigos fuera de pantalla. Sin objetivo siguen en linea recta.
    """
    c_c: CChaser
    for entity, (c_c, c_t, c_s, c_v, c_h) in world.get_components(
            CChaser, CTransform, CSurface, CVelocity, CHeading):
        if target is not None:
            center = c_t.pos + pygame.Vector2(c_s.area.size) / 2
            to_target = signed_delta(center, target, world_size)
            if to_target.length() > despawn_distance:
                world.delete_entity(entity)
                continue
            if to_target.length_squared() > 0:
                c_v.vel = turn_towards(c_v.vel, to_target, c_c.turn_rate * delta_time)
        c_v.vel.scale_to_length(c_c.speed)
        c_h.direction = quantize(c_v.vel, c_c.directions)


def turn_towards(current: pygame.Vector2, wanted: pygame.Vector2,
                 max_degrees: float) -> pygame.Vector2:
    """Gira `current` hacia `wanted` como mucho `max_degrees`, por el lado mas corto."""
    angle = current.angle_to(wanted)
    angle = (angle + 180) % 360 - 180
    angle = max(-max_degrees, min(max_degrees, angle))
    return current.rotate(angle)


def quantize(direction: pygame.Vector2, steps: int) -> pygame.Vector2:
    """La direccion mas cercana de `steps` sentidos repartidos en el circulo."""
    step = 360 / steps
    _, angle = direction.as_polar()
    return pygame.Vector2(1, 0).rotate(round(angle / step) * step)
