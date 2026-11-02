class CRotatingSprite:
    """Sprite que se gira segun hacia donde apunta la entidad (CHeading).

    Guarda de donde se recorta de la hoja de sprites y el angulo con el que se dibujo
    por ultima vez, para volver a recortar solo cuando la nave cambia de direccion.
    """

    def __init__(self, sheet: str, rect: list[int]) -> None:
        self.sheet = sheet
        self.rect = rect
        self.angle = 0.0
