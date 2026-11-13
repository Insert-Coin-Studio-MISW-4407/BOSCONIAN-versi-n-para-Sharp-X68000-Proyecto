class CInvulnerable:
    """La nave no puede morir durante `remaining` segundos (al reaparecer)."""

    def __init__(self, seconds: float) -> None:
        self.remaining = seconds
