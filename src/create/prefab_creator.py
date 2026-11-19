"""Fabrica de entidades.

Es el unico lugar que sabe que componentes forman cada tipo de entidad del juego, y
toma todos los numeros de los archivos de configuracion. Las texturas se piden al
Service Locator, nunca se cargan aqui.
"""
from __future__ import annotations

import math
import random

import esper
import pygame

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_base import CBase
from src.ecs.components.c_base_cannon import CBaseCannon
from src.ecs.components.c_base_core import CBaseCore
from src.ecs.components.c_blink import CBlink
from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_chaser import CChaser
from src.ecs.components.c_enemy import CEnemy
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_formation import CFormationLeader, CFormationMember
from src.ecs.components.c_heading import CHeading
from src.ecs.components.c_alert_state import CAlertState
from src.ecs.components.c_game_stats import CGameStats
from src.ecs.components.c_stage_timer import CStageTimer
from src.ecs.components.c_input_command import CInputCommand, InputDevice
from src.ecs.components.c_lifetime import CLifetime
from src.ecs.components.c_rotating_sprite import CRotatingSprite
from src.ecs.components.c_spy import CSpy
from src.ecs.components.c_ship_motion import CShipMotion
from src.ecs.components.c_star import CStar
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_text import CText
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_weapon import CWeapon
from src.ecs.components.tags.c_tag_base import CTagBase
from src.ecs.components.tags.c_tag_enemy_bullet import CTagEnemyBullet
from src.ecs.components.tags.c_tag_formation import CTagFormation
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_player_bullet import CTagPlayerBullet
from src.ecs.components.tags.c_tag_special_bullet import CTagSpecialBullet
from src.ecs.components.tags.c_tag_ui import CTagUI
from src.engine.service_locator import ServiceLocator
from src.engine.world_math import distance

# Capas de dibujo (CSurface.layer): la estructura de las estaciones va al fondo y las
# explosiones encima de todo.
_LAYER_STRUCTURE = -1
_LAYER_EFFECTS = 2


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


def sprite_frames(sprites_cfg: dict, name: str, flip_x: bool = False) -> list[pygame.Surface]:
    """Cuadros de una animacion de sprites.json (o el recorte unico como un solo cuadro)."""
    sprite = sprites_cfg["sprites"][name]
    rects = sprite.get("frames", [sprite.get("rect")])
    return [ServiceLocator.textures_service.get_region(sprites_cfg["sheet"], rect, flip_x=flip_x)
            for rect in rects]


def create_centered_sprite(world: esper.World, center: pygame.Vector2, vel: pygame.Vector2,
                           texture: pygame.Surface, layer: int = 0) -> int:
    """Como create_sprite, pero recibe el CENTRO de la entidad (asi se ubican los enemigos)."""
    topleft = pygame.Vector2(center) - pygame.Vector2(texture.get_size()) / 2
    entity = create_sprite(world, topleft, vel, texture)
    world.component_for_entity(entity, CSurface).layer = layer
    return entity


def create_animated(world: esper.World, center: pygame.Vector2, frames: list[pygame.Surface],
                    frame_time: float, loop: bool = True, delete_on_end: bool = False,
                    layer: int = 0) -> int:
    entity = create_centered_sprite(world, center, pygame.Vector2(0, 0), frames[0], layer)
    world.add_component(entity, CAnimation(frames, frame_time, loop, delete_on_end))
    return entity


def create_explosion(world: esper.World, sprites_cfg: dict, enemies_cfg: dict,
                     center: pygame.Vector2, kind: str = "enemy") -> int:
    """Explosion que se reproduce una vez y desaparece. `kind` elige la paleta del atlas
    (naranja para naves y estaciones, amarilla para asteroides y minas)."""
    explosions = enemies_cfg["explosions"]
    return create_animated(world, center, sprite_frames(sprites_cfg, explosions[kind]),
                           explosions["frame_time"], loop=False, delete_on_end=True,
                           layer=_LAYER_EFFECTS)


# ---------------------------------------------------------------------- enemigos
def create_asteroid(world: esper.World, sprites_cfg: dict, enemies_cfg: dict,
                    center: pygame.Vector2) -> int:
    """Asteroide fijo: obstaculo que se destruye de un disparo."""
    cfg = enemies_cfg["asteroid"]
    texture = sprite_texture(sprites_cfg, random.choice(cfg["sprites"]))
    entity = create_centered_sprite(world, center, pygame.Vector2(0, 0), texture)
    world.add_component(entity, CEnemy("asteroid", cfg["points"], "obstacle"))
    return entity


def create_mine(world: esper.World, sprites_cfg: dict, enemies_cfg: dict,
                center: pygame.Vector2) -> int:
    """Mina cosmica: parpadea y al destruirse deja una onda que arrasa lo que la rodea."""
    cfg = enemies_cfg["mine"]
    entity = create_animated(world, center, sprite_frames(sprites_cfg, cfg["sprite"]),
                             cfg["frame_time"])
    # Cada mina arranca en un momento distinto del parpadeo
    world.component_for_entity(entity, CAnimation).timer = random.uniform(0, cfg["frame_time"])
    world.add_component(entity, CEnemy("mine", cfg["points"], "obstacle"))
    return entity


