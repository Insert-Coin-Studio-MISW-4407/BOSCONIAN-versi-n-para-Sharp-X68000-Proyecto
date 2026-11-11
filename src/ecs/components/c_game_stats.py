"""Estado de puntuacion y recursos de la partida (datos ECS)."""


class CGameStats:
    """Puntuacion actual, record, vidas y ronda mostrados en el panel."""

    def __init__(self, high_score: int = 0, lives: int = 3,
                 round_number: int = 1,
                 high_score_path: str = "save/high_score.json") -> None:
        self.score = 0
        self.high_score = max(0, int(high_score))
        self.lives = max(0, int(lives))
        self.round_number = max(1, int(round_number))
        self.high_score_path = high_score_path
