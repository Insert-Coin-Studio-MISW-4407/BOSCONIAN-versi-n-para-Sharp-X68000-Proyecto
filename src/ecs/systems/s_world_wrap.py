import esper
import pygame

from src.ecs.components.c_transform import CTransform
from src.engine.world_math import wrap_1d


def system_world_wrap(world: esper.World, world_size: pygame.Vector2) -> None:
    """Normaliza la posicion de TODAS las entidades al rango del mundo.

    Gracias a esto el mundo es un toro: salir por un borde equivale a entrar por el
    opuesto, en horizontal y en vertical, sin casos especiales en otros sistemas.
    """
    for _, c_t in world.get_component(CTransform):
        c_t.pos.x = wrap_1d(c_t.pos.x, world_size.x)
        c_t.pos.y = wrap_1d(c_t.pos.y, world_size.y)
