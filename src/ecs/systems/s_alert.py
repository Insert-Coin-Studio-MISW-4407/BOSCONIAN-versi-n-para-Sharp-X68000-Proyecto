"""Calcula GREEN/YELLOW/RED."""
import esper
import pygame

from src.ecs.components.c_alert_state import CAlertState
from src.ecs.components.c_chaser import CChaser
from src.ecs.components.c_stage_timer import CStageTimer
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.engine.world_math import distance


def enemies_near(world: esper.World, target: pygame.Vector2 | None,
                 world_size: pygame.Vector2, radius: float) -> bool:
    """True si alguna nave enemiga esta a menos de `radius` de la nave (condicion YELLOW)."""
    if target is None:
        return False
    for _, (_, c_t, c_s) in world.get_components(CChaser, CTransform, CSurface):
        if distance(c_t.pos + pygame.Vector2(c_s.area.size) / 2, target, world_size) <= radius:
            return True
    return False


def is_red_alert(world: esper.World) -> bool:
    return any(alert.condition == CAlertState.RED for _, alert in world.get_component(CAlertState))


def system_alert(world: esper.World, enemy_detected: bool = False) -> None:
    """Actualiza la condicion del panel.

    RED tiene prioridad y queda activa hasta que system_start_next_round la reinicie.
    Puede activarse por el limite temporal global o, en el futuro, por el reporte
    de una nave espia. `enemy_detected` permite integrar enemigos futuros sin
    acoplar este sistema a una implementacion que todavia no existe.
    """
    alert_items = world.get_component(CAlertState)
    if not alert_items:
        return

    alert = alert_items[0][1]
    timer_items = world.get_component(CStageTimer)
    timer_expired = bool(timer_items and timer_items[0][1].expired)

    if timer_expired or alert.spy_reported or alert.red_latched:
        alert.condition = CAlertState.RED
        alert.red_latched = True
        return

    alert.condition = CAlertState.YELLOW if enemy_detected else CAlertState.GREEN


def system_report_spy(world: esper.World) -> None:
    """Punto de integracion futuro: la nave espia consiguio enviar su reporte."""
    for _, alert in world.get_component(CAlertState):
        alert.spy_reported = True
        alert.red_latched = True
        alert.condition = CAlertState.RED