def _base_frame_texture(sprites_cfg: dict, base_cfg: dict) -> pygame.Surface:
    """Estructura de la estacion sacada de la ilustracion completa del atlas.

    Se vacian los circulos de los canones y del nucleo: esas piezas son entidades
    propias que se animan y se destruyen por separado.
    """
    sprite = sprites_cfg["sprites"][base_cfg["frame"]]
    center_x, center_y = base_cfg["frame_center"]
    holes = [(center_x + dx, center_y + dy, base_cfg["cannon_radius"])
             for dx, dy in base_cfg["cannon_offsets"]]
    holes.append((center_x, center_y, base_cfg["core_radius"]))
    return ServiceLocator.textures_service.get_keyed_region(
        sprites_cfg["sheet"], sprite["rect"], sprite["colorkey"], tuple(holes))


def create_base(world: esper.World, sprites_cfg: dict, enemies_cfg: dict,
                center: pygame.Vector2) -> int:
    """Estacion enemiga: estructura + nucleo + seis canones. Devuelve la entidad del nucleo.

    Se destruye al acabar con los seis canones o con un disparo al nucleo abierto.
    """
    cfg = enemies_cfg["base"]
    center = pygame.Vector2(center)
    frame = create_centered_sprite(world, center, pygame.Vector2(0, 0),
                                   _base_frame_texture(sprites_cfg, cfg), _LAYER_STRUCTURE)

    core_frames = sprite_frames(sprites_cfg, cfg["core"])
    core = create_centered_sprite(world, center, pygame.Vector2(0, 0), core_frames[-1])
    world.add_component(core, CEnemy("core", 0))
    # Cada estacion arranca su ciclo en un momento distinto
    world.add_component(core, CBaseCore(core, core_frames, cfg["core_frame_time"],
                                        cfg["core_open_time"], cfg["core_closed_time"],
                                        random.uniform(0, cfg["core_closed_time"])))
    world.add_component(core, CTagBase())

    destroyed = sprite_texture(sprites_cfg, cfg["cannon_destroyed"])
    cannons = []
    for dx, dy in cfg["cannon_offsets"]:
        # Los canones de la derecha son los de la izquierda en espejo
        frames = sprite_frames(sprites_cfg, cfg["cannon"], flip_x=dx > 0)
        cannon = create_centered_sprite(world, center + pygame.Vector2(dx, dy),
                                        pygame.Vector2(0, 0), frames[0])
        world.add_component(cannon, CEnemy("cannon", cfg["cannon_points"]))
        world.add_component(cannon, CBaseCannon(core, frames, destroyed,
                                                random.uniform(*cfg["fire"]["cooldown"])))
        cannons.append(cannon)

    world.add_component(core, CBase(frame, cannons, cfg["base_points"]))
    return core


def create_enemy_ship(world: esper.World, sprites_cfg: dict, enemies_cfg: dict, kind: str,
                      center: pygame.Vector2, target: pygame.Vector2) -> int:
    """Nave enemiga (tipos I, P, E de enemies.json) que sale rumbo a `target`."""
    cfg = enemies_cfg["ships"][kind]
    sprite = sprites_cfg["sprites"][cfg["sprite"]]
    direction = pygame.Vector2(target) - pygame.Vector2(center)
    if direction.length_squared() == 0:
        direction = pygame.Vector2(0, -1)
    direction.scale_to_length(cfg["speed"])
    entity = create_centered_sprite(world, center, direction,
                                    sprite_texture(sprites_cfg, cfg["sprite"]), layer=1)
    world.add_component(entity, CEnemy("ship", cfg["points"]))
    world.add_component(entity, CChaser(cfg["speed"], cfg["turn_rate"]))
    world.add_component(entity, CHeading(direction.normalize()))
    world.add_component(entity, CRotatingSprite(sprites_cfg["sheet"], sprite["rect"]))
    return entity


def create_formation(world: esper.World, sprites_cfg: dict, enemies_cfg: dict,
                     center: pygame.Vector2, target: pygame.Vector2) -> int:
    """Formacion: un lider y sus escoltas en V. El lider lleva CTagFormation (radar)."""
    cfg = enemies_cfg["formation"]
    leader = create_enemy_ship(world, sprites_cfg, enemies_cfg, cfg["leader"], center, target)
    c_chaser = world.component_for_entity(leader, CChaser)
    c_chaser.speed = cfg["speed"]
    c_chaser.turn_rate = cfg["turn_rate"]
    world.component_for_entity(leader, CVelocity).vel.scale_to_length(cfg["speed"])
    world.component_for_entity(leader, CEnemy).points = cfg["leader_points"]
    world.add_component(leader, CTagFormation())

    member_cfg = enemies_cfg["ships"][cfg["member"]]
    members = []
    for offset in cfg["offsets"]:
        member = create_enemy_ship(world, sprites_cfg, enemies_cfg, cfg["member"], center, target)
        # La escolta no persigue por su cuenta mientras el lider viva
        world.remove_component(member, CChaser)
        world.component_for_entity(member, CVelocity).vel = pygame.Vector2(0, 0)
        world.add_component(member, CFormationMember(leader, vec({"x": offset[0], "y": offset[1]}),
                                                     member_cfg["speed"], member_cfg["turn_rate"]))
        members.append(member)
    world.add_component(leader, CFormationLeader(members, cfg["leader_bonus"]))
    return leader


