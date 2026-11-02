import pygame


class CShipMotion:
    """Parametros del movimiento con aceleracion de la nave (todos vienen de player.json).

    - max_speed: velocidad (px/s) a la que se acelera mientras hay una flecha presionada.
    - acceleration: cuanto cambia la velocidad por segundo (px/s^2). Tambien frena y gira.
    - cruise_speed: velocidad que mantiene al soltar las flechas. En Bosconian la nave
      siempre esta en movimiento; con 0 la nave frena hasta detenerse.
    - input_dir: direccion que piden las flechas ahora mismo (0,0 si no hay ninguna).
    """

    def __init__(self, max_speed: float, acceleration: float, cruise_speed: float) -> None:
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.cruise_speed = cruise_speed
        self.input_dir = pygame.Vector2(0, 0)
