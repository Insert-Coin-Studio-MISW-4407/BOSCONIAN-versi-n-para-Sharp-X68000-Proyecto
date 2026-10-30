#!/usr/bin/python3
"""Punto de entrada.

Escritorio: python main.py
Web:        pygbag . (requiere que el bucle principal sea asincrono)
"""
import asyncio
import os

from src.engine.game_engine import GameEngine


async def main() -> None:
    # Las rutas de assets son relativas a main.py, para poder lanzarlo desde cualquier sitio
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    engine = GameEngine()
    await engine.run()


if __name__ == "__main__":
    asyncio.run(main())
