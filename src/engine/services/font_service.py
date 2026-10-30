"""Servicio de fuentes.

Soporta dos tipos de fuente con la misma interfaz (`render(texto, antialias, color)`,
igual que `pygame.font.Font`), asi que quien dibuja texto no sabe cual esta usando:

- Fuente de mapa de bits (.png + .json con el charset): es la del juego. A 8 pixeles
  una fuente vectorial se convierte en una mancha, asi que los glifos se dibujan
  pixel a pixel desde una hoja de sprites.
- Fuente TrueType (.ttf): por si se reemplaza por la fuente oficial del curso.

Si el archivo pedido no existe se cae a la fuente por defecto de pygame, para que el
juego nunca se quede sin HUD.
"""
import json
import os

import pygame


class BitmapFont:
    """Fuente de mapa de bits. `scale` multiplica el tamaño del glifo."""

    def __init__(self, image_path: str, meta: dict, scale: int = 1) -> None:
        self._sheet = pygame.image.load(image_path).convert_alpha()
        self._charset = meta["charset"]
        self._cell_w = meta["cell_w"]
        self._cell_h = meta["cell_h"]
        self._advance = meta["advance"] * scale
        self._scale = scale
        self._height = self._cell_h * scale
        if scale != 1:
            self._sheet = pygame.transform.scale_by(self._sheet, scale)
        self._fallback_index = self._charset.find(" ")
        # Una copia teñida por color, para no repetir el trabajo en cada frame
        self._tinted: dict[tuple[int, int, int, int], pygame.Surface] = {}

    def get_height(self) -> int:
        return self._height

    def size(self, text: str) -> tuple[int, int]:
        return len(text) * self._advance, self._height

    def render(self, text: str, antialias: bool, color) -> pygame.Surface:
        """Misma firma que pygame.font.Font.render; `antialias` se ignora."""
        del antialias
        text = text.upper()
        sheet = self._sheet_for(pygame.Color(color))
        cell_w = self._cell_w * self._scale
        surface = pygame.Surface((max(1, len(text) * self._advance), self._height),
                                 pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        for position, char in enumerate(text):
            index = self._charset.find(char)
            if index < 0:
                index = self._fallback_index
            surface.blit(sheet, (position * self._advance, 0),
                         area=pygame.Rect(index * cell_w, 0, cell_w, self._height))
        return surface

    def _sheet_for(self, color: pygame.Color) -> pygame.Surface:
        key = (color.r, color.g, color.b, color.a)
        if key not in self._tinted:
            tinted = self._sheet.copy()
            # Los glifos son blancos: multiplicar por el color los tiñe conservando el alfa
            tinted.fill(key, special_flags=pygame.BLEND_RGBA_MULT)
            self._tinted[key] = tinted
        return self._tinted[key]


class FontService:
    def __init__(self) -> None:
        self._fonts: dict[tuple[str, int], object] = {}

    def get(self, path: str, size: int):
        key = (path, size)
        if key not in self._fonts:
            self._fonts[key] = self._load(path, size)
        return self._fonts[key]

    @staticmethod
    def _load(path: str, size: int):
        if path.endswith(".png") and os.path.isfile(path):
            meta_path = os.path.splitext(path)[0] + ".json"
            with open(meta_path, encoding="utf-8") as meta_file:
                meta = json.load(meta_file)
            scale = max(1, int(size) // meta.get("base_size", 8))
            return BitmapFont(path, meta, scale)
        if path and os.path.isfile(path):
            return pygame.font.Font(path, size)
        return pygame.font.Font(None, size)
