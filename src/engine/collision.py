"""Colision AABB en un mundo toroidal.

No se puede usar `Rect.colliderect` directamente: dos entidades pueden estar a 3 pixeles
una de otra y tener coordenadas en extremos opuestos del mundo. La prueba se hace
sobre la distancia mas corta entre centros, eje por eje.
"""
import pygame

from src.engine.world_math import signed_delta_1d


def collide_world(pos_a: pygame.Vector2, size_a: pygame.Rect,
                  pos_b: pygame.Vector2, size_b: pygame.Rect,
                  world_size: pygame.Vector2) -> bool:
    delta_x = signed_delta_1d(pos_a.x + size_a.w / 2.0, pos_b.x + size_b.w / 2.0,
                              world_size.x)
    if abs(delta_x) * 2 >= size_a.w + size_b.w:
        return False
    delta_y = signed_delta_1d(pos_a.y + size_a.h / 2.0, pos_b.y + size_b.h / 2.0,
                              world_size.y)
    return abs(delta_y) * 2 < size_a.h + size_b.h
