import esper
import pygame

from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_star import CStar


def system_rendering_stars(world: esper.World, screen: pygame.Surface,
                           c_cam: CCamera) -> None:
    for _, c_star in world.get_component(CStar):
        if c_star.visible:
            screen.set_at((c_cam.view.x + int(c_star.pos.x),
                           c_cam.view.y + int(c_star.pos.y)), c_star.color)
