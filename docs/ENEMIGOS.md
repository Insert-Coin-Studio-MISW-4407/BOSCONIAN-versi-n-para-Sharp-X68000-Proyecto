# Enemigos

Replica de los enemigos de Bosconian con los recursos del curso (`assets/img/naves.png`).
Todos los numeros estan en `assets/cfg/enemies.json` y la distribucion de los niveles en
`assets/cfg/level_01.json`, `assets/cfg/level_02.json` y `assets/cfg/level_03.json`.

## Resumen

| Enemigo | Sprite del atlas | Comportamiento | Puntos |
|---|---|---|---|
| Asteroide | 6 rocas (amarillas y grises) | Fijo; se destruye de un disparo | 10 |
| Mina cosmica | Mina verde de 2 cuadros | Fija y parpadea; al destruirse deja una onda que arrasa lo cercano | 20 |
| Canon de estacion | Canon de 3 cuadros + chatarra | Carga (rojo) y dispara a la nave si esta a su alcance | 200 |
| Estacion | Ilustracion completa de la base | Cae con sus 6 canones o con un disparo al nucleo abierto | 1500 |
| Nave tipo I | Caza azul | Persigue a la nave con giro limitado | 50 |
| Nave tipo P | Chevron morado | Mas rapida y gira mejor | 60 |
| Nave tipo E | Misil naranja | La mas rapida | 70 |
| Formacion | Lider P + 4 escoltas I en V | El lider vuela despacio; derribarlo primero rompe la formacion | 100 + 1000 de bonus |
| Nave espia | Nave verde | Observa a la nave y huye; si escapa, condicion RED | 800 |

## Estaciones

La estructura sale de la ilustracion completa del atlas (`base_frame`, fondo magenta).
`TextureService.get_keyed_region` vuelve transparente el magenta y vacia los circulos de
los canones y del nucleo, que son entidades aparte encima de la estructura:

- **Nucleo** (`CBaseCore`, `system_base_core`): ciclo cerrado -> abriendose -> abierto ->
  cerrandose. Solo es vulnerable abierto; cerrado absorbe las balas. Lleva `CBase` y
  `CTagBase`, asi el radar ubica la estacion en su centro.
- **Canones** (`CBaseCannon`, `system_base_cannon`): reposo -> carga -> disparo. Solo cargan
  si la nave esta a menos de `base.fire.range`. Al destruirse quedan como chatarra.
- **Estructura**: solo decorativa, en la capa de dibujo mas baja.

## Naves enemigas

- `system_enemy_spawner` las lanza fuera de pantalla **en el camino de la nave** (la nave del
  jugador nunca se detiene; si salieran por detras casi no la alcanzarian). En RED salen mas
  seguido y hay mas formaciones. Hay un maximo de naves vivas y cada nivel el intervalo baja.
- `system_chaser` gira el rumbo hacia la nave como mucho `turn_rate` grados por segundo: se
  pasan de largo y hay que esquivarlas. El sprite mira en 16 direcciones como en el arcade.
- Las que quedan a mas de `spawner.despawn_distance` se retiran.

### Formaciones

`create_formation` crea un lider con `CFormationLeader` + `CTagFormation` (punto rojo del radar)
y cuatro escoltas con `CFormationMember`. `system_formation` pone cada escolta en su puesto,
girado segun el rumbo del lider. Si el lider cae, cada escolta recibe un `CChaser` y persigue
por su cuenta.

### Nave espia

`CSpy` + `system_spy`: se acerca (APPROACH), da vueltas alrededor de la nave durante
`report_time` (WATCH) y huye mas rapido que la nave (FLEE). Si se aleja mas de
`escape_distance` llama a `system_report_spy` y la condicion queda en RED hasta el nivel
siguiente. Aparece cada `spy.interval` segundos y nunca hay dos a la vez.

## Colisiones

| Choque | Resultado |
|---|---|
| Bala del jugador vs enemigo | `system_bullet_hits`: la bala desaparece y el enemigo se destruye (nucleo cerrado: solo absorbe) |
| Onda de mina vs enemigo | `system_blast`: destruye asteroides, minas y naves dentro del radio; encadena otras minas |
| Nave vs enemigo | `system_player_hits`: muere la nave y el enemigo (salvo el nucleo) |
| Nave vs bala enemiga u onda | muere la nave |

Todas las pruebas usan `collide_world` / `distance`, que miden por el camino mas corto del
mundo toroidal.

## Vidas y niveles

- Cada muerte descuenta una vida; la nave reaparece donde exploto, parpadeando e
  invulnerable (`player.json > death`). Sin vidas: GAME OVER y vuelta al menu.
- Sin estaciones en pie: LEVEL CLEAR, se limpia y repuebla el mundo y arranca el nivel
  siguiente con el siguiente archivo de `scenes.json > LEVEL_01 > levels`. Tras el tercero,
  la secuencia vuelve a `level_01.json` y el numero mostrado continua creciendo.

## Alerta

| Condicion | Cuando |
|---|---|
| GREEN | ninguna nave enemiga cerca |
| YELLOW | alguna nave enemiga a menos de `alert.detect_radius` |
| RED | la espia escapo o se acabo el tiempo de la ronda (queda enclavada) |
