class CSpy:
    """Nave espia: se acerca, observa a la nave dando vueltas y huye a reportar.

    APPROACH -> WATCH (dura `report_time`) -> FLEE. Si al huir se aleja mas de
    `escape_distance` envia su reporte: la condicion pasa a RED.
    """

    APPROACH = "APPROACH"
    WATCH = "WATCH"
    FLEE = "FLEE"

    def __init__(self, cfg: dict) -> None:
        self.speed = cfg["speed"]
        self.flee_speed = cfg["flee_speed"]
        self.watch_radius = cfg["watch_radius"]
        self.escape_distance = cfg["escape_distance"]
        self.report_time = cfg["report_time"]
        self.state = self.APPROACH
        self.timer = 0.0
        # Sentido de giro alrededor de la nave (1 horario, -1 antihorario)
        self.orbit = 1
