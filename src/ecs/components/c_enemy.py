class CEnemy:
    """Todo lo que las balas del jugador pueden destruir y que mata a la nave al tocarla.

    - kind: "asteroid", "mine", "cannon", "core", "ship"... decide como se destruye.
    - points: puntos que da al destruirse.
    - explosion: paleta de explosion de enemies.json ("enemy" u "obstacle").
    """

    def __init__(self, kind: str, points: int, explosion: str = "enemy") -> None:
        self.kind = kind
        self.points = points
        self.explosion = explosion
