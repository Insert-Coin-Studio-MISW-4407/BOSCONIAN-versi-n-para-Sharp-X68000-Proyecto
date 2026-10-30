"""Matematicas del mundo toroidal.

El mundo mide `world_size` pixeles y da la vuelta en ambos ejes: el borde derecho se
pega con el izquierdo y el de abajo con el de arriba. Por eso ninguna distancia se
puede calcular con una resta simple, hay que tomar siempre el camino mas corto.
Las funciones de un eje (`*_1d`) son las del cilindro de Defender; las de vector
las aplican en x y en y.
"""
import pygame


def wrap_1d(value: float, size: float) -> float:
    """Lleva una coordenada al rango [0, size)."""
    return value % size


def signed_delta_1d(from_v: float, to_v: float, size: float) -> float:
    """Distancia con signo por el camino mas corto, en [-size/2, size/2)."""
    half = size / 2.0
    return (to_v - from_v + half) % size - half


def wrap(pos: pygame.Vector2, world_size: pygame.Vector2) -> pygame.Vector2:
    return pygame.Vector2(wrap_1d(pos.x, world_size.x), wrap_1d(pos.y, world_size.y))


def signed_delta(from_pos: pygame.Vector2, to_pos: pygame.Vector2,
                 world_size: pygame.Vector2) -> pygame.Vector2:
    """Vector mas corto de `from_pos` a `to_pos`. Lo usan la camara, la IA y el radar."""
    return pygame.Vector2(signed_delta_1d(from_pos.x, to_pos.x, world_size.x),
                          signed_delta_1d(from_pos.y, to_pos.y, world_size.y))


def distance(from_pos: pygame.Vector2, to_pos: pygame.Vector2,
             world_size: pygame.Vector2) -> float:
    return signed_delta(from_pos, to_pos, world_size).length()


def _to_screen_1d(value: float, camera_start: float, world: float, view: float,
                  sprite: float) -> float | None:
    """Se prueba tambien la copia "dando la vuelta", asi una entidad junto a la costura
    del mundo se ve bien aunque la camara este al otro lado."""
    delta = (value - camera_start) % world
    if delta > world - sprite:
        delta -= world
    if -sprite < delta < view:
        return delta
    return None


def world_to_screen(pos: pygame.Vector2, camera_topleft: pygame.Vector2,
                    world_size: pygame.Vector2, view_size: pygame.Vector2,
                    sprite_size: pygame.Vector2) -> pygame.Vector2 | None:
    """Posicion relativa a la vista, o None si la entidad no es visible."""
    x = _to_screen_1d(pos.x, camera_topleft.x, world_size.x, view_size.x, sprite_size.x)
    if x is None:
        return None
    y = _to_screen_1d(pos.y, camera_topleft.y, world_size.y, view_size.y, sprite_size.y)
    if y is None:
        return None
    return pygame.Vector2(x, y)
