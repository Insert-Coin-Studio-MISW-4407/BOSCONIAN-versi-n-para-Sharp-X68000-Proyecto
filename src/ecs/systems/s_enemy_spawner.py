import random

import esper
import pygame

from src.create.prefab_creator import create_enemy_ship, create_formation
from src.ecs.components.c_chaser import CChaser
from src.ecs.components.c_enemy_spawner import CEnemySpawner


def spawn_point(target: pygame.Vector2, heading: pygame.Vector2, distance: float,
                spread: float) -> pygame.Vector2:
    """Punto a `distance` de la nave, por delante de ella (hasta `spread` grados de desvio).

    La nave del jugador nunca se detiene: si los enemigos salieran por detras casi
    nunca la alcanzarian, asi que aparecen fuera de pantalla en su camino.
    """
    direction = pygame.Vector2(heading)
    if direction.length_squared() == 0:
        direction = pygame.Vector2(0, -1)
    direction.scale_to_length(distance)
    return target + direction.rotate(random.uniform(-spread, spread))


def system_enemy_spawner(world: esper.World, delta_time: float, target: pygame.Vector2 | None,
                         heading: pygame.Vector2 | None, red_alert: bool, sprites_cfg: dict,
                         enemies_cfg: dict) -> None:
    """Lanza naves enemigas desde fuera de la pantalla hacia la nave.

    En condicion RED salen mas seguido. No se lanzan si no hay nave o si ya hay
    `max_alive` naves persiguiendo.
    """
    cfg = enemies_cfg["spawner"]
    for _, c_sp in world.get_component(CEnemySpawner):
        c_sp.timer -= delta_time
        if c_sp.timer > 0:
            continue
        c_sp.timer = random.uniform(*cfg["red_interval" if red_alert else "interval"]) \
            * c_sp.interval_scale
        if target is None or len(world.get_component(CChaser)) >= cfg["max_alive"]:
            continue
        pos = spawn_point(target, heading, cfg["spawn_distance"], cfg["spawn_ahead_spread"])
        formation_cfg = enemies_cfg["formation"]
        if random.random() < formation_cfg["red_chance" if red_alert else "chance"]:
            create_formation(world, sprites_cfg, enemies_cfg, pos, target)
        else:
            create_enemy_ship(world, sprites_cfg, enemies_cfg, random.choice(cfg["types"]),
                              pos, target)
