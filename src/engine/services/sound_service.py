"""Servicio de sonidos.

Tolera archivos ausentes: devuelve None y el sistema que lo pide simplemente no suena.
Esto permite trabajar sin los .ogg definitivos sin romper el juego ni la exportacion web.
"""
import os

import pygame

# Para web (pygbag) el formato soportado es .ogg; .wav se acepta solo en escritorio
_EXTENSIONS = (".ogg", ".wav")


class SoundService:
    def __init__(self) -> None:
        self._sounds: dict[str, pygame.mixer.Sound | None] = {}

    def get(self, path: str) -> pygame.mixer.Sound | None:
        if path not in self._sounds:
            self._sounds[path] = self._load(path)
        return self._sounds[path]

    def play(self, path: str, volume: float = 1.0) -> None:
        sound = self.get(path)
        if sound is not None:
            sound.set_volume(volume)
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
