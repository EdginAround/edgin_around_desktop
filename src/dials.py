import pyglet
import glooey

from . import defs, inventory, media


INVENTORY_IMAGES = ('left_hand', 'right_hand', 'empty_slot', 'axe', 'rocks', 'log')
EMPTY_SLOT = 'empty_slot'
LEFT_HAND = 'left_hand'
RIGHT_HAND = 'right_hand'

pyglet.resource.path = [media.DIR_INVENTORY]


class StatLabel(glooey.Label):
    custom_color = '#eeeeec'
    custom_background_color = '#204a87'
    custom_font_size = 12
    custom_alignment = 'center'
    custom_bold = True


class Dials(glooey.Board):
    custom_alignment = 'fill'

    def __init__(self) -> None:
        super().__init__()

        # Load textures
        self.tex = {}
        for image_name in INVENTORY_IMAGES:
            texture = pyglet.resource.texture(image_name + '.png')
            self.tex[image_name] = texture

        # Stats display
        self.labels_box = glooey.VBox()
        self.labels = [StatLabel('Hunger: --/--')]
        for label in self.labels:
            self.labels_box.add(label)
        self.add(self.labels_box, top_percent=1.0, right_percent=1.0)

        # Hand Inventory buttons
        self.left_hand_button = glooey.Image()
        self.left_hand_button.set_image(self.tex[LEFT_HAND])
        self.add(self.left_hand_button, bottom=0, left=0)

        self.right_hand_button = glooey.Image()
        self.right_hand_button.set_image(self.tex[RIGHT_HAND])
        self.add(self.right_hand_button, bottom=0.0, right_percent=1.0)

        # Clothing inventory buttons
        self.inventory_box = glooey.HBox()
        self.inventory_buttons = list()
        for i in range(defs.INVENTORY_SIZE):
            button = glooey.Image()
            button.set_image(self.tex[EMPTY_SLOT])
            self.inventory_box.add(button)
            self.inventory_buttons.append(button)
        self.add(self.inventory_box, bottom=0.0, center_x_percent=0.5)

    def set_stats(self, stats: defs.Stats) -> None:
        self.labels[0].set_text(f'Hunger: {stats.hunger}/{stats.max_hunger}')

    def set_inventory(self, inventory: inventory.Inventory) -> None:
        image = LEFT_HAND
        if inventory.left_hand is not None:
            image = inventory.left_hand.image
        self.left_hand_button.set_image(self.tex[image])

        image = RIGHT_HAND
        if inventory.right_hand is not None:
            image = inventory.right_hand.image
        self.right_hand_button.set_image(self.tex[image])

        for i, entry in enumerate(inventory.entries):
            image = EMPTY_SLOT
            if entry is not None:
                image = entry.image
            self.inventory_buttons[i].set_image(self.tex[image])

