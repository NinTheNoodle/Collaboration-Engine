__author__ = 'Docopoper'

from globals import *
import glob
import base_engine
import os


class Loader:
    """deals with loading levels and importing objects"""
    def goto_section(self, section_name):
        tags, section = base_engine.loaded_sections[section_name]
        engine.section_tags = tags
        for module_name, class_name, x, y, settings in section:
            engine.instance_create(module_name, class_name, x, y, **settings)


    def level_load(self, name):
        folder_load(engine.path + "/Levels/" + name, base_engine.objects_local)
        for section in glob.glob(engine.path + "/Levels/" + name + "/*.lvl"):
            section_load(section)

        #Load the first section listed as a start section
        for section_name, section in base_engine.loaded_sections.iteritems():
            if "StartSection" in section[0]:
                self.goto_section(section_name)
                break

    def global_load(self):
        folder_load(engine.path + "/Global", base_engine.objects_global)

loader = Loader()

def section_load(path):
    section_name = os.path.basename(path).split(".")[0]

    section_list = []
    section_tags = set()
    base_engine.loaded_sections[section_name] = (section_tags, section_list)

    new_object = None
    new_object_class = None
    with open(path) as fl:
        for line in fl:
            line = line.rstrip('\r\n')

            if line.strip() == "":
                continue

            if line[0] == " ":
                #Attempt to add a new setting change to the object - ignoring invalid lines
                if new_object is None: continue
                try:
                    key, value = line[1:].split(":", 1)
                except ValueError: continue

                new_object[4][key] = eval(value, {})

            elif line[0] == "*":
                #Apply section tags that aren't blank
                if len(line) > 1:
                    section_tags.add(line[1:])
            else:
                #Attempt to add a new object - ignoring invalid lines
                new_object = None
                try:
                    module, object_name, x, y = line.split("|", 3)
                except ValueError: continue
                try:
                    new_object_class = engine.get_class(module, object_name)
                except KeyError: continue

                new_object = (module, object_name, int(x), int(y), {})
                section_list.append(new_object)



def resource_pack_load(path, dictionary):

        for spr in glob.glob(path + "/Sprites/*.png"):
            img = pyglet.image.load(spr)
            dictionary["sprite"][(os.path.basename(path), os.path.basename(spr).split(".")[0])] = img

        for sound in glob.glob(path + "/Sounds/*.wav"):
            snd = pyglet.media.load(sound, streaming=False)
            dictionary["sound"][(os.path.basename(path), os.path.basename(sound).split(".")[0])] = snd

        for music in glob.glob(path + "/Music/*.*"):
            mus = pyglet.media.load(music, streaming=True)
            dictionary["music"][(os.path.basename(path), os.path.basename(music).split(".")[0])] = mus

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
loader.level_load("My First Level")

#########################################################################


# class TestObj:
#     x = 0
#     y = 0
#
#     spr = engine.get_sprite("Res pack test", "Vulpix")
#
#     settings = ["spr"]
#
#     def on_create(self):
#         self.sprite = self.spr
#
#     def on_tick(self):
#         if key.MOTION_LEFT in engine.keys_down: self.x -= 2
#         if key.MOTION_RIGHT in engine.keys_down: self.x += 2
#         if key.MOTION_UP in engine.keys_down: self.y += 2
#         if key.MOTION_DOWN in engine.keys_down: self.y -= 2
#
#         if key.G in engine.keys_pressed: print base_engine.objects_global
#         if key.P in engine.keys_pressed: engine.get_sound('Res pack test', 'bing1').play()
#         if key.M in engine.keys_pressed: engine.get_music('Res pack test', 'File Select').play()
#         if key.Z in engine.keys_pressed: engine.editor_mode = True
#         if key.N in engine.keys_pressed: engine.instance_create("Res pack test2", "test", 0, 0)
#         self.sprite.x, self.sprite.y = self.x, self.y
#
#     def on_editor_tick(self):
#         if key.Z in engine.keys_pressed: engine.editor_mode = False
#
#     def on_draw(self):
#         self.sprite.draw()
#
#     def on_editor_draw(self):
#         self.on_draw()
#
# engine.register_class_global("Testmod", "Test", TestObj)
#engine.instance_create("Res pack test", "test", 0, 0, sprite="Vulpix")