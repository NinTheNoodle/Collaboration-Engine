__author__ = 'Docopoper'

from globals import *
import glob
import base_engine
import os


class Loader:
    """deals with loading levels and importing objects"""
    def level_load(self, name):
        folder_load(engine.path + "/Levels/" + name, base_engine.objects_local)

    def global_load(self):
        folder_load(engine.path + "/Global", base_engine.objects_global)

loader = Loader()


def resource_pack_load(path, dictionary):

        for spr in glob.glob(path + "/Sprites/*.png"):
            img = pyglet.image.load(spr)
            dictionary["sprite"][(os.path.basename(path), os.path.basename(spr).split(".")[0])] = img

        for sound in glob.glob(path + "/Sounds/*.wav"):
            snd = pyglet.media.load(sound, streaming=False)
            dictionary["sound"][(os.path.basename(path), os.path.basename(sound).split(".")[0])] = snd

        for music in glob.glob(path + "/Music/*.*"):
            try:
                mus = pyglet.media.load(music, streaming=True)
                dictionary["music"][(os.path.basename(path), os.path.basename(music).split(".")[0])] = mus
            except pyglet.media.avbin.AVbinException: pass

        for resource in glob.glob(path + "/Resources/*.*"):
            dictionary["resource"][(os.path.basename(path), os.path.basename(resource).split(".")[0])] = os.path.normcase(resource)

        for obj in glob.glob(path + "/Objects/*.py"):
            object_name = os.path.basename(obj).split(".")[0]
            file_dict = {}
            execfile(obj, file_dict)
            try:
                dictionary["class"][(os.path.basename(path), object_name)] = file_dict[object_name]
            except KeyError: pass


def folder_load(path, dictionary):
    """load the contents of the given folder into the given dictionary"""
    paths = [path + "/" + x
           for x in os.listdir(path)
           if os.path.isdir(path + "/" + x)]

    for path in paths:
        resource_pack_load(path, dictionary)

loader.global_load()

#########################################################################


class TestObj:
    x = 0
    y = 0

    spr = engine.get_sprite("Res pack test", "Vulpix")

    settings = ["spr"]

    def on_create(self):
        self.sprite = pyglet.sprite.Sprite(self.spr)

    def on_tick(self):
        if key.MOTION_LEFT in engine.keys_down: self.x -= 2
        if key.MOTION_RIGHT in engine.keys_down: self.x += 2
        if key.MOTION_UP in engine.keys_down: self.y += 2
        if key.MOTION_DOWN in engine.keys_down: self.y -= 2

        if key.G in engine.keys_pressed: print base_engine.objects_global
        if key.P in engine.keys_pressed: engine.get_sound('Res pack test', 'bing1').play()
        if key.M in engine.keys_pressed: engine.get_music('Res pack test', 'File Select').play()
        if key.Z in engine.keys_pressed: engine.editor_mode = True
        if key.N in engine.keys_pressed: engine.instance_create("Res pack test", "test", 0, 0)
        self.sprite.x, self.sprite.y = self.x, self.y

    def on_editor_tick(self):
        if key.Z in engine.keys_pressed: engine.editor_mode = False

    def on_draw(self):
        self.sprite.draw()

    def on_editor_draw(self):
        self.on_draw()

engine.register_class_global("Testmod", "Test", TestObj)
engine.instance_create("Testmod", "Test", 0, 0)