"""Estado de puntuacion y recursos de la partida (datos ECS)."""


class CGameStats:
    """Puntuacion actual, record, vidas y ronda mostrados en el panel.

    `next_extra_life` es el puntaje con el que se gana la proxima vida (0 = nunca) y
    `extra_life_every` cuanto sube ese umbral despues de cada vida ganada.
    """

    def __init__(self, high_score: int = 0, lives: int = 3,
                 round_number: int = 1,
                 high_score_path: str = "save/high_score.json",
                 extra_life_first: int = 0, extra_life_every: int = 0) -> None:
        self.score = 0
        self.high_score = max(0, int(high_score))
        self.lives = max(0, int(lives))
        self.round_number = max(1, int(round_number))
        self.high_score_path = high_score_path
        self.next_extra_life = max(0, int(extra_life_first))
        self.extra_life_every = max(0, int(extra_life_every))
