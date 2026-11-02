import esper
import pygame

from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.engine.world_math import signed_delta, wrap


def system_camera(world: esper.World, target_entity: int,
                  world_size: pygame.Vector2) -> None:
    """Centra la camara en el objetivo (la nave) y guarda cuanto se movio."""
    c_t = world.component_for_entity(target_entity, CTransform)
    c_s = world.component_for_entity(target_entity, CSurface)
    center = c_t.pos + pygame.Vector2(c_s.area.size) / 2
    for _, c_cam in world.get_component(CCamera):
        new_topleft = wrap(center - pygame.Vector2(c_cam.view.size) / 2, world_size)
        c_cam.delta = signed_delta(c_cam.topleft, new_topleft, world_size)
        c_cam.topleft = new_topleft
