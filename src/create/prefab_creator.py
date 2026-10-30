"""Fabrica de entidades.

Es el unico lugar que sabe que componentes forman cada tipo de entidad del juego, y
toma todos los numeros de los archivos de configuracion. Las texturas se piden al
Service Locator, nunca se cargan aqui.
"""
import random

import esper
import pygame

from src.ecs.components.c_blink import CBlink
from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_input_command import CInputCommand, InputDevice
from src.ecs.components.c_star import CStar
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_text import CText
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_ui import CTagUI
from src.engine.service_locator import ServiceLocator


def vec(cfg: dict) -> pygame.Vector2:
    return pygame.Vector2(cfg["x"], cfg["y"])


def color(cfg) -> pygame.Color:
    if isinstance(cfg, dict):
        return pygame.Color(cfg["r"], cfg["g"], cfg["b"])
    return pygame.Color(*cfg)


def create_sprite(world: esper.World, pos: pygame.Vector2, vel: pygame.Vector2,
                  texture: pygame.Surface) -> int:
    entity = world.create_entity()
    world.add_component(entity, CTransform(pos))
    world.add_component(entity, CVelocity(vel))
    world.add_component(entity, CSurface(texture))
    return entity


def sprite_texture(sprites_cfg: dict, name: str) -> pygame.Surface:
    """Recorte de la hoja de sprites declarado en sprites.json."""
    return ServiceLocator.textures_service.get_region(
        sprites_cfg["sheet"], sprites_cfg["sprites"][name]["rect"])


def _add_optional_blink(world: esper.World, entity: int, cfg: dict) -> None:
    if "blink" in cfg:
        world.add_component(entity, CBlink(cfg["blink"]))


# ------------------------------------------------------------------------ mundo
def create_camera(world: esper.World, view_cfg: dict) -> int:
    entity = world.create_entity()
    world.add_component(entity, CCamera(pygame.Rect(view_cfg["x"], view_cfg["y"],
                                                    view_cfg["w"], view_cfg["h"])))
    return entity


def create_starfield(world: esper.World, stars_cfg: dict, view: pygame.Rect) -> None:
    """Una entidad por estrella, repartidas al azar en capas de parallax."""
    colors = [color(c) for c in stars_cfg["colors"]]
    blink = stars_cfg["blink_interval"]
    for layer in stars_cfg["layers"]:
        for _ in range(layer["count"]):
            entity = world.create_entity()
            pos = pygame.Vector2(random.uniform(0, view.w), random.uniform(0, view.h))
            world.add_component(entity, CStar(pos, random.choice(colors),
                                              layer["parallax"],
                                              random.uniform(blink["min"], blink["max"])))


def create_player(world: esper.World, player_cfg: dict, sprites_cfg: dict,
                  pos: pygame.Vector2) -> int:
    texture = sprite_texture(sprites_cfg, player_cfg["sprite"])
    # La posicion de spawn es el centro de la nave
    topleft = pygame.Vector2(pos) - pygame.Vector2(texture.get_size()) / 2
    entity = create_sprite(world, topleft, pygame.Vector2(0, 0), texture)
    world.add_component(entity, CTagPlayer())
    return entity


# --------------------------------------------------------------------- interfaz
def create_text(world: esper.World, text_cfg: dict, text: str | None = None) -> int:
    entity = world.create_entity()
    world.add_component(entity, CText(
        text if text is not None else text_cfg.get("text", ""),
        text_cfg["font"], text_cfg["size"], color(text_cfg["color"]),
        vec(text_cfg["pos"]), text_cfg.get("align", "left")))
    _add_optional_blink(world, entity, text_cfg)
    return entity


def create_ui_image(world: esper.World, image_cfg: dict) -> int:
    """Imagen fija en pantalla. Con align "center", `pos.x` es el centro horizontal."""
    texture = ServiceLocator.textures_service.get(image_cfg["path"])
    pos = vec(image_cfg["pos"])
    if image_cfg.get("align") == "center":
        pos.x -= texture.get_width() // 2
    entity = world.create_entity()
    world.add_component(entity, CTransform(pos))
    world.add_component(entity, CSurface(texture))
    world.add_component(entity, CTagUI())
    _add_optional_blink(world, entity, image_cfg)
    return entity


# ------------------------------------------------------------------------ input
def create_input_player(world: esper.World, input_cfg: dict) -> None:
    """Crea una entidad por cada binding declarado en input.json (patron Command)."""
    for action in input_cfg["actions"]:
        device = InputDevice[action["device"]]
        if device == InputDevice.KEYBOARD:
            codes = [pygame.key.key_code(name) for name in action["keys"]]
        else:
            codes = action["buttons"]
        for code in codes:
            entity = world.create_entity()
            world.add_component(entity, CInputCommand(action["name"], code, device))
