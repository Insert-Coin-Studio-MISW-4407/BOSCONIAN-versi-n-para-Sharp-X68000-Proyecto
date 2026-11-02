class CWeapon:
    """Armas de la nave (todos los numeros vienen de player.json).

    - bullet_speed: velocidad de las balas (px/s).
    - max_bullets: maximo de balas del disparo simple vivas al mismo tiempo.
    - muzzle_offset: distancia (px) desde el centro de la nave a la que sale cada bala.
    - triple_spread: apertura (grados) del cañon triple.
    """

    def __init__(self, fire_cfg: dict) -> None:
        self.bullet_speed = fire_cfg["bullet_speed"]
        self.max_bullets = fire_cfg["max_bullets"]
        self.muzzle_offset = fire_cfg["muzzle_offset"]
        self.triple_spread = fire_cfg["triple_spread"]
