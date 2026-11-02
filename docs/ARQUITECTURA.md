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
| `system_rendering` | dibuja sprites de mundo recortados a la vista |

## Servicios (Service Locator)

| Servicio | Recurso |
|---|---|
| `TextureService` | imagenes y recortes del atlas (con espejo y giro opcionales), cargados una sola vez |
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
| `sprites.json` | recortes de la hoja de sprites del curso |
| `player.json` | movimiento (`max_speed`, `acceleration`, `cruise_speed`) y disparos (`fire`) de la nave |
| `level_XX.json` | contenido de cada nivel, incluida su habilidad especial (`special_ability`) |