def create_enemy_spawner(world: esper.World, enemies_cfg: dict) -> int:
    entity = world.create_entity()
    world.add_component(entity, CEnemySpawner(enemies_cfg["spawner"]["first_delay"],
                                              enemies_cfg["spy"]["first_delay"]))
    return entity


def create_spy(world: esper.World, sprites_cfg: dict, enemies_cfg: dict,
               center: pygame.Vector2, target: pygame.Vector2) -> int:
    """Nave espia: no ataca; si consigue escapar tras observar la nave, activa RED."""
    cfg = enemies_cfg["spy"]
    sprite = sprites_cfg["sprites"][cfg["sprite"]]
    direction = pygame.Vector2(target) - pygame.Vector2(center)
    if direction.length_squared() == 0:
        direction = pygame.Vector2(0, -1)
    direction.scale_to_length(cfg["speed"])
    entity = create_centered_sprite(world, center, direction,
                                    sprite_texture(sprites_cfg, cfg["sprite"]), layer=1)
    world.add_component(entity, CEnemy("ship", cfg["points"]))
    world.add_component(entity, CSpy(cfg))
    world.add_component(entity, CHeading(direction.normalize()))
    world.add_component(entity, CRotatingSprite(sprites_cfg["sheet"], sprite["rect"]))
    return entity


def create_enemy_bullet(world: esper.World, sprites_cfg: dict, enemies_cfg: dict,
                        center: pygame.Vector2, direction: pygame.Vector2) -> int:
    """Bala enemiga: sale de `center` hacia `direction` y vive unos segundos."""
    cfg = enemies_cfg["enemy_bullet"]
    direction = pygame.Vector2(direction).normalize()
    texture = _bullet_texture(sprites_cfg, cfg, direction, cfg["tint"])
    entity = create_centered_sprite(world, center, direction * cfg["speed"], texture, layer=1)
    world.add_component(entity, CTagEnemyBullet())
    world.add_component(entity, CLifetime(cfg["lifetime"]))
    return entity


def create_bases(world: esper.World, sprites_cfg: dict, enemies_cfg: dict,
                 bases_cfg: list[dict], occupied: list[tuple[pygame.Vector2, float]]) -> None:
    """Estaciones del nivel en las posiciones fijas de level_XX.json."""
    radius = enemies_cfg["base"]["clearance_radius"]
    for base_cfg in bases_cfg:
        center = vec(base_cfg)
        create_base(world, sprites_cfg, enemies_cfg, center)
        occupied.append((center, radius))


def free_position(world_size: pygame.Vector2, occupied: list[tuple[pygame.Vector2, float]],
                  radius: float, attempts: int = 200) -> pygame.Vector2 | None:
    """Posicion al azar en el mundo que no pisa nada de `occupied` (centro, radio).

    La distancia se mide por el camino mas corto del toro. Devuelve None si no hay sitio.
    """
    for _ in range(attempts):
        pos = pygame.Vector2(random.uniform(0, world_size.x), random.uniform(0, world_size.y))
        if all(distance(pos, other, world_size) >= radius + other_radius
               for other, other_radius in occupied):
            return pos
    return None


def create_obstacles(world: esper.World, sprites_cfg: dict, enemies_cfg: dict,
                     obstacles_cfg: dict, world_size: pygame.Vector2,
                     occupied: list[tuple[pygame.Vector2, float]]) -> None:
    """Reparte asteroides y minas por el mundo sin pisarse entre si ni lo ya ocupado.

    `occupied` se amplia con cada obstaculo creado.
    """
    spacing = obstacles_cfg["min_spacing"] / 2
    for count, create in ((obstacles_cfg["asteroids"], create_asteroid),
                          (obstacles_cfg["mines"], create_mine)):
        for _ in range(count):
            pos = free_position(world_size, occupied, spacing)
            if pos is None:
                return
            create(world, sprites_cfg, enemies_cfg, pos)
            occupied.append((pos, spacing))


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


def _bullet_texture(sprites_cfg: dict, fire_cfg: dict, direction: pygame.Vector2,
                    tint: tuple | None = None) -> pygame.Surface:
    """Sprite de la bala segun su direccion: vertical, horizontal o diagonal (en espejo).

    El atlas solo trae la diagonal "/", asi que la "\\" es esa misma imagen en espejo.
    `tint` tine la bala (las enemigas usan las mismas imagenes en otro color).
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
        sprites_cfg["sheet"], sprites_cfg["sprites"][name]["rect"], flip_x=flip,
        tint=tuple(tint) if tint else None)


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
