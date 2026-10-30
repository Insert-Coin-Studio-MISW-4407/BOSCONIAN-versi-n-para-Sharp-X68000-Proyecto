"""Escena de juego: el mundo toroidal, la camara, el fondo de estrellas y la nave."""
import pygame

from src.create.prefab_creator import (color, create_camera, create_player,
                                       create_starfield, create_text, vec)
from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.s_camera import system_camera
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_rendering_stars import system_rendering_stars
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
        self._player_c_v = self.ecs_world.component_for_entity(self._player_entity,
                                                               CVelocity)
        # La camara arranca ya centrada en la nave, sin un salto en el primer frame
        system_camera(self.ecs_world, self._player_entity, self._world_size)
        self._c_camera.delta.update(0, 0)

    # ----------------------------------------------------------- acciones (Command)
    def do_action(self, c_input: CInputCommand) -> None:
        if c_input.name in _MOVE_ACTIONS:
            self._update_player_velocity()
        elif c_input.phase != CommandPhase.START:
            return
        elif c_input.name == "GAME_PAUSE":
            self._toggle_pause()
        elif c_input.name == "GAME_BACK":
            self.switch_scene(self.cfg["back_scene"])
        elif c_input.name == "DEBUG_COLLIDERS":
            self._debug = not self._debug

    def _update_player_velocity(self) -> None:
        # Una accion esta activa si cualquiera de sus teclas esta presionada
        active = {c.name for _, c in self.ecs_world.get_component(CInputCommand)
                  if c.phase == CommandPhase.START}
        direction = pygame.Vector2(0, 0)
        for name in active & _MOVE_ACTIONS.keys():
            direction += _MOVE_ACTIONS[name]
        if direction.length_squared() > 0:
            direction.scale_to_length(1)
        self._player_c_v.vel = direction * self.engine.player_cfg["speed"]

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
        system_movement(self.ecs_world, delta_time)
        system_world_wrap(self.ecs_world, self._world_size)
        system_camera(self.ecs_world, self._player_entity, self._world_size)
        system_stars(self.ecs_world, self._c_camera, delta_time)

    # ------------------------------------------------------------------------ dibujo
    def do_draw(self, screen: pygame.Surface) -> None:
        system_rendering_stars(self.ecs_world, screen, self._c_camera)
        system_rendering(self.ecs_world, screen, self._c_camera, self._world_size)
        panel = self.engine.window_cfg["layout"]["panel"]
        pygame.draw.rect(screen, color(panel["color"]),
                         (panel["x"], panel["y"], panel["w"], panel["h"]))
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
