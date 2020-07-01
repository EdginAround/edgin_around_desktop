import glooey

from . import defs


class StatLabel(glooey.Label):
    custom_color = '#eeeeec'
    custom_background_color = '#204a87'
    custom_font_size = 12
    custom_alignment = 'center'
    custom_bold = True

class Dials(glooey.VBox):
    custom_alignment = 'top right'
    custom_margin = 10

    def __init__(self):
        super().__init__()

        self.labels = [StatLabel('Hunger: --/--')]
        for label in self.labels:
           self.add(label)

    def set_stats(self, stats: defs.Stats):
        self.labels[0].set_text(f'Hunger: {stats.hunger}/{stats.max_hunger}')

