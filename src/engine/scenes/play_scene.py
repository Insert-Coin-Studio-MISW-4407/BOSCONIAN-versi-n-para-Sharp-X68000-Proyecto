"""Escena de juego: el mundo toroidal, la camara, el fondo de estrellas, la nave y los enemigos."""
from __future__ import annotations

import pygame

from src.create.prefab_creator import (create_alert_state, create_bases, create_camera,
                                       create_enemy_spawner, create_explosion, create_game_stats,
                                       create_obstacles, create_player, create_player_shot,
                                       create_stage_timer, create_starfield, create_text,
                                       create_triple_shot, sprite_texture, vec)
from src.ecs.components.c_base import CBase
from src.ecs.components.c_blink import CBlink
from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_enemy import CEnemy
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_game_stats import CGameStats
from src.ecs.components.c_heading import CHeading
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_invulnerable import CInvulnerable
from src.ecs.components.c_ship_motion import CShipMotion
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_weapon import CWeapon
from src.ecs.components.tags.c_tag_enemy_bullet import CTagEnemyBullet
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_player_bullet import CTagPlayerBullet
from src.ecs.components.tags.c_tag_special_bullet import CTagSpecialBullet
from src.ecs.systems.s_alert import enemies_near, is_red_alert, system_alert
from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_base_cannon import system_base_cannon
from src.ecs.systems.s_base_core import system_base_core
from src.ecs.systems.s_bullet_offscreen import system_bullet_offscreen
from src.ecs.systems.s_camera import system_camera
from src.ecs.systems.s_chaser import system_chaser
from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_formation import system_formation
from src.ecs.systems.s_spy import system_spy, system_spy_spawner
from src.ecs.systems.s_enemy_hits import system_blast, system_bullet_hits
from src.ecs.systems.s_game_stats import load_high_score, system_lose_life
from src.ecs.systems.s_lifetime import system_lifetime
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_player_hits import system_invulnerable, system_player_hits
from src.ecs.systems.s_player_sprite import system_player_sprite
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_rendering_panel import system_rendering_panel
from src.ecs.systems.s_rendering_stars import system_rendering_stars
from src.ecs.systems.s_ship_motion import system_ship_motion
from src.ecs.systems.s_stage_timer import system_stage_timer, system_start_next_round
from src.ecs.systems.s_stars import system_stars
from src.ecs.systems.s_world_wrap import system_world_wrap
from src.engine.scenes.scene import Scene
from src.engine.services.sound_service import (SOUND_EXPLOSION, SOUND_FIRE,
                                                SOUND_GAME_OVER, SOUND_LEVEL_CLEAR)
from src.engine.service_locator import ServiceLocator
from src.engine.world_math import world_to_screen

# Direccion en la que cada accion de movimiento empuja a la nave
_MOVE_ACTIONS = {
    "PLAYER_LEFT": pygame.Vector2(-1, 0),
    "PLAYER_RIGHT": pygame.Vector2(1, 0),
    "PLAYER_UP": pygame.Vector2(0, -1),
    "PLAYER_DOWN": pygame.Vector2(0, 1),
}

_MESSAGE_FONT = "assets/fnt/PressStart2P.ttf"


