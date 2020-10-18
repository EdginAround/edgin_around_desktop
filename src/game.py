from . import animator, connector, controls, gui, lan, proxy, scene, window, world

class Game:
    """The main class of the client (frontend) side of the game."""

    def __init__(self) -> None:
        self.proxy = proxy.Proxy()

        self.scene = scene.Scene()
        self.world = world.World(self.scene)
        self.gui = gui.Gui(self.world, self.proxy)
        self.controls = controls.Controls(self.world, self.gui, self.proxy)
        self.animator = animator.Animator(self.scene, self.world, self.gui)

        self.window = window.Window(self.gui, self.controls, self.animator)
        self.connector = connector.Connector(self.animator)

    def run(self) -> None:
        print('Welcome to Edgin\' Around!')

        srv = lan.list_servers()
        if len(srv) < 1:
            return

        addr = srv[0][0]
        sock = self.connector.start(addr)
        self.proxy.set_socket(sock)

        self.window.run()
        self.connector.stop()

