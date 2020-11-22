import edgin_around_rendering as ear
from . import animator, connector, controls, gui, lan, proxy, window


class Game:
    """The main class of the client (frontend) side of the game."""

    def __init__(self, resource_dir: str) -> None:
        ear.init()

        self.proxy = proxy.Proxy()

        self.scene = ear.Scene()
        self.world = ear.WorldExpositor(resource_dir, (600, 800))
        self.gui = gui.Gui(self.world, self.scene, self.proxy, resource_dir)
        self.controls = controls.Controls(self.world, self.gui, self.proxy)
        self.animator = animator.Animator(self.scene, self.world, self.gui, resource_dir)

        self.window = window.Window(self.gui, self.controls, self.animator)
        self.connector = connector.Connector(self.animator)

    def run(self) -> None:
        print("Welcome to Edgin' Around!")

        srv = lan.list_servers()
        if len(srv) < 1:
            return

        addr = srv[0][0]
        sock = self.connector.start(addr)
        self.proxy.set_socket(sock)

        self.window.run()
        self.connector.stop()

        print("Bye!")
