# COSMONIAN - Proyecto final MISW-4407

Shooter espacial multidireccional en Python con pygame-ce y arquitectura **ECS**
(esper 2.5). Equipo **Insert Coin Studio**.

## Ejecutar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

`esper/` viene incluido en el repo (version 2.5).

## Controles

| Accion | Tecla |
|---|---|
| Mover | Flechas |
| Disparar / Start | Z (o Enter en menus) |
| Especial | X |
| Pausa | P |
| Volver / salir | ESC |
| Instrucciones / creditos (menu) | I / C |

Todas las teclas se configuran en `assets/cfg/input.json`.

## Resolucion

256x208 nativos (`assets/cfg/window.json`). La ventana usa `pygame.SCALED`, asi que
se puede agrandar sin que el juego deje de dibujar a resolucion original.

## Estructura

```
main.py                         punto de entrada asincrono (compatible con pygbag)
esper/                          libreria esper 2.5 incluida
assets/cfg/                     TODA la configuracion del juego en JSON
assets/img/ mus/ snd/ fnt/      recursos (ver assets/LICENCIAS.txt)
src/engine/game_engine.py       game loop + gestor de escenas
src/engine/scenes/              Scene (base) y sus implementaciones
src/engine/service_locator.py   acceso unico a texturas, sonidos, musica y fuentes
src/engine/services/            un servicio por tipo de recurso
src/create/prefab_creator.py    fabrica de entidades
src/ecs/components/             componentes (solo datos)
src/ecs/components/tags/        componentes marcadores sin datos
src/ecs/systems/                sistemas (solo logica)
docs/                           arquitectura y documentos de entrega
```

## Patrones aplicados

| Patron | Donde |
|---|---|
| **ECS** | `src/ecs/`: los componentes solo tienen datos y los sistemas solo logica |
| **Game Loop** | `GameEngine.run`: tiempo -> eventos -> update -> draw |
| **Command** | `CInputCommand` + `system_input_player`; las escenas reciben nombres de accion, nunca teclas |
| **Service Locator** | `ServiceLocator`; ningun sistema carga archivos por su cuenta |
| **Escena** | `Scene` y sus implementaciones; cada escena tiene su propio mundo ECS |

## Flujo de trabajo

- Una rama por avance (`feature/...`) y un PR hacia `main`.
- Commits en espanol explicando el cambio.
