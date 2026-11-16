import pygame


class CFormationLeader:
    """Lider de una formacion: guarda a sus escoltas y el bonus por derribarlo primero."""

    def __init__(self, members: list[int], bonus: int) -> None:
        self.members = members
        self.bonus = bonus


class CFormationMember:
    """Escolta que vuela pegada a su lider.

    `offset` es su puesto con el lider mirando hacia arriba; se gira con el rumbo del
    lider. `speed` y `turn_rate` son los que usa al romperse la formacion.
    """

    def __init__(self, leader: int, offset: pygame.Vector2, speed: float,
                 turn_rate: float) -> None:
        self.leader = leader
        self.offset = pygame.Vector2(offset)
        self.speed = speed
        self.turn_rate = turn_rate
