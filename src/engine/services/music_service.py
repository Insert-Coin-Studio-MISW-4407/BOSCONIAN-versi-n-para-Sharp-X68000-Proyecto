"""Servicio de musica.

La musica se reproduce en streaming con pygame.mixer.music (no se carga entera en
memoria como los efectos). Cada escena declara su pista en scenes.json; si la pista
pedida ya esta sonando no se reinicia, asi dos escenas seguidas pueden compartirla.
"""
from __future__ import annotations

import os

import pygame


class MusicService:
    def __init__(self) -> None:
        self._current: str | None = None

    def play(self, path: str | None, loops: int = -1, volume: float = 1.0) -> None:
        if not path:
            self.stop()
            return
        if path == self._current or not pygame.mixer.get_init():
            return
        if not os.path.isfile(path):
            self.stop()
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            self._current = path
        except pygame.error:
            self._current = None

    def stop(self) -> None:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self._current = None
