"""Lo que puede matar a la nave del jugador."""
import esper
import pygame

from src.ecs.components.c_enemy import CEnemy
from src.ecs.components.c_invulnerable import CInvulnerable
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy_bullet import CTagEnemyBullet
from src.ecs.systems.s_enemy_hits import destroy_enemy
from src.engine.collision import collide_world
from src.engine.world_math import distance

# Al chocar, estas piezas se destruyen junto con la nave; el nucleo resiste.
_SURVIVES_RAMMING = ("core",)


def system_invulnerable(world: esper.World, delta_time: float) -> None:
    for entity, c_inv in world.get_component(CInvulnerable):
        c_inv.remaining -= delta_time
        if c_inv.remaining <= 0:
            world.remove_component(entity, CInvulnerable)


def system_player_hits(world: esper.World, player: int, world_size: pygame.Vector2,
                       blasts: list[tuple[pygame.Vector2, float]], sprites_cfg: dict,
                       enemies_cfg: dict) -> bool:
    """True si la nave murio este frame.

    Mueren la nave y lo que choca con ella (como en Bosconian, embestir da los puntos
    del enemigo). Tambien matan las balas enemigas y las ondas de las minas.
    """
    if world.has_component(player, CInvulnerable):
        return False
    p_t = world.component_for_entity(player, CTransform)
    p_s = world.component_for_entity(player, CSurface)
    center = p_t.pos + pygame.Vector2(p_s.area.size) / 2

    if any(distance(center, blast_center, world_size) <= radius for blast_center, radius in blasts):
        return True

    for bullet, (b_t, b_s, _) in world.get_components(CTransform, CSurface, CTagEnemyBullet):
        if collide_world(p_t.pos, p_s.area, b_t.pos, b_s.area, world_size):
            world.delete_entity(bullet)
            return True

    for enemy, (e_t, e_s, c_e) in world.get_components(CTransform, CSurface, CEnemy):
        if collide_world(p_t.pos, p_s.area, e_t.pos, e_s.area, world_size):
            if c_e.kind not in _SURVIVES_RAMMING:
                destroy_enemy(world, enemy, sprites_cfg, enemies_cfg)
            return True
    return False
