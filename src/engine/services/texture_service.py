"""Servicio de texturas: carga cada imagen una sola vez y la reparte."""
import pygame


class TextureService:
    def __init__(self) -> None:
        self._textures: dict[str, pygame.Surface] = {}

    def get(self, path: str) -> pygame.Surface:
        if path not in self._textures:
            self._textures[path] = pygame.image.load(path).convert_alpha()
        return self._textures[path]

    def clear(self) -> None:
        self._textures.clear()
