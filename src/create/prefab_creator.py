"""Fabrica de entidades.

Es el unico lugar que sabe que componentes forman cada tipo de entidad del juego, y
toma todos los numeros de los archivos de configuracion. Las texturas se piden al
Service Locator, nunca se cargan aqui.
"""
import esper
import pygame

from src.ecs.components.c_blink import CBlink
from src.ecs.components.c_input_command import CInputCommand, InputDevice
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_text import CText
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
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


def _add_optional_blink(world: esper.World, entity: int, cfg: dict) -> None:
    if "blink" in cfg:
        world.add_component(entity, CBlink(cfg["blink"]))


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
