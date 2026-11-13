import random

import esper
import pygame

from src.create.prefab_creator import create_enemy_bullet
from src.ecs.components.c_base_cannon import CBaseCannon
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.engine.world_math import signed_delta


def system_base_cannon(world: esper.World, delta_time: float, target: pygame.Vector2 | None,
                       world_size: pygame.Vector2, sprites_cfg: dict, enemies_cfg: dict) -> None:
    """Los canones disparan a la nave cuando la tienen a su alcance.

    Cada disparo se anuncia: el canon se pone rojo (CHARGING), luego se abre y dispara
    (FIRING) y vuelve a reposo una pausa al azar. `target` es el centro de la nave, o
    None si no hay nave (explotando o reapareciendo).
    """
    cfg = enemies_cfg["base"]["fire"]
    c_c: CBaseCannon
    for _, (c_c, c_t, c_s) in world.get_components(CBaseCannon, CTransform, CSurface):
        c_c.timer -= delta_time
        if c_c.timer > 0:
            continue
        center = c_t.pos + pygame.Vector2(c_s.area.size) / 2
        if c_c.state == CBaseCannon.REST:
            to_target = signed_delta(center, target, world_size) if target is not None else None
            if to_target is None or to_target.length() > cfg["range"]:
                c_c.timer = cfg["check_interval"]
                continue
            c_c.state = CBaseCannon.CHARGING
            c_c.timer = cfg["charge_time"]
        elif c_c.state == CBaseCannon.CHARGING:
            to_target = signed_delta(center, target, world_size) if target is not None else None
            if to_target is not None and to_target.length_squared() > 0:
                create_enemy_bullet(world, sprites_cfg, enemies_cfg, center, to_target)
            c_c.state = CBaseCannon.FIRING
            c_c.timer = cfg["fire_time"]
        else:
            c_c.state = CBaseCannon.REST
            c_c.timer = random.uniform(*cfg["cooldown"])
        c_s.surf = c_c.frames[c_c.state]
