import math

import esper
import pygame

from src.ecs.components.c_heading import CHeading
from src.ecs.components.c_rotating_sprite import CRotatingSprite
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.engine.service_locator import ServiceLocator


def heading_angle(direction: pygame.Vector2) -> float:
    """Angulo (grados, antihorario) para girar un sprite que mira hacia arriba."""
    return math.degrees(math.atan2(-direction.x, -direction.y))


def system_player_sprite(world: esper.World) -> None:
    """Gira el sprite de la nave hacia donde apunta, sin mover su centro."""
    c_h: CHeading
    c_r: CRotatingSprite
    c_s: CSurface
    c_t: CTransform
    for _, (c_h, c_r, c_s, c_t) in world.get_components(CHeading, CRotatingSprite, CSurface,
                                                         CTransform):
        angle = round(heading_angle(c_h.direction))
        if angle == c_r.angle:
            continue
        old_size = pygame.Vector2(c_s.area.size)
        c_s.surf = ServiceLocator.textures_service.get_region(c_r.sheet, c_r.rect, angle=angle)
        c_s.area = c_s.surf.get_rect()
        # El sprite girado tiene otro tamano: se corrige la esquina para que el centro quede igual
        c_t.pos += (old_size - pygame.Vector2(c_s.area.size)) / 2
        c_r.angle = angle
