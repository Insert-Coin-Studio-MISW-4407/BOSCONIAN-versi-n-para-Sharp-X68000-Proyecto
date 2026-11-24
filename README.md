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

## Publicar en itch.io

El proyecto ya incluye el bucle asincrono y la configuracion necesaria para exportarlo
a HTML con `pygbag 0.9.2`.

### Probar en el navegador

```powershell
python -m pygbag --ume_block 1 --width 768 --height 624 --title "COSMONIAN" .
```

Tambien puedes ejecutar `serve_web.bat` desde Windows. Pygbag iniciara un servidor local
en `http://localhost:8000`.

### Crear el archivo para itch.io

```powershell
python -m pygbag --build --archive --ume_block 1 --width 768 --height 624 --app_name cosmonian --package com.insertcoinstudio.cosmonian --title "COSMONIAN" .
```

El archivo listo es `build/web.zip`. En itch.io:

1. Crea o abre el proyecto y selecciona **HTML** como tipo de proyecto.
2. Sube `build/web.zip`.
3. Activa **This file will be played in the browser**.
4. Establece el marco recomendado en `768 x 624` (factor exacto 3x sobre la resolucion 256 x 208).
5. Activa **Embed options -> Enable fullscreen** si quieres mostrar el boton de pantalla completa.
6. Guarda y publica la pagina.

Desde Windows puedes crear el paquete directamente con `build_web.bat`.

## Controles

| Accion | Tecla |
|---|---|
| Mover | Flechas |
| Disparar / Start | Z (o Enter en menus) |
| Alternar disparo principal normal/triple (pruebas) | U |
| Pausa | P |
| Volver / salir | ESC |
| Instrucciones / creditos (menu) | I / C |

### Depuracion

| Tecla | Efecto |
|---|---|
| F1 | Muestra las cajas de colision |

Todas las teclas se configuran en `assets/cfg/input.json`.

## Enemigos

Estaciones con seis canones y nucleo, asteroides, minas cosmicas, naves tipo I/P/E,
formaciones con lider y la nave espia que activa la condicion RED. Destruye todas las
estaciones para pasar de nivel. Los tres mapas se recorren en bucle con un numero de
nivel creciente. Detalle en `docs/ENEMIGOS.md`.

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
