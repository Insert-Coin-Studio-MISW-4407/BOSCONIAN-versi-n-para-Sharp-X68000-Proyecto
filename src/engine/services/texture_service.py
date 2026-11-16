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
                   angle: float = 0, tint: tuple | None = None) -> pygame.Surface:
        """Recorte del atlas, opcionalmente en espejo horizontal, girado `angle` grados
        (antihorario) y/o tenido (multiplica el color). Cada variante se crea una sola vez."""
        key = (path, tuple(rect), flip_x, angle, tint)
        if key not in self._regions:
            region = self.get(path).subsurface(pygame.Rect(rect))
            if flip_x:
                region = pygame.transform.flip(region, True, False)
            if angle:
                region = pygame.transform.rotate(region, angle)
            if tint:
                region = region.copy()
                region.fill(pygame.Color(*tint), special_flags=pygame.BLEND_RGB_MULT)
            self._regions[key] = region
        return self._regions[key]

    def get_keyed_region(self, path: str, rect: list[int], colorkey: tuple,
                         holes: tuple = ()) -> pygame.Surface:
        """Recorte de una ilustracion con fondo de color solido (`colorkey`), que se vuelve
        transparente. `holes` son circulos (cx, cy, radio) que tambien se vacian, para
        poner encima piezas que se animan o se destruyen por separado."""
        key = (path, tuple(rect), tuple(colorkey), tuple(holes))
        if key not in self._regions:
            region = self.get(path).subsurface(pygame.Rect(rect)).copy()
            clear = pygame.Color(0, 0, 0, 0)
            keyed = pygame.Color(*colorkey)
            for y in range(region.get_height()):
                for x in range(region.get_width()):
                    pixel = region.get_at((x, y))
                    in_hole = any((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r
                                  for cx, cy, r in holes)
                    if in_hole or pixel[:3] == keyed[:3]:
                        region.set_at((x, y), clear)
            self._regions[key] = region
        return self._regions[key]

    def clear(self) -> None:
        self._textures.clear()
        self._regions.clear()
