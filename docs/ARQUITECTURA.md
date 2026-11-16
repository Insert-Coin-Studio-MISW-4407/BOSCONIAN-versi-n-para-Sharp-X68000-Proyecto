# Arquitectura

Documento vivo: cada PR que agregue componentes, sistemas o escenas lo actualiza.

## Game loop

`GameEngine.run` (`src/engine/game_engine.py`) repite cada frame:

1. **Tiempo**: `clock.tick(framerate)` y `delta_time` en segundos (limitado a 1/20 s).
2. **Eventos**: `pygame.QUIT` cierra el juego; el resto va a la escena activa.
3. **Update**: la escena corre sus sistemas. Si pidio un cambio de escena, se aplica
   al final del frame para no destruir el mundo ECS mientras se recorre.
4. **Draw**: la escena dibuja y se hace `flip`.
5. `await asyncio.sleep(0)`: cede el control al navegador (pygbag).

## Escenas

`Scene` (`src/engine/scenes/scene.py`) es la base. Cada escena:

- tiene su propio `esper.World`, asi nada se filtra de una escena a otra;
- crea las entidades de input al entrar y pone su musica (clave `music` en `scenes.json`);
- implementa los ganchos `do_create`, `do_action`, `do_update`, `do_draw`, `do_clean`.

El motor construye la escena a partir del campo `type` de `scenes.json` usando el
diccionario `_SCENE_TYPES`.

| Tipo | Clase | Uso |
|---|---|---|
| `TEXT` | `TextScene` | titulo, instrucciones, creditos: imagenes + textos + mapa accion->escena |
| `PLAY` | `PlayScene` | un nivel: mundo toroidal, camara, estrellas y entidades del juego |

## Mundo toroidal

El mundo mide `world.json > size` y da la vuelta en ambos ejes. Todas las cuentas
de distancia pasan por `src/engine/world_math.py`, que toma siempre el camino mas
corto (heredado del mundo cilindrico de Defender y extendido al eje y):

- `system_world_wrap` envuelve la posicion de **todas** las entidades cada frame.
- `world_to_screen` prueba tambien la copia "dando la vuelta", asi lo que esta junto
  a la costura se dibuja bien aunque la camara este al otro lado.
- `collide_world` compara centros por la distancia mas corta.

## Camara y parallax

`CCamera` guarda la esquina superior izquierda de la vista en coordenadas de mundo,
el rectangulo de pantalla donde se dibuja el juego y `delta`, cuanto se movio en el
ultimo frame. Las estrellas viven en coordenadas de vista y se desplazan
`-delta * parallax`, envolviendose en la vista: el fondo es infinito y no salta al
cruzar la costura del mundo. Cada capa tiene su factor de parallax.

## Componentes

| Componente | Datos |
|---|---|
| `CTransform` | posicion en coordenadas de mundo |
| `CVelocity` | velocidad en px/s |
| `CSurface` | textura y recorte (`area`) |
| `CText` | texto, fuente, tamano, color, posicion de pantalla, alineacion |
| `CBlink` | intervalo y duracion del parpadeo (None = infinito) |
| `CInputCommand` | nombre de accion, tecla/boton, fase (patron Command) |
| `CTagUI` | marca un sprite dibujado en coordenadas de pantalla |
| `CTagPlayer` | marca la nave del jugador |
| `CTagPlayerBullet` | marca las balas del jugador |
| `CTagSpecialBullet` | marca las balas del disparo especial (no cuentan para el limite del simple) |
| `CHeading` | hacia donde apunta la nave (8 sentidos, vector unitario) |
| `CShipMotion` | velocidad maxima, aceleracion, velocidad de crucero y direccion pedida por las flechas |
| `CWeapon` | velocidad y limite de balas, desplazamiento de la boca, recarga y apertura del especial |
| `CRotatingSprite` | recorte del atlas que se gira segun `CHeading` |
| `CCamera` | esquina de la vista en el mundo, rectangulo de pantalla, delta del frame |
| `CStar` | posicion en la vista, color, factor de parallax, temporizador de parpadeo |
| `CGameStats` | puntuacion, record, vidas, ronda y ruta de persistencia del record |
| `CStageTimer` | limite y tiempo restante de la ronda; indica si expiro |
| `CAlertState` | condicion GREEN/YELLOW/RED y enclavamiento de RED; marca si la espia ya reporto |
| `CTagBase` | marca el nucleo de cada estacion para el minimapa |
| `CTagFormation` | marca el lider de cada formacion para el minimapa |
| `CAnimation` | cuadros de una animacion del atlas, tiempo por cuadro, repetir o borrar al terminar |
| `CEnemy` | lo que las balas del jugador destruyen: tipo, puntos y paleta de explosion |
| `CBlast` | onda expansiva de una mina (dura un frame) |
| `CBase` | estacion: estructura, canones, canones vivos y bonus (en la entidad del nucleo) |
| `CBaseCore` | ciclo abierto/cerrado del nucleo; solo es vulnerable abierto |
| `CBaseCannon` | canon de estacion: cuadros, chatarra y ciclo reposo/carga/disparo |
| `CLifetime` | segundos que le quedan a la entidad (balas enemigas) |
| `CTagEnemyBullet` | marca las balas enemigas |
| `CInvulnerable` | la nave no puede morir durante unos segundos (al reaparecer) |
| `CChaser` | velocidad, giro maximo y direcciones del sprite de una nave que persigue |
| `CEnemySpawner` | temporizadores de la proxima nave/formacion y de la proxima espia, escala por ronda |
| `CFormationLeader` / `CFormationMember` | lider con sus escoltas y bonus / puesto de cada escolta |
| `CSpy` | estado de la nave espia (acercarse, observar, huir) |

