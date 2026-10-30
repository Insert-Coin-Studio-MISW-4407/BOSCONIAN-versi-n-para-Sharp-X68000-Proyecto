class CBlink:
    """Game feel: parpadeo de una entidad (textos de "pulsa start", invulnerabilidad).

    `duration` en None significa que parpadea para siempre.
    """

    def __init__(self, interval: float, duration: float | None = None) -> None:
        self.interval = interval
        self.remaining = duration
        self.timer = interval
        self.visible = True
