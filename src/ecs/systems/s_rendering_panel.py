"""Renderizado del panel lateral siguiendo la referencia visual de Bosconian."""
import esper
import pygame

from src.ecs.components.c_alert_state import CAlertState
from src.ecs.components.c_game_stats import CGameStats
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_base import CTagBase
from src.ecs.components.tags.c_tag_formation import CTagFormation
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.engine.service_locator import ServiceLocator


def _map_position(pos: pygame.Vector2, map_rect: pygame.Rect,
                  world_size: pygame.Vector2) -> tuple[int, int]:
    """Proyecta una posicion del mundo toroidal sobre el minimapa."""
    inner = map_rect
    x_ratio = (pos.x % world_size.x) / max(1.0, world_size.x)
    y_ratio = (pos.y % world_size.y) / max(1.0, world_size.y)
    return (
        inner.left + min(inner.width - 1, int(x_ratio * inner.width)),
        inner.top + min(inner.height - 1, int(y_ratio * inner.height)),
    )


def _draw_left(screen: pygame.Surface, font, text: str, x: int, y: int,
               color: pygame.Color) -> None:
    rendered = font.render(str(text), False, color)
    screen.blit(rendered, (x, y))


def _draw_right(screen: pygame.Surface, font, text: str, right: int, y: int,
                color: pygame.Color) -> None:
    rendered = font.render(str(text), False, color)
    screen.blit(rendered, (right - rendered.get_width(), y))


def system_rendering_panel(
    world: esper.World,
    screen: pygame.Surface,
    panel_cfg: dict,
    world_size: pygame.Vector2,
    ship_texture: pygame.Surface | None = None,
) -> None:
    """Dibuja puntajes, condicion, minimapa, vidas como naves y ronda.

    Las bases y formaciones no se crean aqui: toda entidad con CTransform y
    CTagBase o CTagFormation aparece automaticamente en el radar.
    """
    panel_rect = pygame.Rect(
        panel_cfg["x"], panel_cfg["y"], panel_cfg["w"], panel_cfg["h"]
    )
    pygame.draw.rect(
        screen, pygame.Color(*panel_cfg.get("color", [0, 0, 0])), panel_rect
    )

    hud_cfg = panel_cfg.get("hud", {})
    palette = hud_cfg.get("colors", {})
    text_color = pygame.Color(palette.get("text", [255, 255, 255]))
    high_score_color = pygame.Color(palette.get("high_score", [236, 60, 38]))
    map_color = pygame.Color(palette.get("map_background", [155, 144, 251]))
    player_color = pygame.Color(palette.get("player", [98, 249, 144]))
    base_color = pygame.Color(palette.get("base", [255, 220, 0]))
    formation_color = pygame.Color(palette.get("formation", [236, 60, 38]))
    alert_colors = {
        CAlertState.GREEN: pygame.Color(palette.get("green", [98, 249, 144])),
        CAlertState.YELLOW: pygame.Color(palette.get("yellow", [255, 220, 0])),
        CAlertState.RED: pygame.Color(palette.get("red", [236, 60, 38])),
    }

    font_path = hud_cfg.get("font", "assets/fnt/PressStart2P.ttf")
    # La fuente se obtiene del servicio compartido para mantener el cache del juego.
    font = ServiceLocator.fonts_service.get(
        font_path, int(hud_cfg.get("font_size", 6))
    )
    value_font = ServiceLocator.fonts_service.get(
        font_path, int(hud_cfg.get("value_size", 7))
    )
    condition_font = ServiceLocator.fonts_service.get(
        font_path, int(hud_cfg.get("condition_size", 8))
    )

    left = panel_rect.left + int(hud_cfg.get("horizontal_margin", 5))
    right = panel_rect.right - int(hud_cfg.get("horizontal_margin", 5))
    top = panel_rect.top

    stats_items = world.get_component(CGameStats)
    stats = stats_items[0][1] if stats_items else None
    current_score = stats.score if stats else 0
    high_score = stats.high_score if stats else 0
    lives = stats.lives if stats else 0
    round_number = stats.round_number if stats else 1

    # Puntajes: etiquetas a la izquierda y valores alineados a la derecha.
    _draw_left(screen, font, "HI-SCORE", left, top + 9, high_score_color)
    _draw_right(screen, value_font, str(high_score), right, top + 16, text_color)
    _draw_left(screen, font, "1UP", left, top + 23, text_color)
    _draw_right(screen, value_font, str(current_score), right, top + 30, text_color)

    # Condicion: una franja de color con el estado escrito en negro.
    alert_items = world.get_component(CAlertState)
    condition = alert_items[0][1].condition if alert_items else CAlertState.GREEN
    condition_color = alert_colors.get(condition, alert_colors[CAlertState.GREEN])
    _draw_left(screen, font, "CONDITION", left, top + 51, text_color)

    alert_rect = pygame.Rect(
        panel_rect.left + 5, top + 62, panel_rect.width - 10, 13
    )
    pygame.draw.rect(screen, condition_color, alert_rect)
    condition_text = condition_font.render(condition, False, pygame.Color(0, 0, 0))
    screen.blit(
        condition_text,
        (alert_rect.centerx - condition_text.get_width() // 2,
         alert_rect.centery - condition_text.get_height() // 2),
    )

    # Minimap vertical: color plano, sin cuadrícula ni marco adicional.
    map_rect = pygame.Rect(
        panel_rect.left + 5, top + 79, panel_rect.width - 10, 84
    )
    pygame.draw.rect(screen, map_color, map_rect)

    # Bases (nucleo de cada estacion) y formaciones (su lider) se ubican por tags.
    for _, (transform, _) in world.get_components(CTransform, CTagBase):
        marker = _map_position(transform.pos, map_rect, world_size)
        pygame.draw.rect(screen, base_color, (*marker, 2, 2))

    for _, (transform, _) in world.get_components(CTransform, CTagFormation):
        marker = _map_position(transform.pos, map_rect, world_size)
        pygame.draw.rect(screen, formation_color, (*marker, 2, 2))

    # Jugador como pequeno marcador verde, como en la referencia.
    for _, (transform, surface, _) in world.get_components(
            CTransform, CSurface, CTagPlayer):
        player_center = transform.pos + pygame.Vector2(surface.area.size) / 2
        marker = _map_position(player_center, map_rect, world_size)
        pygame.draw.rect(screen, player_color, (*marker, 2, 2))

    # Las vidas se representan con el sprite original de la nave, no con un contador.
    if ship_texture is not None:
        visible_lives = min(max(0, lives), 3)
        ship_width = ship_texture.get_width()
        ship_x = panel_rect.left + 5
        ship_y = top + 167
        for index in range(visible_lives):
            screen.blit(
                ship_texture,
                (ship_x + index * (ship_width + 5), ship_y),
            )

    # Ronda: etiqueta a la izquierda y valor pegado al borde derecho.
    _draw_left(screen, font, "ROUND", left, top + 185, text_color)
    _draw_right(screen, value_font, str(round_number), right, top + 185, text_color)
