"""Estado de alerta del panel. RED queda enclavada hasta iniciar otra ronda."""


class CAlertState:
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"

    def __init__(self) -> None:
        self.condition = self.GREEN
        # Se activa cuando la nave espia logra escapar con su reporte (system_report_spy).
        self.spy_reported = False
        self.red_latched = False
