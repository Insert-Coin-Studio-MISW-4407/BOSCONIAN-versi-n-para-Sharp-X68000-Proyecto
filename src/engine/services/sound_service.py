"""Servicio de sonidos.

Tolera archivos ausentes: devuelve None y el sistema que lo pide simplemente no suena.
Esto permite trabajar sin los .ogg definitivos sin romper el juego ni la exportacion web.
"""
from __future__ import annotations

import os

import pygame

# Para web (pygbag) el formato soportado es .ogg; .wav se acepta solo en escritorio
_EXTENSIONS = (".ogg", ".wav")
SOUND_FIRE = "assets/sfx/01_disparo_laser.ogg"
SOUND_EXPLOSION = "assets/sfx/02_explosion.ogg"
SOUND_LEVEL_CLEAR = "assets/sfx/03_victoria_nivel.ogg"
SOUND_GAME_OVER = "assets/sfx/04_game_over.ogg"


class SoundService:
    def __init__(self) -> None:
        self._sounds: dict[str, pygame.mixer.Sound | None] = {}
        self._default_volume = 1.0

    def set_default_volume(self, volume: float) -> None:
        """Define el volumen usado por los efectos que no especifican uno propio."""
        self._default_volume = max(0.0, min(1.0, float(volume)))

    def get(self, path: str) -> pygame.mixer.Sound | None:
        if path not in self._sounds:
            self._sounds[path] = self._load(path)
        return self._sounds[path]

    def play(self, path: str, volume: float | None = None) -> None:
        sound = self.get(path)
        if sound is not None:
            sound.set_volume(self._default_volume if volume is None else volume)
            sound.play()

    def _load(self, path: str) -> pygame.mixer.Sound | None:
        if not pygame.mixer.get_init():
            return None
        for candidate in self._candidates(path):
            if os.path.isfile(candidate):
                try:
                    return pygame.mixer.Sound(candidate)
                except pygame.error:
                    return None
        return None

    @staticmethod
    def _candidates(path: str) -> list[str]:
        base, _ = os.path.splitext(path)
        return [path] + [base + ext for ext in _EXTENSIONS]
