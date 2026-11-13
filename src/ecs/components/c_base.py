class CBase:
    """Estacion enemiga. Vive en la entidad del nucleo (asi el radar la ubica en su centro).

    - frame: entidad de la estructura (arcos y brazos), solo decorativa.
    - cannons: entidades de los seis canones, vivos o destruidos.
    - alive_cannons: canones que quedan; con 0 la estacion explota.
    - points: bonus por destruir la estacion.
    """

    def __init__(self, frame: int, cannons: list[int], points: int) -> None:
        self.frame = frame
        self.cannons = cannons
        self.alive_cannons = len(cannons)
        self.points = points
