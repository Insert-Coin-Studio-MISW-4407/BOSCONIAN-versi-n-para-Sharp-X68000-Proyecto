"""Motor del juego: patron Game Loop + gestor de escenas."""
import asyncio
import json

import pygame

from src.engine.scenes.play_scene import PlayScene
from src.engine.scenes.text_scene import TextScene
from src.engine.service_locator import ServiceLocator, preload_assets

_CFG = "assets/cfg/"

# Tipo de escena declarado en scenes.json -> clase que la implementa.
# Cada PR que agregue un tipo de escena nuevo lo registra aqui.
_SCENE_TYPES = {
    "TEXT": TextScene,
    "PLAY": PlayScene,
}


class GameEngine:
    def __init__(self) -> None:
        self._load_config_files()

        pygame.init()
        self._init_mixer()
        ServiceLocator.sounds_service.set_default_volume(self.audio_cfg["sfx_volume"])
        pygame.display.set_caption(self.window_cfg["title"])
        # SCALED: la ventana se agranda pero el juego sigue dibujando a resolucion nativa
        self.screen = pygame.display.set_mode(
            (self.window_cfg["size"]["w"], self.window_cfg["size"]["h"]),
            pygame.SCALED | pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.framerate = self.window_cfg["framerate"]
        self.bg_color = pygame.Color(self.window_cfg["bg_color"]["r"],
                                     self.window_cfg["bg_color"]["g"],
                                     self.window_cfg["bg_color"]["b"])
        self.is_running = False
        self.delta_time = 0.0

        preload_assets(self.assets_cfg)
        self._current_scene = None
        self._scene_to_switch: str | None = None

    # -------------------------------------------------------------- configuracion
    def _load_config_files(self) -> None:
        """Todo numero ajustable del juego vive en assets/cfg/*.json."""
        self.window_cfg = self.load_cfg("window.json")
        self.assets_cfg = self.load_cfg("assets.json")
        self.audio_cfg = self.load_cfg("audio.json")
        self.input_cfg = self.load_cfg("input.json")
        self.scenes_cfg = self.load_cfg("scenes.json")
        self.sprites_cfg = self.load_cfg("sprites.json")
        self.world_cfg = self.load_cfg("world.json")
        self.player_cfg = self.load_cfg("player.json")
        self.enemies_cfg = self.load_cfg("enemies.json")

    @staticmethod
    def load_cfg(name: str) -> dict:
        with open(_CFG + name, encoding="utf-8") as cfg_file:
            return json.load(cfg_file)

    @staticmethod
    def _init_mixer() -> None:
        """El audio puede no estar disponible (web o maquina sin tarjeta); no es fatal."""
        try:
            pygame.mixer.init()
        except pygame.error:
            pass

    # ------------------------------------------------------------------- escenas
    def switch_scene(self, name: str) -> None:
        """Pide el cambio de escena; se aplica al final del frame actual."""
        self._scene_to_switch = name

    def _apply_scene_switch(self) -> None:
        name = self._scene_to_switch
        self._scene_to_switch = None
        if self._current_scene is not None:
            self._current_scene.clean()
        scene_cfg = self.scenes_cfg["scenes"][name]
        # Las escenas se crean de nuevo en cada visita: asi siempre empiezan limpias
        self._current_scene = _SCENE_TYPES[scene_cfg["type"]](self, scene_cfg)
        self._current_scene.create()

    # ----------------------------------------------------------------- game loop
    async def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
            # Cede el control al navegador: obligatorio para la exportacion con pygbag
            await asyncio.sleep(0)
        self._clean()

    def _create(self) -> None:
        self.switch_scene(self.scenes_cfg["initial_scene"])
        self._apply_scene_switch()

    def _calculate_time(self) -> None:
        self.clock.tick(self.framerate)
        # Se limita el paso para que una pausa larga (arrastrar la ventana) no
        # teletransporte a las entidades
        self.delta_time = min(self.clock.get_time() / 1000.0, 1.0 / 20)

    def _process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            else:
                self._current_scene.process_events(event)

    def _update(self) -> None:
        self._current_scene.update(self.delta_time)
        if self._scene_to_switch is not None:
            self._apply_scene_switch()

    def _draw(self) -> None:
        self._current_scene.draw(self.screen)
        pygame.display.flip()

    def _clean(self) -> None:
        if self._current_scene is not None:
            self._current_scene.clean()
        pygame.quit()
