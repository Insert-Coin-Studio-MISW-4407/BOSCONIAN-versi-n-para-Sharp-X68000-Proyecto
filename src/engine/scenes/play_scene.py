"""Escena de juego: el mundo toroidal, la camara, el fondo de estrellas y la nave."""
import pygame

from src.create.prefab_creator import (create_alert_state, create_bases, create_camera,
                                       create_game_stats,
                                       create_obstacles, create_player, create_player_shot,
                                       create_stage_timer, create_starfield, create_text,
                                       create_triple_shot, sprite_texture, vec)
from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_heading import CHeading
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_ship_motion import CShipMotion
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_weapon import CWeapon
from src.ecs.components.tags.c_tag_player_bullet import CTagPlayerBullet
from src.ecs.components.tags.c_tag_special_bullet import CTagSpecialBullet
from src.ecs.systems.s_alert import system_alert
from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_base_core import system_base_core
from src.ecs.systems.s_bullet_offscreen import system_bullet_offscreen
from src.ecs.systems.s_camera import system_camera
from src.ecs.systems.s_enemy_hits import system_blast, system_bullet_hits
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_player_sprite import system_player_sprite
from src.ecs.systems.s_game_stats import load_high_score
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_rendering_panel import system_rendering_panel
from src.ecs.systems.s_rendering_stars import system_rendering_stars
from src.ecs.systems.s_ship_motion import system_ship_motion
from src.ecs.systems.s_stage_timer import system_stage_timer
from src.ecs.systems.s_stars import system_stars
from src.ecs.systems.s_world_wrap import system_world_wrap
from src.engine.scenes.scene import Scene
from src.engine.world_math import world_to_screen

# Direccion en la que cada accion de movimiento empuja a la nave
_MOVE_ACTIONS = {
    "PLAYER_LEFT": pygame.Vector2(-1, 0),
    "PLAYER_RIGHT": pygame.Vector2(1, 0),
    "PLAYER_UP": pygame.Vector2(0, -1),
    "PLAYER_DOWN": pygame.Vector2(0, 1),
}


