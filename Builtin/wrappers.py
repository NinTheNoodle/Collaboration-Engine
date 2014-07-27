from globals import *
import base_engine

__author__ = 'Docopoper'

next_layer_id = 0

class Layer(object):
    layer_id = -1
    name = ""
    x = 0
    y = 0
    hspeed = 0
    vspeed = 0
    _disabled = False
    cell_size = 64

    def on_create(self):
        global next_layer_id
        self.layer_id = next_layer_id
        next_layer_id += 1
        self.instances = set()
        self.instance_dict = {}

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value):
        was_disabled = self._disabled
        self._disabled = value
        for inst in self.instances:
            if inst.temporary and value:
                inst.destroy()
            else:
                if value and not inst._disabled and not was_disabled:
                    base_engine.engine.instance_disable(inst, True)
                elif not value and not inst._disabled and was_disabled:
                    base_engine.engine.instance_enable(inst, True)

class Drawable(object):
    def __init__(self, drawing_layer):
        self.require_draw = False
        self.update_group(drawing_layer)

    @property
    def visible(self): return False
    @visible.setter
    def visible(self, value): pass

    @property
    def disabled(self): return True
    @disabled.setter
    def disabled(self, value): pass

    def destroy(self):
        try:
            self.group.drawables.remove(self)
        except AttributeError: pass

    def update_group(self, drawing_layer):
        try:
            self.group.drawables.remove(self)
        except AttributeError: pass
        self.group = renderer.drawing_layers[drawing_layer]
        self.group.drawables.add(self)

class FakeSprite(object):
    visible = True
    scale = 1
    rotation = 0
    x = 0
    y = 0
    opacity = 255
    color = (255, 255, 255)
    _texture = None
    _image = None

    @property
    def position(self):
        return self.x, self.y
    @position.setter
    def position(self, value):
        self.x, self.y = value

class Sprite(Drawable):

    _disabled = True

    def __init__(self, spr, drawing_layer):
        super(Sprite, self).__init__(drawing_layer)
        self._sprite = FakeSprite()
        self._image = spr
        self._sprite.width = self._image.width
        self._sprite.height = self._image.height
        self.bbox = (-self._sprite.width / 2, -self._sprite.height / 2, self._sprite.width / 2, self._sprite.height / 2)

    #wrapper properties for the underlying sprite
    @property
    def x(self): return self._sprite.x
    @x.setter
    def x(self, value): self._sprite.x = value

    @property
    def y(self): return self._sprite.y
    @y.setter
    def y(self, value): self._sprite.y = value

    @property
    def angle(self): return self._sprite.rotation
    @angle.setter
    def angle(self, value): self._sprite.rotation = value

    @property
    def position(self): return self._sprite.position
    @position.setter
    def position(self, value): self._sprite.position = value

    @property
    def visible(self): return self._sprite.visible
    @visible.setter
    def visible(self, value): self._sprite.visible = value

    @property
    def scale(self): return self._sprite.scale
    @scale.setter
    def scale(self, value): self._sprite.scale = value

    @property
    def opacity(self): return self._sprite.opacity
    @opacity.setter
    def opacity(self, value): self._sprite.opacity = value

    @property
    def disabled(self): return self._disabled
    @disabled.setter
    def disabled(self, value):
        if value != self._disabled:
            self._disabled = value
            if value:
                spr = FakeSprite()
                spr.scale = self._sprite.scale
                spr.rotation = self._sprite.rotation
                spr.opacity = self._sprite.opacity
                spr.visible = self._sprite.visible
                spr.position = self._sprite.position
                spr.color = self._sprite.color
                self._sprite.delete()
                self._sprite = spr
            else:
                spr = pyglet.sprite.Sprite(self._image, batch=renderer.batch, group=self.group)
                spr.scale = self._sprite.scale
                spr.rotation = self._sprite.rotation
                spr.opacity = self._sprite.opacity
                spr.visible = self._sprite.visible
                spr.position = self._sprite.position
                spr.color = self._sprite.color
                self._sprite = spr


    def draw(self, x, y):
        if not self.require_draw:
            self.require_draw = True
            renderer.drawables_to_show.append(self)
            if (x, y) != self._sprite.position:
                self._sprite.position = (x, y)
        else:
            raise AssertionError("Drawing the same instance of a sprite twice in one frame")


class Sound:

    def __init__(self, snd):
        self.snd = snd

    def play(self):
        self.snd.play()


class Music:

    def __init__(self, mus):
        self.mus = mus
        self.player = pyglet.media.Player()
        self.player.queue(self.mus)
        self.player.eos_action = self.player.EOS_LOOP

    def play(self):
        if base_engine.engine.current_music == self: return

        if base_engine.engine.current_music is not None:
            base_engine.engine.current_music.player.pause()
            base_engine.engine.current_music.player.seek(0)

        self.player.volume = 1
        global transitioning_music_from, transitioning_music_to, transitioning_music_time
        transitioning_music_from = set()
        transitioning_music_to = None
        transitioning_music_time = 0
        self.player.play()

        base_engine.engine.current_music = self

    def replace(self, fade_time=1):
        current_music = base_engine.engine.current_music

        if current_music is None:
            return self.play()

        if current_music == self: return

        self.player.volume = 0
        #seek to the relative position on the other track - accounting for length differences
        if self.mus.duration is not None and current_music.mus.duration is not None:
            start_pos = (0.1 + current_music.player.time) * (self.mus.duration / current_music.mus.duration)
            self.player.seek(start_pos - 0.1)

        self.player.play()

        #delay the playing of the new music by 0.1 seconds in order to hide the squeak of the music seeking
        def delayed_play(dt):
            global transitioning_music_to,transitioning_music_time
            transitioning_music_time = max(fade_time, 0.001)
            self.player.volume = 0
            if base_engine.engine.current_music is not None:
                transitioning_music_from.add(base_engine.engine.current_music)

            self.player.play()
            transitioning_music_to = self
            try:
                transitioning_music_from.remove(self)
            except KeyError: pass
            base_engine.engine.current_music = self

        pyglet.clock.schedule_once(delayed_play, 0.1)

transitioning_music_from = set()
transitioning_music_to = None
transitioning_music_time = 0

#fade in and out music as required every tick
def music_tick(dt):
    global transitioning_music_to

    #reduce the volume of all the music tracks currently fading out
    for music in transitioning_music_from.copy():
        music.player.volume -= dt / transitioning_music_time
        if music.player.volume <= 0:
            music.player.pause()
            music.player.seek(0)
            music.player.volume = 1
            transitioning_music_from.remove(music)

    #increace the volume of the music track currently fading in
    if transitioning_music_to is not None:
        transitioning_music_to.player.volume += dt / transitioning_music_time
        if transitioning_music_to.player.volume >= 1:
            transitioning_music_to.player.volume = 1
            transitioning_music_to = None