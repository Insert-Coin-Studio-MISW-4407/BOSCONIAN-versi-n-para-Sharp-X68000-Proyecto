import random

import esper
import pygame

from src.create.prefab_creator import create_spy
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_heading import CHeading
from src.ecs.components.c_spy import CSpy
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.s_alert import system_report_spy
from src.ecs.systems.s_chaser import quantize
from src.ecs.systems.s_enemy_spawner import spawn_point
from src.engine.world_math import signed_delta


def system_spy_spawner(world: esper.World, delta_time: float, target: pygame.Vector2 | None,
                       heading: pygame.Vector2 | None, sprites_cfg: dict,
                       enemies_cfg: dict) -> None:
    """Cada cierto tiempo aparece una espia, nunca dos a la vez."""
    cfg = enemies_cfg["spy"]
    for _, c_sp in world.get_component(CEnemySpawner):
        c_sp.spy_timer -= delta_time
        if c_sp.spy_timer > 0:
            continue
        c_sp.spy_timer = random.uniform(*cfg["interval"])
        if target is None or world.get_component(CSpy):
            continue
        spawner_cfg = enemies_cfg["spawner"]
        pos = spawn_point(target, heading, spawner_cfg["spawn_distance"],
                          spawner_cfg["spawn_ahead_spread"])
        create_spy(world, sprites_cfg, enemies_cfg, pos, target)


def system_spy(world: esper.World, delta_time: float, target: pygame.Vector2 | None,
               world_size: pygame.Vector2) -> None:
    """Comportamiento de la espia. Si escapa, reporta y la condicion pasa a RED."""
    c_spy: CSpy
    for entity, (c_spy, c_t, c_s, c_v, c_h) in world.get_components(
            CSpy, CTransform, CSurface, CVelocity, CHeading):
        center = c_t.pos + pygame.Vector2(c_s.area.size) / 2
        to_target = signed_delta(center, target, world_size) if target is not None else None

        if c_spy.state == CSpy.APPROACH:
            if to_target is None:
                c_spy.state = CSpy.FLEE
            elif to_target.length() <= c_spy.watch_radius:
                c_spy.state = CSpy.WATCH
                c_spy.timer = c_spy.report_time
                c_spy.orbit = random.choice((-1, 1))
            elif to_target.length_squared() > 0:
                c_v.vel = to_target.normalize() * c_spy.speed
        if c_spy.state == CSpy.WATCH:
            c_spy.timer -= delta_time
            if c_spy.timer <= 0 or to_target is None:
                c_spy.state = CSpy.FLEE
            elif to_target.length_squared() > 0:
                # Da vueltas alrededor de la nave corrigiendo la distancia
                radial = to_target.normalize()
                correction = (to_target.length() - c_spy.watch_radius) / c_spy.watch_radius
                c_v.vel = (radial.rotate(90 * c_spy.orbit) + radial * correction * 2)
                c_v.vel.scale_to_length(c_spy.speed)
        if c_spy.state == CSpy.FLEE:
            if to_target is not None and to_target.length_squared() > 0:
                c_v.vel = -to_target.normalize() * c_spy.flee_speed
                if to_target.length() > c_spy.escape_distance:
                    system_report_spy(world)
                    world.delete_entity(entity)
                    continue
            elif c_v.vel.length_squared() > 0:
                c_v.vel.scale_to_length(c_spy.flee_speed)
        if c_v.vel.length_squared() > 0:
            c_h.direction = quantize(c_v.vel, 16)
