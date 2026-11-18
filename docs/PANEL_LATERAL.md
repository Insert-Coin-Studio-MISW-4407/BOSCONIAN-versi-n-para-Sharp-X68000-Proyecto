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
| `system_report_spy` | Activa RED cuando la nave espia escapa con su reporte. |
| `system_start_next_round` | Reinicia temporizador/alerta y actualiza el numero de nivel. |
| `system_rendering_panel` | Dibuja el panel y el minimapa a partir de los componentes ECS. |

## Reglas de alerta

1. `RED` tiene prioridad sobre cualquier otro estado.
2. El temporizador global activa `RED` al llegar a cero, incluso sin enemigos ni nave espia.
3. La nave espia activa el mismo estado llamando `system_report_spy(world)` cuando consigue escapar.
4. `RED` permanece enclavada hasta que el flujo de nivel llame `system_start_next_round(world, numero, limite)`.
5. `YELLOW` se activa cuando hay naves enemigas cerca de la nave (`enemies_near`).
6. El temporizador se detiene durante la pausa porque `PlayScene.do_update` no ejecuta sistemas mientras esta pausado.

## Integracion con los enemigos

La rama de enemigos ya usa estos puntos (ver `docs/ENEMIGOS.md`):

- `destroy_enemy` llama `system_add_score` con los puntos de cada enemigo.
- `PlayScene._kill_player` llama `system_lose_life`.
- `system_alert` recibe `enemy_detected=enemies_near(...)`: YELLOW con naves enemigas cerca.
- `system_spy` llama `system_report_spy` cuando la nave espia escapa.
- El nucleo de cada estacion lleva `CTagBase` y el lider de cada formacion `CTagFormation`.
- `PlayScene._start_next_level` llama `system_start_next_round` y carga el siguiente mapa.

## Persistencia

El record se carga desde `save/high_score.json` al entrar a la escena y se guarda al superar la mejor puntuacion. Esta persistencia usa el sistema de archivos local; en una compilacion web de Pygbag, la permanencia entre recargas dependera de configurar almacenamiento persistente del navegador.

## Configuracion

- `assets/cfg/window.json > layout.panel.hud`: fuente, tamanos y paleta del panel.
- `assets/cfg/level_01.json > starting_lives`: vidas iniciales.
- `assets/cfg/level_01.json > round_number`: numero inicial del nivel mostrado.
- `assets/cfg/level_01.json > alert_time_limit_seconds`: limite temporal global.
- `assets/cfg/level_01.json > high_score_path`: ruta del record.
