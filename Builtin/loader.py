__author__ = 'Docopoper'

from globals import *
import glob
import base_engine
import os
import wrappers


class Loader:
    """deals with loading levels and importing objects"""
    def goto_section(self, section_name):


        tags, section, layers = base_engine.loaded_sections[section_name]
        engine.section_tags = tags

        for layer_name, settings in layers:
            if layer_name not in engine.layers:
                engine.layers[layer_name] = layer = wrappers.Layer()

                for key, value in settings.iteritems():
                    setattr(layer, key, value)

                layer.on_create()

        for module_name, class_name, layer_name, settings in section:
            engine.instance_create(module_name, class_name, layer_name, **settings)


    def level_load(self, name, section_name=None):
        if name.lower() == "global":
            raise NameError()

        engine.layers = {}
        base_engine.objects_local = base_engine.dictionary_template.copy()
        folder_load(engine.path + "/Levels/" + name, base_engine.objects_local)
        for section in glob.glob(engine.path + "/Levels/" + name + "/*.lvl"):
            section_load(section)

        if section_name is None:
            #Load the first section listed as a start section
            for section_name, section in base_engine.loaded_sections.iteritems():
                if "StartSection" in section[0]:
                    self.goto_section(section_name)
                    break
        else:
            self.goto_section(section_name)

    def global_load(self):
        folder_load(engine.path + "/Global", base_engine.objects_global)

loader = Loader()

def section_load(path):
    section_name = os.path.basename(path).split(".")[0]

    section_list = []
    section_tags = {}
    section_layers = []
    base_engine.loaded_sections[section_name] = (section_tags, section_list, section_layers)

    new_object = None
    new_object_attributes = None

    with open(path) as fl:
        for line in fl:
            line = line.rstrip('\r\n')

            if line == "":
                continue

            line_type = line[0]
            line = line[1:]

            if line_type == " ":
                #Attempt to add a new setting change to the object - ignoring invalid lines
                if new_object is None or new_object_attributes is None: continue
                try:
                    key, value = line.split(":", 1)
                except ValueError: continue

                new_object_attributes[key] = eval(value, {})

            elif line_type == "*":
                #Apply section tags that aren't blank
                if len(line) > 1:
                    data = line.split(":", 1)

                    if len(data) >= 2:
                        section_tags[data[0]] = eval(data[1])
                    else:
                        section_tags[data[0]] = True
            elif line_type == ">":
                #Attempt to add a new class - ignoring invalid lines
                new_object = None
                new_object_attributes = None
                try:
                    module, object_name, layer_name = line.split("|", 2)
                except ValueError: continue
                try:
                    engine.get_class(module, object_name)
                except KeyError: continue

                new_object_attributes = {}
                new_object = (module, object_name, layer_name, new_object_attributes)
                section_list.append(new_object)
            elif line_type == "@":
                #Attempt to add a new layer - ignoring invalid lines
                new_object_attributes = {}
                new_object = (line, new_object_attributes)
                section_layers.append(new_object)
            elif line_type == "#":
                continue #Ignore comments



def resource_pack_load(path, dictionary):

        module_name = os.path.basename(path)
        level_name = os.path.basename(path[:-len(module_name) - 1])

        try:
            os.mkdir(engine.path + "/Temp/" + level_name)
        except: pass

        for spr in glob.glob(path + "/Sprites/*.png"):
            img = pyglet.image.load(spr).get_texture().get_transform(flip_y=True)
            img.anchor_x = img.width / 2
            img.anchor_y = img.height / 2
            dictionary["sprite"][(module_name, os.path.splitext(os.path.basename(spr))[0])] = img

        for sound in glob.glob(path + "/Sounds/*.wav"):
            snd = pyglet.media.load(sound, streaming=False)
            dictionary["sound"][(module_name, os.path.splitext(os.path.basename(sound))[0])] = snd

        for music in glob.glob(path + "/Music/*.*"):
            mus = wrappers.Music(load_sound(music, level_name, module_name, True))
            dictionary["music"][(module_name, os.path.splitext(os.path.basename(music))[0])] = mus

        for resource in glob.glob(path + "/Resources/*.*"):
            dictionary["resource"][(module_name, os.path.splitext(os.path.basename(resource))[0])] = os.path.normcase(resource)

        for obj in glob.glob(path + "/Objects/*.py"):
            object_name = os.path.splitext(os.path.basename(obj))[0]
            file_dict = {}
            execfile(obj, file_dict)
            try:
                engine._register_class_dict(module_name, object_name, file_dict[object_name], dictionary)
            except KeyError: pass


def folder_load(path, dictionary):
    """load the contents of the given folder into the given dictionary"""
    paths = [path + "/" + x
           for x in os.listdir(path)
           if os.path.isdir(path + "/" + x)]

    for path in paths:
        resource_pack_load(path, dictionary)

#Deal with AVBin not loading sometimes by dumping music into wav files
def load_sound(fname, level_name, module_name, streaming):
    try: #Try loading the mp3 normally
        sound = pyglet.media.load(fname, streaming=streaming)
    except:
        temp_path = engine.path + "/Temp/" + level_name + "/" + module_name

        try: #If that fails try loading a temporary wav file that may have been created
            temp_fname = os.path.splitext(os.path.basename(fname))[0]
            sound = pyglet.media.load(temp_path + "/" + temp_fname + ".wav", streaming=False)
        except: #If that fails - create a temporary wav file
            try:
                os.mkdir(temp_path)
            except: pass
            sound = pyglet.media.load(dump_wav(fname, temp_path), streaming=False)

    return sound

#Taken from http://pymedia.org/tut/src/dump_wav.py.html
def dump_wav(name, temp_dir):
    from pymedia.audio import acodec
    from pymedia import muxer
    import wave, string, os

    path, fname_ext = os.path.split(name)
    fname, ext = os.path.splitext(fname_ext)
    output_path = temp_dir + "/" + fname + ".wav"
    #Open demuxer first

    dm = muxer.Demuxer(ext[1:].lower())
    dec = None
    f = open(name,'rb')
    snd = None
    s = " "
    while len(s):
        s = f.read(20000)
        if len(s):
            frames = dm.parse(s)
            for fr in frames:
                if dec is None:
                    #Open decoder

                    dec = acodec.Decoder(dm.streams[0])
                r = dec.decode(fr[1])
                if r and r.data:
                    if snd is None:
                        snd = wave.open(output_path, "wb")
                        snd.setparams((r.channels, 2, r.sample_rate, 0, "NONE",""))

                    snd.writeframes(r.data)
    return output_path

loader.global_load()
#loader.level_load("My First Level")
loader.level_load("Demo Level")