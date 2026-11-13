class CEnemySpawner:
    """Generador de naves enemigas de la ronda: cuenta el tiempo hasta la proxima nave
    (o formacion) y, aparte, hasta la proxima nave espia."""

    def __init__(self, first_delay: float, spy_first_delay: float) -> None:
        self.timer = first_delay
        self.spy_timer = spy_first_delay
