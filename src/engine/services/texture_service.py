"""Servicio de texturas: carga cada imagen una sola vez y la reparte.

Los recursos del curso vienen en una sola hoja (atlas). `get_region` devuelve un
recorte de esa hoja, tambien cacheado, asi todas las entidades del mismo tipo
comparten la misma superficie.
"""
import pygame


class TextureService:
    def __init__(self) -> None:
        self._textures: dict[str, pygame.Surface] = {}
        self._regions: dict[tuple, pygame.Surface] = {}

    def get(self, path: str) -> pygame.Surface:
        if path not in self._textures:
            self._textures[path] = pygame.image.load(path).convert_alpha()
        return self._textures[path]

    def get_region(self, path: str, rect: list[int], flip_x: bool = False,
                   angle: float = 0) -> pygame.Surface:
        """Recorte del atlas, opcionalmente en espejo horizontal y/o girado `angle` grados
        (antihorario). Cada variante se crea una sola vez."""
        key = (path, tuple(rect), flip_x, angle)
        if key not in self._regions:
            region = self.get(path).subsurface(pygame.Rect(rect))
            if flip_x:
                region = pygame.transform.flip(region, True, False)
            if angle:
                region = pygame.transform.rotate(region, angle)
            self._regions[key] = region
        return self._regions[key]

    def clear(self) -> None:
        self._textures.clear()
        self._regions.clear()
