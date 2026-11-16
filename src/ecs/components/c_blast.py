class CBlast:
    """Onda expansiva de una mina cosmica: dura un solo frame.

    Todo enemigo suelto (asteroides, minas, naves) a menos de `radius` del centro se
    destruye, y la nave del jugador tambien si esta dentro. Asi una mina puede
    encadenar a otras, como en el original.
    """

    def __init__(self, radius: float) -> None:
        self.radius = radius
