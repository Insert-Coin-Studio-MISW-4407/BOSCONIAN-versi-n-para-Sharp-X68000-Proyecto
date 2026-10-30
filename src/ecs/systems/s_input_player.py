from typing import Callable

import esper
import pygame

from src.ecs.components.c_input_command import CInputCommand, CommandPhase, InputDevice

_PHASE_BY_EVENT = {
    pygame.KEYDOWN: (InputDevice.KEYBOARD, CommandPhase.START),
    pygame.KEYUP: (InputDevice.KEYBOARD, CommandPhase.END),
    pygame.MOUSEBUTTONDOWN: (InputDevice.MOUSE, CommandPhase.START),
    pygame.MOUSEBUTTONUP: (InputDevice.MOUSE, CommandPhase.END),
}


def system_input_player(world: esper.World, event: pygame.event.Event,
                        do_action: Callable[[CInputCommand], None]) -> None:
    """Traduce eventos de pygame a acciones del juego (patron Command).

    La escena recibe el CInputCommand con su nombre y su fase; nunca ve codigos de tecla.
    """
    if event.type not in _PHASE_BY_EVENT:
        return
    device, phase = _PHASE_BY_EVENT[event.type]
    pressed = event.key if device == InputDevice.KEYBOARD else event.button
    for _, c_input in world.get_component(CInputCommand):
        if c_input.device == device and c_input.key == pressed:
            c_input.phase = phase
            do_action(c_input)
