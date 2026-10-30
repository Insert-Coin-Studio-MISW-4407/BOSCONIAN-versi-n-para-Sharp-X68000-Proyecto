import esper
import pygame

from src.ecs.components.c_blink import CBlink
from src.ecs.components.c_text import CText
from src.engine.service_locator import ServiceLocator


def system_rendering_text(world: esper.World, screen: pygame.Surface) -> None:
    """Dibuja los textos de menus y HUD pidiendo las fuentes al Service Locator."""
    for entity, c_text in world.get_component(CText):
        c_blink = world.try_component(entity, CBlink)
        if c_blink is not None and not c_blink.visible:
            continue
        font = ServiceLocator.fonts_service.get(c_text.font_path, c_text.size)
        surface = font.render(c_text.text, False, c_text.color)
        rect = surface.get_rect()
        pos = (int(c_text.pos.x), int(c_text.pos.y))
        if c_text.align == "center":
            rect.midtop = pos
        elif c_text.align == "right":
            rect.topright = pos
        else:
            rect.topleft = pos
        screen.blit(surface, rect)
