import esper

from src.ecs.components.c_lifetime import CLifetime


def system_lifetime(world: esper.World, delta_time: float) -> None:
    for entity, c_l in world.get_component(CLifetime):
        c_l.remaining -= delta_time
        if c_l.remaining <= 0:
            world.delete_entity(entity)
