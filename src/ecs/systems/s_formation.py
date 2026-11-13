import esper
import pygame

from src.ecs.components.c_chaser import CChaser
from src.ecs.components.c_enemy import CEnemy
from src.ecs.components.c_formation import CFormationMember
from src.ecs.components.c_heading import CHeading
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity

_UP = pygame.Vector2(0, -1)


def system_formation(world: esper.World) -> None:
    """Las escoltas ocupan su puesto respecto al lider y miran hacia donde el mira.

    Si el lider ya no existe la formacion se rompe: cada escolta sigue por su cuenta
    persiguiendo a la nave. Se ejecuta despues del movimiento para no ir un frame atras.
    """
    c_m: CFormationMember
    for entity, (c_m, c_t, c_s, c_h, c_v) in world.get_components(
            CFormationMember, CTransform, CSurface, CHeading, CVelocity):
        if not world.entity_exists(c_m.leader) or not world.has_component(c_m.leader, CEnemy):
            world.remove_component(entity, CFormationMember)
            world.add_component(entity, CChaser(c_m.speed, c_m.turn_rate))
            c_v.vel = pygame.Vector2(c_h.direction) * c_m.speed
            continue
        l_t = world.component_for_entity(c_m.leader, CTransform)
        l_s = world.component_for_entity(c_m.leader, CSurface)
        l_h = world.component_for_entity(c_m.leader, CHeading)
        leader_center = l_t.pos + pygame.Vector2(l_s.area.size) / 2
        slot = leader_center + c_m.offset.rotate(_UP.angle_to(l_h.direction))
        c_t.pos = slot - pygame.Vector2(c_s.area.size) / 2
        c_h.direction = pygame.Vector2(l_h.direction)
