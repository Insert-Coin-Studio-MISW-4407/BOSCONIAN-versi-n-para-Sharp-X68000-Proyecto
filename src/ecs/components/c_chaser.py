class CChaser:
    """Nave enemiga que persigue a la nave del jugador.

    - speed: velocidad constante (px/s).
    - turn_rate: cuanto puede girar por segundo (grados); con poco giro la nave se
      pasa de largo y tiene que dar la vuelta, que es lo que permite esquivarla.
    - directions: el sprite solo mira en estas direcciones (16 en el arcade).
    """

    def __init__(self, speed: float, turn_rate: float, directions: int = 16) -> None:
        self.speed = speed
        self.turn_rate = turn_rate
        self.directions = directions
