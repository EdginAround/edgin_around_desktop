from . import animator, controls, engine, executor, generator, gui, proxy, scene, window, world

class Game:
    def __init__(self) -> None:
        self.proxy = proxy.Proxy()

        self.scene = scene.Scene()
        self.world = world.World(self.scene)
        self.gui = gui.Gui(self.world, self.proxy)
        self.controls = controls.Controls(self.world, self.gui, self.proxy)
        self.animator = animator.Animator(self.scene, self.world, self.gui)
        self.window = window.Window(self.gui, self.controls, self.animator)

        self.state = generator.WorldGenerator().generate(100.0)
        self.engine = engine.Engine(self.proxy, self.state)
        self.runner = executor.Runner(self.engine)

        self.proxy.set_ends(self.engine, self.animator)

    def run(self) -> None:
        self.runner.start()
        self.window.run()
        self.runner.stop()

