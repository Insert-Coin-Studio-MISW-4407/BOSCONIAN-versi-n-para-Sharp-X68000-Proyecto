"""Sistemas de puntuacion y vidas, separados de la presentacion del HUD."""
import json
import os

import esper

from src.ecs.components.c_game_stats import CGameStats

_DEFAULT_HIGH_SCORE_PATH = "save/high_score.json"


def load_high_score(path: str = _DEFAULT_HIGH_SCORE_PATH) -> int:
    """Lee el record local. Un archivo ausente o invalido equivale a cero."""
    try:
        with open(path, "r", encoding="utf-8") as save_file:
            data = json.load(save_file)
        return max(0, int(data.get("high_score", 0)))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return 0


def _save_high_score(score: int, path: str) -> None:
    """Guarda el record sin interrumpir la partida si el almacenamiento falla."""
    try:
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as save_file:
            json.dump({"high_score": int(score)}, save_file)
    except OSError:
        # El juego sigue funcionando aunque el entorno sea de solo lectura.
        pass


def system_add_score(world: esper.World, points: int,
                     save_path: str | None = None) -> None:
    """Suma puntos y persiste el record cuando se supera.

    La llama `destroy_enemy` (y el bonus de estaciones y formaciones) con los
    puntos de cada enemigo.
    """
    amount = int(points)
    if amount <= 0:
        return
    for _, stats in world.get_component(CGameStats):
        stats.score += amount
        if stats.score > stats.high_score:
            stats.high_score = stats.score
            _save_high_score(stats.high_score, save_path or stats.high_score_path
                             or _DEFAULT_HIGH_SCORE_PATH)


def system_lose_life(world: esper.World) -> None:
    """Descuenta una vida, sin permitir valores negativos."""
    for _, stats in world.get_component(CGameStats):
        stats.lives = max(0, stats.lives - 1)
