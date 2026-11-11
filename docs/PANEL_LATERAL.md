# Panel lateral inspirado en Bosconian

## Alcance de esta entrega

El panel ocupa la columna derecha ya reservada en `assets/cfg/window.json` (64 x 208 px). No cambia el area jugable (192 x 208), el movimiento de la nave, la camara, el mundo toroidal, los disparos ni el fondo de estrellas.

El panel muestra:

- `HI-SCORE`: record persistente en `save/high_score.json`.
- `1UP`: puntuacion de la partida actual.
- `FORMATION`: cantidad de entidades marcadas como formacion; por ahora muestra `NONE`.
- `CONDITION`: estado `GREEN`, `YELLOW` o `RED`.
- `RADAR`: minimapa del mundo completo con jugador y puntos de extension para bases/formaciones.
- `SHIPS`: vidas restantes.
- `ROUND` y `TIME`: ronda actual y segundos restantes del temporizador global.

## Sistemas ECS

| Componente/sistema | Responsabilidad |
|---|---|
| `CGameStats` | Datos de puntaje, record, vidas y ronda. |
| `system_add_score` | Suma puntos y persiste un nuevo record. |
| `system_lose_life` | Descuenta una vida sin bajar de cero. |
| `CStageTimer` / `system_stage_timer` | Cuenta regresiva global independiente de enemigos. |
| `CAlertState` / `system_alert` | Calcula GREEN/YELLOW/RED y enclava RED. |
| `system_report_spy` | Punto de integracion futuro para el reporte de una nave espia. |
| `system_start_next_round` | Reinicia temporizador/alerta y actualiza el numero de ronda. |
| `system_rendering_panel` | Dibuja el panel y el minimapa a partir de los componentes ECS. |

## Reglas de alerta

1. `RED` tiene prioridad sobre cualquier otro estado.
2. El temporizador global activa `RED` al llegar a cero, incluso sin enemigos ni nave espia.
3. Una futura nave espia activa el mismo estado llamando `system_report_spy(world)` cuando consiga reportar.
4. `RED` permanece enclavada hasta que el flujo de ronda llame `system_start_next_round(world, numero, limite)`.
5. `YELLOW` se puede activar pasando `enemy_detected=True` a `system_alert`. En esta entrega no se crean enemigos, por lo que la escena pasa `False` y el estado normal es `GREEN`.
6. El temporizador se detiene durante la pausa porque `PlayScene.do_update` no ejecuta sistemas mientras esta pausado.

## Integracion futura

- Al destruir una entidad que otorgue puntos: `system_add_score(world, puntos)`.
- Al perder una nave: `system_lose_life(world)`.
- Al detectarse enemigos: llamar `system_alert(world, enemy_detected=True)` desde la integracion del sistema de enemigos.
- Al escapar la nave espia: `system_report_spy(world)`.
- Para que bases/formaciones aparezcan en el radar, sus prefabs deben incluir `CTransform` y, respectivamente, `CTagBase` o `CTagFormation`. No se crean esas entidades en esta entrega.

## Persistencia

El record se carga desde `save/high_score.json` al entrar a la escena y se guarda al superar la mejor puntuacion. Esta persistencia usa el sistema de archivos local; en una compilacion web de Pygbag, la permanencia entre recargas dependera de configurar almacenamiento persistente del navegador.

## Configuracion

- `assets/cfg/window.json > layout.panel.hud`: fuente, tamanos y paleta del panel.
- `assets/cfg/level_01.json > starting_lives`: vidas iniciales.
- `assets/cfg/level_01.json > round_number`: numero inicial de ronda.
- `assets/cfg/level_01.json > alert_time_limit_seconds`: limite temporal global.
- `assets/cfg/level_01.json > high_score_path`: ruta del record.
