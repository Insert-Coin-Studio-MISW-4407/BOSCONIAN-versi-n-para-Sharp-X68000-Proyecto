"""Fabrica de entidades.

Es el unico lugar que sabe que componentes forman cada tipo de entidad del juego, y
toma todos los numeros de los archivos de configuracion. Las texturas se piden al
Service Locator, nunca se cargan aqui.
"""
import math
import random

import esper
import pygame

from src.ecs.components.c_blink import CBlink
from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_heading import CHeading
from src.ecs.components.c_alert_state import CAlertState
from src.ecs.components.c_game_stats import CGameStats
from src.ecs.components.c_stage_timer import CStageTimer
from src.ecs.components.c_input_command import CInputCommand, InputDevice
from src.ecs.components.c_rotating_sprite import CRotatingSprite
from src.ecs.components.c_ship_motion import CShipMotion
from src.ecs.components.c_star import CStar
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_text import CText
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_weapon import CWeapon
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_player_bullet import CTagPlayerBullet
from src.ecs.components.tags.c_tag_special_bullet import CTagSpecialBullet
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
    world.add_component(entity, CHeading())
    world.add_component(entity, CShipMotion(player_cfg["max_speed"], player_cfg["acceleration"],
                                            player_cfg["cruise_speed"]))
    world.add_component(entity, CWeapon(player_cfg["fire"]))
    world.add_component(entity, CRotatingSprite(sprites_cfg["sheet"],
                                                sprites_cfg["sprites"][player_cfg["sprite"]]["rect"]))
    return entity


def _bullet_texture(sprites_cfg: dict, fire_cfg: dict, direction: pygame.Vector2) -> pygame.Surface:
    """Sprite de la bala segun su direccion: vertical, horizontal o diagonal (en espejo).

    El atlas solo trae la diagonal "/", asi que la "\\" es esa misma imagen en espejo.
    """
    octant = round(math.degrees(math.atan2(direction.y, direction.x)) / 45) % 8
    names = fire_cfg["bullet_sprites"]
    if octant in (2, 6):
        name, flip = names["vertical"], False
    elif octant in (0, 4):
        name, flip = names["horizontal"], False
    else:
        name, flip = names["diagonal"], octant in (1, 5)
    return ServiceLocator.textures_service.get_region(
        sprites_cfg["sheet"], sprites_cfg["sprites"][name]["rect"], flip_x=flip)


def create_bullet(world: esper.World, sprites_cfg: dict, player_cfg: dict, center: pygame.Vector2,
                  direction: pygame.Vector2, special: bool = False) -> int:
    """Una bala que sale de `center` (centro de la nave) hacia `direction`."""
    fire_cfg = player_cfg["fire"]
    direction = pygame.Vector2(direction).normalize()
    texture = _bullet_texture(sprites_cfg, fire_cfg, direction)
    muzzle = center + direction * fire_cfg["muzzle_offset"]
    topleft = muzzle - pygame.Vector2(texture.get_size()) / 2
    entity = create_sprite(world, topleft, direction * fire_cfg["bullet_speed"], texture)
    world.add_component(entity, CTagPlayerBullet())
    if special:
        world.add_component(entity, CTagSpecialBullet())
    return entity


def create_player_shot(world: esper.World, sprites_cfg: dict, player_cfg: dict,
                       center: pygame.Vector2, heading: pygame.Vector2) -> None:
    """Disparo simple: dos balas a la vez, una hacia adelante y otra hacia atras."""
    create_bullet(world, sprites_cfg, player_cfg, center, heading)
    create_bullet(world, sprites_cfg, player_cfg, center, -heading)


def create_triple_shot(world: esper.World, sprites_cfg: dict, player_cfg: dict,
                       center: pygame.Vector2, heading: pygame.Vector2) -> None:
    """Cañon triple: tres balas al frente en abanico y una bala trasera."""
    spread = player_cfg["fire"]["triple_spread"]
    for angle in (-spread, 0, spread):
        create_bullet(world, sprites_cfg, player_cfg, center, heading.rotate(angle), special=True)
    create_bullet(world, sprites_cfg, player_cfg, center, -heading, special=True)


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


# --------------------------------------------------------------- estado de partida
def create_game_stats(world: esper.World, high_score: int, lives: int,
                      round_number: int, high_score_path: str) -> int:
    """Crea el estado ECS que alimenta el puntaje, el record y las vidas."""
    entity = world.create_entity()
    world.add_component(
        entity, CGameStats(high_score, lives, round_number, high_score_path))
    return entity


def create_stage_timer(world: esper.World, duration: float) -> int:
    """Crea el temporizador global de la ronda."""
    entity = world.create_entity()
    world.add_component(entity, CStageTimer(duration))
    return entity


def create_alert_state(world: esper.World) -> int:
    """Crea el estado GREEN/YELLOW/RED consumido por el panel."""
    entity = world.create_entity()
    world.add_component(entity, CAlertState())
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
