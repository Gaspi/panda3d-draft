import random
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import PerspectiveLens, TextNode, TextureStage, \
    TexGenAttrib

def add_instructions(pos, msg):
    """Function to put instructions on the screen."""
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1),
                        parent=base.a2dTopLeft, align=TextNode.ALeft,
                        pos=(0.08, -pos - 0.04), scale=.05)

def add_title(text):
    """Function to put title on the screen."""
    return OnscreenText(text=text, style=1, pos=(-0.1, 0.09), scale=.08,
                        parent=base.a2dBottomRight, align=TextNode.ARight,
                        fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1))

class Game(ShowBase):
    """Sets up the game, camera, controls, and loads models."""
    def __init__(self):
        ShowBase.__init__(self)

        # Display instructions
        add_title("Panda3D Simple Game")
        add_instructions(0.06, "[Esc]: Quit")
        add_instructions(0.12, "[E]: Move Forward")
        add_instructions(0.18, "[S]: Move Left")
        add_instructions(0.24, "[F]: Move Right")
        add_instructions(0.30, "[D]: Move Back")
        add_instructions(0.36, "[R]: Jump")
        add_instructions(0.42, "Arrow Keys: Look Around")

        # Setup controls
        self.keys = {}
        for key in ['arrow_left', 'arrow_right', 'arrow_up', 'arrow_down',
                    'e', 'd', 's', 'f']:
            self.keys[key] = 0
            self.accept(key, self.push_key, [key, 1])
            self.accept('shift-%s' % key, self.push_key, [key, 1])
            self.accept('%s-up' % key, self.push_key, [key, 0])
        self.accept('r', self.jump)
        self.accept('escape', __import__('sys').exit, [0])
        self.disableMouse()

        # Setup camera
        lens = PerspectiveLens()
        lens.setFov(60)
        lens.setNear(0.01)
        lens.setFar(1000.0)
        self.cam.node().setLens(lens)
        self.camera.setPos(-9, -0.5, 1)
        self.heading = -95.0
        self.pitch = 0.0

        # Load level geometry
        self.level_model = self.loader.loadModel('models/level')
        self.level_model.reparentTo(self.render)
        self.level_model.setTexGen(TextureStage.getDefault(),
                                   TexGenAttrib.MWorldPosition)
        self.level_model.setTexProjector(TextureStage.getDefault(),
                                         self.render, self.level_model)
        self.level_model.setTexScale(TextureStage.getDefault(), 4)

        # Main loop
        self.taskMgr.add(self.update, 'main loop')

    def jump(self):
        pass

    def push_key(self, key, value):
        """Stores a value associated with a key."""
        self.keys[key] = value

    def update(self, task):
        """Updates the camera based on the keyboard input. Once this is
        done, then the CellManager's update function is called."""
        dt = globalClock.getDt()
        dx = dt * 3 * -self.keys['s'] + dt * 3 * self.keys['f']
        dz = dt * 3 * self.keys['d'] + dt * 3 * -self.keys['e']
        self.camera.setPos(self.camera, dx, -dz, 0)
        self.heading += (dt * 90 * self.keys['arrow_left'] +
                         dt * 90 * -self.keys['arrow_right'])
        self.pitch += (dt * 90 * self.keys['arrow_up'] +
                       dt * 90 * -self.keys['arrow_down'])
        self.camera.setHpr(self.heading, self.pitch, 0)
        return task.cont


game = Game()
game.run()
