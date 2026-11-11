"""Sistemas del temporizador global de ronda."""
import esper

from src.ecs.components.c_stage_timer import CStageTimer
from src.ecs.components.c_alert_state import CAlertState
from src.ecs.components.c_game_stats import CGameStats


def system_stage_timer(world: esper.World, delta_time: float) -> None:
    """Descuenta el tiempo global; no depende de la existencia de enemigos."""
    elapsed = max(0.0, float(delta_time))
    for _, timer in world.get_component(CStageTimer):
        if timer.expired:
            continue
        timer.remaining = max(0.0, timer.remaining - elapsed)
        timer.expired = timer.remaining <= 0.0


def system_start_next_round(world: esper.World, round_number: int,
                            time_limit: float) -> None:
    """Reinicia temporizador y alerta al comenzar otra ronda.

    Conserva la puntuacion, el record y las vidas. La progresion de rondas puede
    llamar este sistema cuando se incorpore al flujo del juego.
    """
    duration = max(0.0, float(time_limit))
    for _, timer in world.get_component(CStageTimer):
        timer.duration = duration
        timer.remaining = duration
        timer.expired = duration <= 0.0
    for _, alert in world.get_component(CAlertState):
        alert.condition = CAlertState.GREEN
        alert.spy_reported = False
        alert.red_latched = False
    for _, stats in world.get_component(CGameStats):
        stats.round_number = max(1, int(round_number))
