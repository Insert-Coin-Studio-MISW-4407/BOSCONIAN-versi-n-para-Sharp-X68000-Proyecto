import esper

from src.ecs.components.c_camera import CCamera
from src.ecs.components.c_star import CStar


def system_stars(world: esper.World, c_cam: CCamera, delta_time: float) -> None:
    """Parallax y parpadeo del fondo de estrellas.

    Cada estrella se desplaza en sentido contrario a la camara, escalado por su capa,
    y se envuelve dentro de la vista para que el fondo nunca se acabe.
    """
    view_w, view_h = c_cam.view.size
    for _, c_star in world.get_component(CStar):
        c_star.pos -= c_cam.delta * c_star.parallax
        c_star.pos.x %= view_w
        c_star.pos.y %= view_h
        c_star.blink_timer -= delta_time
        if c_star.blink_timer <= 0:
            c_star.blink_timer += c_star.blink_interval
            c_star.visible = not c_star.visible
