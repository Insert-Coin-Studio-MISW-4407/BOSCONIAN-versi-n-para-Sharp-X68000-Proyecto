class CEnemySpawner:
    """Generador de naves enemigas de la ronda: cuenta el tiempo hasta la proxima."""

    def __init__(self, first_delay: float) -> None:
        self.timer = first_delay
