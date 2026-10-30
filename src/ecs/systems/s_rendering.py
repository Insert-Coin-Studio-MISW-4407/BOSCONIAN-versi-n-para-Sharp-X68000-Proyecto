import esper
import pygame

from src.ecs.components.c_blink import CBlink
from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_ui import CTagUI
from src.engine.world_math import world_to_screen


def system_rendering(world: esper.World, screen: pygame.Surface, c_cam: CCamera,
                     world_size: pygame.Vector2) -> None:
    """Dibuja los sprites convirtiendo coordenadas de mundo a coordenadas de pantalla.

    El recorte a la vista evita que una nave se dibuje encima del panel lateral.
    """
    view_size = pygame.Vector2(c_cam.view.size)
    screen.set_clip(c_cam.view)
    for entity, (c_t, c_s) in world.get_components(CTransform, CSurface):
        if world.has_component(entity, CTagUI):
            continue
        c_blink = world.try_component(entity, CBlink)
        if c_blink is not None and not c_blink.visible:
            continue
        screen_pos = world_to_screen(c_t.pos, c_cam.topleft, world_size, view_size,
                                     pygame.Vector2(c_s.area.size))
        if screen_pos is None:
            continue
        screen.blit(c_s.surf, screen_pos + c_cam.view.topleft, area=c_s.area)
    screen.set_clip(None)
