import esper

from src.ecs.components.c_blink import CBlink


def system_blink(world: esper.World, delta_time: float) -> None:
    """Game feel: alterna la visibilidad y quita el componente al terminar."""
    for entity, c_blink in world.get_component(CBlink):
        c_blink.timer -= delta_time
        if c_blink.timer <= 0:
            c_blink.timer += c_blink.interval
            c_blink.visible = not c_blink.visible
        if c_blink.remaining is None:
            continue
        c_blink.remaining -= delta_time
        if c_blink.remaining <= 0:
            world.remove_component(entity, CBlink)
