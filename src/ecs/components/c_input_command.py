from enum import Enum


class CommandPhase(Enum):
    START = 0
    END = 1


class InputDevice(Enum):
    KEYBOARD = 0
    MOUSE = 1


class CInputCommand:
    """Patron Command: asocia una tecla/boton con el NOMBRE de una accion del juego.

    La escena solo reacciona a nombres de accion, nunca a teclas concretas, asi que
    el mapeo se puede cambiar desde input.json sin tocar la logica.
    """

    def __init__(self, name: str, key: int,
                 device: InputDevice = InputDevice.KEYBOARD) -> None:
        self.name = name
        self.key = key
        self.device = device
        self.phase = CommandPhase.END