## Sistemas

| Sistema | Responsabilidad |
|---|---|
| `system_input_player` | traduce eventos de pygame a acciones con nombre |
| `system_blink` | alterna la visibilidad de lo que tiene `CBlink` |
| `system_rendering_ui` | dibuja sprites `CTagUI` en pantalla |
| `system_rendering_text` | dibuja `CText` con fuentes del Service Locator |
| `system_movement` | integra la velocidad en la posicion |
| `system_world_wrap` | envuelve las posiciones en ambos ejes |
| `system_camera` | centra la camara en la nave y calcula su delta |
| `system_ship_motion` | movimiento con aceleracion: la velocidad persigue a la deseada (arrancar, frenar y girar toman tiempo) |
| `system_player_sprite` | gira el sprite de la nave hacia donde apunta, sin mover su centro |
| `system_bullet_offscreen` | borra las balas que salen por completo de la pantalla (respeta la costura del mundo) |
| `system_weapon_cooldown` | descuenta la recarga del disparo especial |
| `system_stars` | parallax y parpadeo de las estrellas |
| `system_rendering_stars` | dibuja las estrellas visibles |
| `system_rendering` | dibuja sprites de mundo recortados a la vista, ordenados por `CSurface.layer` |
| `system_animation` | avanza los cuadros de `CAnimation`; borra las explosiones al terminar |
| `system_lifetime` | borra las entidades cuyo `CLifetime` se agoto |
| `system_base_core` | ciclo del nucleo de las estaciones |
| `system_base_cannon` | los canones cargan y disparan a la nave cuando esta a su alcance |
| `system_enemy_spawner` / `system_spy_spawner` | lanzan naves, formaciones y espias en el camino de la nave |
| `system_chaser` | las naves giran hacia la nave con giro limitado; las lejanas se retiran |
| `system_formation` | las escoltas siguen a su lider; si cae, persiguen por su cuenta |
| `system_spy` | la espia observa y huye; si escapa llama a `system_report_spy` |
| `system_bullet_hits` / `system_blast` | balas del jugador y ondas de minas contra enemigos (`destroy_enemy`) |
| `system_player_hits` / `system_invulnerable` | choques y balas que matan a la nave / fin de la invulnerabilidad |
| `system_rendering_panel` | dibuja puntaje, record, vidas, temporizador, alerta y minimapa en el panel derecho |
| `system_stage_timer` | descuenta el limite global de la ronda, tambien cuando no hay enemigos |
| `system_alert` | prioriza y enclava RED; YELLOW con naves enemigas cerca (`enemies_near`) |
| `system_report_spy` | activa y enclava RED cuando la nave espia escapa |
| `system_add_score` / `system_lose_life` | actualiza puntuacion/record y vidas |
| `system_start_next_round` | reinicia temporizador/alerta y cambia el numero de ronda |

## Servicios (Service Locator)

| Servicio | Recurso |
|---|---|
| `TextureService` | imagenes y recortes del atlas (con espejo, giro y tinte opcionales; recortes con fondo transparente), cargados una sola vez |
| `SoundService` | efectos; tolera archivos ausentes |
| `MusicService` | musica en streaming; no reinicia la pista si ya suena |
| `FontService` | TTF o fuentes de mapa de bits |

## Archivos de configuracion

| Archivo | Contenido |
|---|---|
| `window.json` | titulo, resolucion 256x208, color de fondo, fps |
| `assets.json` | recursos a precargar |
| `audio.json` | volumen de musica y efectos |
| `input.json` | mapeo accion -> teclas |
| `scenes.json` | escena inicial y definicion de cada escena |
| `world.json` | tamano del mundo y capas, colores y parpadeo de las estrellas |
| `sprites.json` | recortes de la hoja de sprites del curso (`frames` para animaciones) |
| `enemies.json` | explosiones, asteroides, minas, estaciones, naves, formaciones, espia, generador y alerta |
| `player.json` | movimiento (`max_speed`, `acceleration`, `cruise_speed`), disparos (`fire`) y muerte (`death`) de la nave |
| `window.json > layout.panel.hud` | tipografia y paleta de colores del panel/minimapa |
| `level_XX.json` | incluye `starting_lives`, `round_number`, `alert_time_limit_seconds` y `high_score_path` |
| `level_XX.json` | contenido de cada nivel, incluido el desbloqueo del cañon triple (`triple_cannon`) |
| `level_XX.json` | `bases` (posiciones de las estaciones), `obstacles` (asteroides y minas) y `rounds` (paso de ronda) |

## Enemigos

Detalle de cada enemigo, sus colisiones y el flujo de vidas y rondas en `docs/ENEMIGOS.md`.
