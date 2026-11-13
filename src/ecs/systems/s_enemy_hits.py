"""Impactos sobre enemigos: balas del jugador, ondas de las minas y destruccion."""
import esper
import pygame

from src.create.prefab_creator import create_explosion
from src.ecs.components.c_blast import CBlast
from src.ecs.components.c_enemy import CEnemy
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_player_bullet import CTagPlayerBullet
from src.ecs.systems.s_game_stats import system_add_score
from src.engine.collision import collide_world
from src.engine.world_math import distance

# Lo que una onda expansiva puede destruir (las piezas de las estaciones la resisten)
_BLAST_KINDS = ("asteroid", "mine", "ship")


def entity_center(world: esper.World, entity: int) -> pygame.Vector2:
    c_t = world.component_for_entity(entity, CTransform)
    c_s = world.component_for_entity(entity, CSurface)
    return c_t.pos + pygame.Vector2(c_s.area.size) / 2


def destroy_enemy(world: esper.World, entity: int, sprites_cfg: dict,
                  enemies_cfg: dict) -> None:
    """Borra el enemigo, deja su explosion y suma sus puntos.

    Las minas dejan ademas una onda expansiva (CBlast) que se resuelve en
    system_blast el mismo frame.
    """
    c_e = world.component_for_entity(entity, CEnemy)
    center = entity_center(world, entity)
    explosion = create_explosion(world, sprites_cfg, enemies_cfg, center, c_e.explosion)
    if c_e.kind == "mine":
        world.add_component(explosion, CBlast(enemies_cfg["mine"]["blast_radius"]))
    system_add_score(world, c_e.points)
    # Se quita CEnemy ya mismo: la entidad muere al final del frame y no debe
    # recibir un segundo impacto mientras tanto.
    world.remove_component(entity, CEnemy)
    world.delete_entity(entity)


def system_bullet_hits(world: esper.World, world_size: pygame.Vector2, sprites_cfg: dict,
                       enemies_cfg: dict) -> None:
    """Cada bala del jugador destruye como mucho un enemigo y desaparece."""
    bullets = world.get_components(CTransform, CSurface, CTagPlayerBullet)
    for bullet, (b_t, b_s, _) in bullets:
        for enemy, (e_t, e_s, _) in world.get_components(CTransform, CSurface, CEnemy):
            if not world.has_component(enemy, CEnemy):
                continue
            if collide_world(b_t.pos, b_s.area, e_t.pos, e_s.area, world_size):
                world.delete_entity(bullet)
                destroy_enemy(world, enemy, sprites_cfg, enemies_cfg)
                break


def system_blast(world: esper.World, world_size: pygame.Vector2, sprites_cfg: dict,
                 enemies_cfg: dict) -> list[tuple[pygame.Vector2, float]]:
    """Resuelve las ondas expansivas de este frame (y las que encadenan).

    Devuelve los centros y radios de las ondas para que la escena compruebe si la
    nave del jugador quedo dentro.
    """
    blasts = []
    pending = world.get_component(CBlast)
    while pending:
        for blast_entity, c_b in pending:
            center = entity_center(world, blast_entity)
            blasts.append((center, c_b.radius))
            world.remove_component(blast_entity, CBlast)
            for enemy, c_e in world.get_component(CEnemy):
                if c_e.kind in _BLAST_KINDS and \
                        distance(center, entity_center(world, enemy), world_size) <= c_b.radius:
                    destroy_enemy(world, enemy, sprites_cfg, enemies_cfg)
        pending = world.get_component(CBlast)
    return blasts
