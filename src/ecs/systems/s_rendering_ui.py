import esper
import pygame

from src.ecs.components.c_blink import CBlink
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_ui import CTagUI


def system_rendering_ui(world: esper.World, screen: pygame.Surface) -> None:
    """Dibuja los sprites de interfaz directamente en pantalla, sin camara."""
    for entity, (c_t, c_s, _) in world.get_components(CTransform, CSurface, CTagUI):
        c_blink = world.try_component(entity, CBlink)
        if c_blink is not None and not c_blink.visible:
            continue
        screen.blit(c_s.surf, c_t.pos, area=c_s.area)