class PlayScene(Scene):
    def __init__(self, engine, scene_cfg: dict) -> None:
        super().__init__(engine, scene_cfg)
        self._level_paths = scene_cfg.get("levels") or [scene_cfg["level"]]
        self._level_index = 0
        self._level_cfg = engine.load_cfg(self._level_paths[self._level_index])
        self._paused = False
        self._pause_text: int | None = None
        self._debug = False
        self._main_weapon_is_triple = bool(self._level_cfg.get("triple_cannon", False))
        # Nave: None mientras esta explotando o tras el game over
        self._player_entity: int | None = None
        self._respawn_timer = 0.0
        self._respawn_pos = pygame.Vector2(0, 0)
        self._game_over_timer: float | None = None
        self._round_clear_timer: float | None = None
        self._message_text: int | None = None
        self._message_timer: float | None = None

    # --------------------------------------------------------------------- creacion
    def do_create(self) -> None:
        engine = self.engine
        world_cfg = engine.world_cfg
        self._world_size = pygame.Vector2(world_cfg["size"]["w"], world_cfg["size"]["h"])
        layout = engine.window_cfg["layout"]

        camera_entity = create_camera(self.ecs_world, layout["view"])
        self._c_camera = self.ecs_world.component_for_entity(camera_entity, CCamera)
        create_starfield(self.ecs_world, world_cfg["stars"], self._c_camera.view)

        self._spawn_player(vec(self._level_cfg["player_spawn"]), invulnerable=False)

        # Estado no jugable: puntaje/record, vidas, alerta y limite temporal global.
        self._high_score_path = self._level_cfg.get(
            "high_score_path", "save/high_score.json")
        self._game_stats_entity = create_game_stats(
            self.ecs_world,
            load_high_score(self._high_score_path),
            getattr(engine, "game_cfg", {}).get("starting_lives", 3),
            self._level_cfg.get("round_number", 1),
            self._high_score_path,
        )
        self._c_stats = self.ecs_world.component_for_entity(self._game_stats_entity, CGameStats)
        create_stage_timer(
            self.ecs_world, self._level_cfg.get("alert_time_limit_seconds", 120))
        create_alert_state(self.ecs_world)
        create_enemy_spawner(self.ecs_world, engine.enemies_cfg)

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

    def _spawn_player(self, center: pygame.Vector2, invulnerable: bool = True) -> None:
        """Crea la nave centrada en `center`; al reaparecer parpadea y es invulnerable un rato."""
        engine = self.engine
        self._player_entity = create_player(self.ecs_world, engine.player_cfg,
                                            engine.sprites_cfg, center)
        world = self.ecs_world
        self._player_c_t = world.component_for_entity(self._player_entity, CTransform)
        self._player_c_s = world.component_for_entity(self._player_entity, CSurface)
        self._player_c_h = world.component_for_entity(self._player_entity, CHeading)
        self._player_c_m = world.component_for_entity(self._player_entity, CShipMotion)
        self._player_c_w = world.component_for_entity(self._player_entity, CWeapon)
        if invulnerable:
            death_cfg = engine.player_cfg["death"]
            world.add_component(self._player_entity, CInvulnerable(death_cfg["invulnerable_time"]))
            world.add_component(self._player_entity, CBlink(death_cfg["blink_interval"],
                                                            death_cfg["invulnerable_time"]))
        self._update_input_direction()

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
        elif c_input.name == "PLAYER_TOGGLE_MAIN_WEAPON":
            self._main_weapon_is_triple = not self._main_weapon_is_triple

    def _update_input_direction(self) -> None:
        """Direccion que piden las flechas (8 sentidos). El sistema de movimiento la usa."""
        if self._player_entity is None:
            return
        # Una accion esta activa si cualquiera de sus teclas esta presionada
        active = {c.name for _, c in self.ecs_world.get_component(CInputCommand)
                  if c.phase == CommandPhase.START}
        direction = pygame.Vector2(0, 0)
        for name in active & _MOVE_ACTIONS.keys():
            direction += _MOVE_ACTIONS[name]
        if direction.length_squared() > 0:
            direction.scale_to_length(1)
        self._player_c_m.input_dir = direction

    def _ship_center(self) -> pygame.Vector2 | None:
        if self._player_entity is None:
            return None
        return self._player_c_t.pos + pygame.Vector2(self._player_c_s.area.size) / 2

    def _can_fire(self) -> bool:
        return not self._paused and self._player_entity is not None

    def _fire(self) -> None:
        """Disparo principal, alternable entre normal y triple para pruebas."""
        if not self._can_fire():
            return
        if self._main_weapon_is_triple:
            self._fire_triple_cannon(force=True)
            ServiceLocator.sounds_service.play(SOUND_FIRE)
            return
        alive = (len(self.ecs_world.get_component(CTagPlayerBullet))
                 - len(self.ecs_world.get_component(CTagSpecialBullet)))
        if alive + 2 <= self._player_c_w.max_bullets:
            create_player_shot(self.ecs_world, self.engine.sprites_cfg, self.engine.player_cfg,
                               self._ship_center(), self._player_c_h.direction)
            ServiceLocator.sounds_service.play(SOUND_FIRE)

    def _fire_triple_cannon(self, force: bool = False) -> None:
        """Cañon triple desbloqueado por nivel, con atajo de prueba opcional."""
        if not self._can_fire() or (not force and not self._level_cfg.get("triple_cannon", False)):
            return
        create_triple_shot(self.ecs_world, self.engine.sprites_cfg, self.engine.player_cfg,
                           self._ship_center(), self._player_c_h.direction)

    def _toggle_pause(self) -> None:
        self._paused = not self._paused
        if self._paused:
            self._pause_text = self._create_message("PAUSA", blink=True, dy=-32)
        elif self._pause_text is not None:
            self.ecs_world.delete_entity(self._pause_text)
            self._pause_text = None

    def _create_message(self, text: str, blink: bool = False, dy: int = 0) -> int:
        """Texto centrado en la vista de juego (pausa, game over...)."""
        view = self._c_camera.view
        text_cfg = {"text": text, "font": _MESSAGE_FONT, "size": 8, "color": [255, 255, 255],
                    "align": "center", "pos": {"x": view.centerx, "y": view.centery + dy}}
        if blink:
            text_cfg["blink"] = 0.5
        return create_text(self.ecs_world, text_cfg)

    # ------------------------------------------------------------------ actualizacion
    def do_update(self, delta_time: float) -> None:
        if self._paused:
            return
        engine = self.engine
        world = self.ecs_world
        enemies_cfg = engine.enemies_cfg
        target = self._ship_center()
        system_ship_motion(world, delta_time)
        heading = self._player_c_h.direction if self._player_entity is not None else None
        # Con la ronda ya ganada no aparecen enemigos nuevos
        spawn_target = target if self._round_clear_timer is None else None
        system_enemy_spawner(world, delta_time, spawn_target, heading, is_red_alert(world),
                             engine.sprites_cfg, enemies_cfg)
        system_spy_spawner(world, delta_time, spawn_target, heading, engine.sprites_cfg,
                           enemies_cfg)
        system_chaser(world, delta_time, target, self._world_size,
                      enemies_cfg["spawner"]["despawn_distance"])
        system_spy(world, delta_time, target, self._world_size)
        # Gira el sprite de todo lo que tenga rumbo: la nave y las naves enemigas
        system_player_sprite(world)
        system_animation(world, delta_time)
        system_invulnerable(world, delta_time)
        system_base_core(world, delta_time)
        system_base_cannon(world, delta_time, self._ship_center(), self._world_size,
                           engine.sprites_cfg, engine.enemies_cfg)
        system_lifetime(world, delta_time)
        system_movement(world, delta_time)
        system_world_wrap(world, self._world_size)
        system_formation(world)
        if self._player_entity is not None:
            system_camera(world, self._player_entity, self._world_size)
        else:
            # Sin nave la camara se queda quieta (y las estrellas tambien)
            self._c_camera.delta.update(0, 0)
        system_bullet_hits(world, self._world_size, engine.sprites_cfg, engine.enemies_cfg)
        blasts = system_blast(world, self._world_size, engine.sprites_cfg, engine.enemies_cfg)
        if self._player_entity is not None and system_player_hits(
                world, self._player_entity, self._world_size, blasts,
                engine.sprites_cfg, engine.enemies_cfg):
            self._kill_player()
        system_bullet_offscreen(world, self._c_camera, self._world_size)
        system_stars(world, self._c_camera, delta_time)

        # El temporizador es global e independiente de cualquier enemigo.
        system_stage_timer(world, delta_time)
        # YELLOW cuando hay naves enemigas cerca de la nave
        system_alert(world, enemy_detected=enemies_near(
            world, self._ship_center(), self._world_size,
            enemies_cfg["alert"]["detect_radius"]))

        if self._round_clear_timer is None and self._game_over_timer is None \
                and not world.get_component(CBase):
            self._start_round_clear()
        self._update_death_flow(delta_time)
        self._update_round_flow(delta_time)
        self._update_message(delta_time)

    def _show_message(self, text: str, seconds: float | None = None) -> None:
        """Mensaje central unico (GAME OVER, LEVEL CLEAR...); `seconds` None = permanente."""
        if self._message_text is not None:
            self.ecs_world.delete_entity(self._message_text)
        self._message_text = self._create_message(text, dy=-40)
        self._message_timer = seconds

    def _update_message(self, delta_time: float) -> None:
        if self._message_timer is None:
            return
        self._message_timer -= delta_time
        if self._message_timer <= 0 and self._message_text is not None:
            self.ecs_world.delete_entity(self._message_text)
            self._message_text = None
            self._message_timer = None

    def _kill_player(self) -> None:
        """La nave explota y se descuenta una vida; sin vidas, termina la partida."""
        center = self._ship_center()
        create_explosion(self.ecs_world, self.engine.sprites_cfg, self.engine.enemies_cfg, center)
        ServiceLocator.sounds_service.play(SOUND_EXPLOSION)
        self.ecs_world.delete_entity(self._player_entity)
        self._player_entity = None
        system_lose_life(self.ecs_world)
        death_cfg = self.engine.player_cfg["death"]
        if self._c_stats.lives <= 0:
            self._game_over_timer = death_cfg["game_over_delay"]
            ServiceLocator.sounds_service.play(SOUND_GAME_OVER)
            self._show_message("GAME OVER")
        else:
            # Como en el original, la nave reaparece donde exploto
            self._respawn_timer = death_cfg["respawn_delay"]
            self._respawn_pos = center

    def _update_death_flow(self, delta_time: float) -> None:
        if self._game_over_timer is not None:
            self._game_over_timer -= delta_time
            if self._game_over_timer <= 0:
                self.switch_scene(self.cfg["back_scene"])
        elif self._player_entity is None:
            self._respawn_timer -= delta_time
            if self._respawn_timer <= 0:
                self._spawn_player(self._respawn_pos)

    # -------------------------------------------------------------------------- rondas
    def _start_round_clear(self) -> None:
        """Todas las estaciones cayeron: la nave queda a salvo hasta la ronda siguiente."""
        rounds_cfg = self._level_cfg["rounds"]
        self._round_clear_timer = rounds_cfg["clear_delay"]
        ServiceLocator.sounds_service.play(SOUND_LEVEL_CLEAR)
        self._show_message("LEVEL CLEAR")
        if self._player_entity is not None:
            self.ecs_world.add_component(self._player_entity,
                                         CInvulnerable(rounds_cfg["clear_delay"] + 1))

    def _update_round_flow(self, delta_time: float) -> None:
        if self._round_clear_timer is None or self._game_over_timer is not None:
            return
        self._round_clear_timer -= delta_time
        if self._round_clear_timer <= 0:
            self._round_clear_timer = None
            self._start_next_level()

    def _start_next_level(self) -> None:
        """Cicla los mapas, incrementa el nivel y conserva el progreso de la partida.

        Se conservan puntaje, record y vidas; el temporizador y la alerta se reinician
        y los enemigos aparecen un poco mas seguido en cada nivel.
        """
        world = self.ecs_world
        for component in (CEnemy, CTagEnemyBullet, CTagPlayerBullet, CTagPlayer):
            for entity, _ in world.get_component(component):
                world.delete_entity(entity)
        self._player_entity = None

        self._level_index = (self._level_index + 1) % len(self._level_paths)
        self._level_cfg = self.engine.load_cfg(self._level_paths[self._level_index])
        self._main_weapon_is_triple = bool(self._level_cfg.get("triple_cannon", False))
        level_number = self._c_stats.round_number + 1
        system_start_next_round(world, level_number,
                               self._level_cfg.get("alert_time_limit_seconds", 120))
        rounds_cfg = self._level_cfg["rounds"]
        spawner_cfg = self.engine.enemies_cfg["spawner"]
        for _, c_sp in world.get_component(CEnemySpawner):
            c_sp.timer = spawner_cfg["first_delay"]
            c_sp.spy_timer = self.engine.enemies_cfg["spy"]["first_delay"]
            c_sp.interval_scale = max(rounds_cfg["min_interval_scale"],
                                      c_sp.interval_scale * rounds_cfg["interval_scale"])

        self._populate_level()
        self._spawn_player(vec(self._level_cfg["player_spawn"]))
        system_camera(world, self._player_entity, self._world_size)
        self._c_camera.delta.update(0, 0)
        self._show_message(f"LEVEL {level_number}", rounds_cfg["banner_time"])

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
