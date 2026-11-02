import esper
import pygame

from src.ecs.components.c_heading import CHeading
from src.ecs.components.c_ship_motion import CShipMotion
from src.ecs.components.c_velocity import CVelocity


def system_ship_motion(world: esper.World, delta_time: float) -> None:
    """Movimiento con aceleracion: la velocidad persigue a la velocidad deseada.

    Si hay flechas presionadas, la nave gira hacia esa direccion y la velocidad deseada es
    `max_speed` en ella. Si no, la nave mantiene su direccion a `cruise_speed`. La velocidad
    real nunca salta: cambia como mucho `acceleration * delta_time` por frame, asi que
    arrancar, frenar y dar la vuelta llevan tiempo.
    """
    c_v: CVelocity
    c_m: CShipMotion
    c_h: CHeading
    for _, (c_v, c_m, c_h) in world.get_components(CVelocity, CShipMotion, CHeading):
        if c_m.input_dir.length_squared() > 0:
            c_h.direction = pygame.Vector2(c_m.input_dir)
            target = c_h.direction * c_m.max_speed
        else:
            target = c_h.direction * c_m.cruise_speed
        change = target - c_v.vel
        max_change = c_m.acceleration * delta_time
        if change.length() <= max_change:
            c_v.vel = pygame.Vector2(target)
        else:
            c_v.vel += change.normalize() * max_change