class PlayScene(Scene):
    def __init__(self, engine, scene_cfg: dict) -> None:
        super().__init__(engine, scene_cfg)
        self._level_cfg = engine.load_cfg(scene_cfg["level"])
        self._paused = False
        self._pause_text: int | None = None
        self._debug = False
        self._main_weapon_is_triple = False

    # --------------------------------------------------------------------- creacion
    def do_create(self) -> None:
        engine = self.engine
        world_cfg = engine.world_cfg
        self._world_size = pygame.Vector2(world_cfg["size"]["w"], world_cfg["size"]["h"])
        layout = engine.window_cfg["layout"]

        camera_entity = create_camera(self.ecs_world, layout["view"])
        self._c_camera = self.ecs_world.component_for_entity(camera_entity, CCamera)
        create_starfield(self.ecs_world, world_cfg["stars"], self._c_camera.view)

        self._player_entity = create_player(self.ecs_world, engine.player_cfg,
                                            engine.sprites_cfg,
                                            vec(self._level_cfg["player_spawn"]))
        self._player_c_t = self.ecs_world.component_for_entity(self._player_entity, CTransform)
        self._player_c_s = self.ecs_world.component_for_entity(self._player_entity, CSurface)
        self._player_c_h = self.ecs_world.component_for_entity(self._player_entity, CHeading)
        self._player_c_m = self.ecs_world.component_for_entity(self._player_entity, CShipMotion)
        self._player_c_w = self.ecs_world.component_for_entity(self._player_entity, CWeapon)

        # Estado no jugable: puntaje/record, vidas, alerta y limite temporal global.
        self._high_score_path = self._level_cfg.get(
            "high_score_path", "save/high_score.json")
        self._game_stats_entity = create_game_stats(
            self.ecs_world,
            load_high_score(self._high_score_path),
            self._level_cfg.get("starting_lives", 3),
            self._level_cfg.get("round_number", 1),
            self._high_score_path,
        )
        create_stage_timer(
            self.ecs_world, self._level_cfg.get("alert_time_limit_seconds", 120))
        create_alert_state(self.ecs_world)

        # Sprite fijo, sin rotacion, para representar cada vida en el panel.
        player_texture = sprite_texture(engine.sprites_cfg, engine.player_cfg["sprite"])
        self._panel_ship_texture = pygame.transform.scale(player_texture, (12, 14))

        self._populate_level()

        # La camara arranca ya centrada en la nave, sin un salto en el primer frame
        system_camera(self.ecs_world, self._player_entity, self._world_size)
        self._c_camera.delta.update(0, 0)

    def _populate_level(self) -> None:
        """Coloca los enemigos fijos del nivel lejos del punto de aparicion de la nave."""
        obstacles_cfg = self._level_cfg["obstacles"]
        occupied = [(vec(self._level_cfg["player_spawn"]), obstacles_cfg["player_safe_radius"])]
        create_bases(self.ecs_world, self.engine.sprites_cfg, self.engine.enemies_cfg,
                     self._level_cfg["bases"], occupied)
        create_obstacles(self.ecs_world, self.engine.sprites_cfg, self.engine.enemies_cfg,
                         obstacles_cfg, self._world_size, occupied)

    # ----------------------------------------------------------- acciones (Command)
    def do_action(self, c_input: CInputCommand) -> None:
        if c_input.name in _MOVE_ACTIONS:
            self._update_input_direction()
        elif c_input.phase != CommandPhase.START:
            return
        elif c_input.name == "GAME_PAUSE":
            self._toggle_pause()
        elif c_input.name == "GAME_BACK":
            self.switch_scene(self.cfg["back_scene"])
        elif c_input.name == "DEBUG_COLLIDERS":
            self._debug = not self._debug
        elif c_input.name == "PLAYER_FIRE":
            self._fire()
        elif c_input.name == "PLAYER_TRIPLE_CANNON":
            self._fire_triple_cannon()
        elif c_input.name == "PLAYER_TOGGLE_MAIN_WEAPON":
            self._main_weapon_is_triple = not self._main_weapon_is_triple

    def _update_input_direction(self) -> None:
        """Direccion que piden las flechas (8 sentidos). El sistema de movimiento la usa."""
        # Una accion esta activa si cualquiera de sus teclas esta presionada
        active = {c.name for _, c in self.ecs_world.get_component(CInputCommand)
                  if c.phase == CommandPhase.START}
        direction = pygame.Vector2(0, 0)
        for name in active & _MOVE_ACTIONS.keys():
            direction += _MOVE_ACTIONS[name]
        if direction.length_squared() > 0:
            direction.scale_to_length(1)
        self._player_c_m.input_dir = direction

    def _ship_center(self) -> pygame.Vector2:
        return self._player_c_t.pos + pygame.Vector2(self._player_c_s.area.size) / 2

    def _fire(self) -> None:
        """Disparo principal, alternable entre normal y triple para pruebas."""
        if self._paused:
            return
        if self._main_weapon_is_triple:
            self._fire_triple_cannon(force=True)
            return
        alive = (len(self.ecs_world.get_component(CTagPlayerBullet))
                 - len(self.ecs_world.get_component(CTagSpecialBullet)))
        if alive + 2 <= self._player_c_w.max_bullets:
            create_player_shot(self.ecs_world, self.engine.sprites_cfg, self.engine.player_cfg,
                               self._ship_center(), self._player_c_h.direction)

    def _fire_triple_cannon(self, force: bool = False) -> None:
        """Cañon triple desbloqueado por nivel, con atajo de prueba opcional."""
        if self._paused or (not force and not self._level_cfg.get("triple_cannon", False)):
            return
        create_triple_shot(self.ecs_world, self.engine.sprites_cfg, self.engine.player_cfg,
                           self._ship_center(), self._player_c_h.direction)

    def _toggle_pause(self) -> None:
        self._paused = not self._paused
        if self._paused:
            view = self._c_camera.view
            self._pause_text = create_text(self.ecs_world, {
                "text": "PAUSA", "font": "assets/fnt/PressStart2P.ttf", "size": 8,
                "color": [255, 255, 255], "align": "center", "blink": 0.5,
                "pos": {"x": view.centerx, "y": view.centery - 32}})
        elif self._pause_text is not None:
            self.ecs_world.delete_entity(self._pause_text)
            self._pause_text = None

    # ------------------------------------------------------------------ actualizacion
    def do_update(self, delta_time: float) -> None:
        if self._paused:
            return
        engine = self.engine
        system_ship_motion(self.ecs_world, delta_time)
        system_player_sprite(self.ecs_world)
        system_animation(self.ecs_world, delta_time)
        system_base_core(self.ecs_world, delta_time)
        system_movement(self.ecs_world, delta_time)
        system_world_wrap(self.ecs_world, self._world_size)
        system_camera(self.ecs_world, self._player_entity, self._world_size)
        system_bullet_hits(self.ecs_world, self._world_size, engine.sprites_cfg, engine.enemies_cfg)
        system_blast(self.ecs_world, self._world_size, engine.sprites_cfg, engine.enemies_cfg)
        system_bullet_offscreen(self.ecs_world, self._c_camera, self._world_size)
        system_stars(self.ecs_world, self._c_camera, delta_time)

        # El temporizador es global e independiente de cualquier enemigo.
        system_stage_timer(self.ecs_world, delta_time)
        # No hay enemigos/espia implementados todavia; el parametro permite integrarlos despues.
        system_alert(self.ecs_world, enemy_detected=False)

    # ------------------------------------------------------------------------ dibujo
    def do_draw(self, screen: pygame.Surface) -> None:
        system_rendering_stars(self.ecs_world, screen, self._c_camera)
        system_rendering(self.ecs_world, screen, self._c_camera, self._world_size)
        panel = self.engine.window_cfg["layout"]["panel"]
        system_rendering_panel(
            self.ecs_world, screen, panel, self._world_size, self._panel_ship_texture
        )
        if self._debug:
            self._draw_colliders(screen)

    def _draw_colliders(self, screen: pygame.Surface) -> None:
        """Ayuda de depuracion (F1): dibuja las cajas de colision."""
        view_size = pygame.Vector2(self._c_camera.view.size)
        screen.set_clip(self._c_camera.view)
        for _, (c_t, c_s) in self.ecs_world.get_components(CTransform, CSurface):
            size = pygame.Vector2(c_s.area.size)
            pos = world_to_screen(c_t.pos, self._c_camera.topleft, self._world_size,
                                  view_size, size)
            if pos is not None:
                pygame.draw.rect(screen, pygame.Color(255, 0, 255),
                                 (pos + self._c_camera.view.topleft, size), width=1)
        screen.set_clip(None)
