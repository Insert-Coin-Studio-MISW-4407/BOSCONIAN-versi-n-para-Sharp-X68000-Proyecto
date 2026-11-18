"""Impactos sobre enemigos: balas del jugador, ondas de las minas y destruccion."""
import esper
import pygame

from src.create.prefab_creator import create_explosion
from src.ecs.components.c_base import CBase
from src.ecs.components.c_base_cannon import CBaseCannon
from src.ecs.components.c_base_core import CBaseCore
from src.ecs.components.c_blast import CBlast
from src.ecs.components.c_enemy import CEnemy
from src.ecs.components.c_formation import CFormationLeader, CFormationMember
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_player_bullet import CTagPlayerBullet
from src.ecs.systems.s_game_stats import system_add_score
from src.engine.collision import collide_world
from src.engine.service_locator import ServiceLocator
from src.engine.services.sound_service import SOUND_EXPLOSION
from src.engine.world_math import distance

# Lo que una onda expansiva puede destruir (las piezas de las estaciones la resisten)
_BLAST_KINDS = ("asteroid", "mine", "ship")


def entity_center(world: esper.World, entity: int) -> pygame.Vector2:
    c_t = world.component_for_entity(entity, CTransform)
    c_s = world.component_for_entity(entity, CSurface)
    return c_t.pos + pygame.Vector2(c_s.area.size) / 2


def is_vulnerable(world: esper.World, entity: int) -> bool:
    """El nucleo de una estacion solo se puede destruir mientras esta abierto."""
    c_core = world.try_component(entity, CBaseCore)
    return c_core is None or c_core.is_open


def destroy_base(world: esper.World, core: int, sprites_cfg: dict, enemies_cfg: dict) -> None:
    """La estacion entera explota: nucleo, canones (vivos o no) y estructura."""
    c_base = world.component_for_entity(core, CBase)
    for part in c_base.cannons + [core]:
        create_explosion(world, sprites_cfg, enemies_cfg, entity_center(world, part))
        if world.has_component(part, CEnemy):
            world.remove_component(part, CEnemy)
        world.delete_entity(part)
    world.delete_entity(c_base.frame)
    system_add_score(world, c_base.points)
    world.remove_component(core, CBase)


def _destroy_cannon(world: esper.World, cannon: int, sprites_cfg: dict,
                    enemies_cfg: dict) -> None:
    """El canon queda como chatarra; si era el ultimo, explota toda la estacion."""
    c_e = world.component_for_entity(cannon, CEnemy)
    c_c = world.component_for_entity(cannon, CBaseCannon)
    create_explosion(world, sprites_cfg, enemies_cfg, entity_center(world, cannon))
    system_add_score(world, c_e.points)
    c_s = world.component_for_entity(cannon, CSurface)
    c_s.surf = c_c.destroyed
    c_s.area = c_s.surf.get_rect()
    world.remove_component(cannon, CEnemy)
    world.remove_component(cannon, CBaseCannon)

    c_base = world.try_component(c_c.base_entity, CBase)
    if c_base is None:
        return
    c_base.alive_cannons -= 1
    if c_base.alive_cannons <= 0:
        destroy_base(world, c_c.base_entity, sprites_cfg, enemies_cfg)


def destroy_enemy(world: esper.World, entity: int, sprites_cfg: dict,
                  enemies_cfg: dict) -> None:
    """Borra el enemigo, deja su explosion y suma sus puntos.

    Las minas dejan ademas una onda expansiva (CBlast) que se resuelve en
    system_blast el mismo frame. Las piezas de las estaciones tienen reglas propias.
    """
    c_e = world.component_for_entity(entity, CEnemy)
    ServiceLocator.sounds_service.play(SOUND_EXPLOSION)
    if c_e.kind == "cannon":
        _destroy_cannon(world, entity, sprites_cfg, enemies_cfg)
        return
    if c_e.kind == "core":
        destroy_base(world, entity, sprites_cfg, enemies_cfg)
        return
    # Derribar al lider mientras conserva escoltas da un bonus (y rompe la formacion)
    c_leader = world.try_component(entity, CFormationLeader)
    if c_leader is not None and any(world.entity_exists(member) and
                                    world.has_component(member, CFormationMember)
                                    for member in c_leader.members):
        system_add_score(world, c_leader.bonus)
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
                # Un nucleo cerrado absorbe la bala sin danarse
                world.delete_entity(bullet)
                if is_vulnerable(world, enemy):
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
