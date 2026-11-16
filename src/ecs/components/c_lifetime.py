class CLifetime:
    """La entidad se borra al cabo de `remaining` segundos (balas enemigas)."""

    def __init__(self, seconds: float) -> None:
        self.remaining = seconds
