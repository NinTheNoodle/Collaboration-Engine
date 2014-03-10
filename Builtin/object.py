__author__ = 'Docopoper'

from globals import *


class Object:
    x = 0
    y = 0

    def on_draw_editor(self):
        self.on_draw()