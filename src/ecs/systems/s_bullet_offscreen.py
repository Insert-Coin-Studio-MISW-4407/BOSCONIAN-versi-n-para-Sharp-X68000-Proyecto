import esper
import pygame

from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_player_bullet import CTagPlayerBullet
from src.engine.world_math import world_to_screen


def system_bullet_offscreen(world: esper.World, c_cam: CCamera,
                            world_size: pygame.Vector2) -> None:
    """Las balas desaparecen al salir por completo de la pantalla, como en el original.

    Se usa `world_to_screen`, que entiende la costura del mundo: una bala que cruza el borde
    del mundo sigue viva mientras se vea.
    """
    view_size = pygame.Vector2(c_cam.view.size)
    c_t: CTransform
    c_s: CSurface
    for entity, (c_t, c_s, _) in world.get_components(CTransform, CSurface, CTagPlayerBullet):
        if world_to_screen(c_t.pos, c_cam.topleft, world_size, view_size,
                           pygame.Vector2(c_s.area.size)) is None:
            world.delete_entity(entity)
