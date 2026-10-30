from src.create.prefab_creator import create_text, create_ui_image
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.engine.scenes.scene import Scene

QUIT = "QUIT"


class TextScene(Scene):
    """Pantalla estatica de imagenes y textos: titulo, instrucciones, creditos...

    Todo sale de scenes.json. `actions` asocia el nombre de una accion de input.json
    con la escena a la que lleva (o "QUIT" para cerrar el juego), asi agregar una
    pantalla nueva no requiere escribir codigo.
    """

    def do_create(self) -> None:
        for image_cfg in self.cfg.get("images", []):
            create_ui_image(self.ecs_world, image_cfg)
        for text_cfg in self.cfg.get("texts", []):
            create_text(self.ecs_world, text_cfg)

    def do_action(self, c_input: CInputCommand) -> None:
        if c_input.phase != CommandPhase.START:
            return
        target = self.cfg.get("actions", {}).get(c_input.name)
        if target == QUIT:
            self.engine.is_running = False
        elif target is not None:
            self.switch_scene(target)
