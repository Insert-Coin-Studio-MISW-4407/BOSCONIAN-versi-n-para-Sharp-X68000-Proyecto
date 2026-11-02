import esper

from src.ecs.components.c_weapon import CWeapon


def system_weapon_cooldown(world: esper.World, delta_time: float) -> None:
    c_w: CWeapon
    for _, c_w in world.get_component(CWeapon):
        c_w.special_time_left = max(0.0, c_w.special_time_left - delta_time)
