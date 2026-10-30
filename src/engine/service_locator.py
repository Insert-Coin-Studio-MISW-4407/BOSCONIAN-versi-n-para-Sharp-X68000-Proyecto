"""Patron Service Locator.

Punto unico de acceso a los servicios de recursos del juego. Los sistemas y los
prefabs piden texturas, sonidos, musica y fuentes aqui en vez de cargarlas por su
cuenta, asi cada recurso se carga una sola vez y se puede cambiar la implementacion
de un servicio sin tocar a quien lo usa.
"""
from src.engine.services.font_service import FontService
from src.engine.services.music_service import MusicService
from src.engine.services.sound_service import SoundService
from src.engine.services.texture_service import TextureService


class ServiceLocator:
    textures_service = TextureService()
    sounds_service = SoundService()
    music_service = MusicService()
    fonts_service = FontService()


def preload_assets(assets_cfg: dict) -> None:
    """Carga de una vez los recursos listados en assets.json (pantalla de carga)."""
    for path in assets_cfg.get("images", []):
        ServiceLocator.textures_service.get(path)
    for path in assets_cfg.get("sounds", []):
        ServiceLocator.sounds_service.get(path)
    for font in assets_cfg.get("fonts", []):
        ServiceLocator.fonts_service.get(font["path"], font["size"])
