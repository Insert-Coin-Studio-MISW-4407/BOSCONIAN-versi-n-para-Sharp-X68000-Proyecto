"""Temporizador global de la ronda, independiente de enemigos o de la nave espia."""


class CStageTimer:
    def __init__(self, duration: float) -> None:
        self.duration = max(0.0, float(duration))
        self.remaining = self.duration
        self.expired = self.remaining <= 0.0
