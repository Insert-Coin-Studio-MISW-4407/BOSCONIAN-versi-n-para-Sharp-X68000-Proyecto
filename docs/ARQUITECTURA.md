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

## Sistemas

| Sistema | Responsabilidad |
|---|---|
| `system_input_player` | traduce eventos de pygame a acciones con nombre |
| `system_blink` | alterna la visibilidad de lo que tiene `CBlink` |
| `system_rendering_ui` | dibuja sprites `CTagUI` en pantalla |
| `system_rendering_text` | dibuja `CText` con fuentes del Service Locator |

## Servicios (Service Locator)

| Servicio | Recurso |
|---|---|
| `TextureService` | imagenes, cargadas una sola vez |
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
| `world.json` | parametros del fondo de estrellas (pendiente de usar) |
