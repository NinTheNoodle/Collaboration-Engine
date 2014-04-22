from globals import *
import base_engine

__author__ = 'Docopoper'


class Sprite(object):

    def __init__(self, spr):
        self.spr = pyglet.sprite.Sprite(spr)
        self.width = self.spr.width
        self.height = self.spr.height
        self.bbox = (-self.width / 2, -self.height / 2, self.width / 2, self.height / 2)

    #wrapper properties for the underlying sprite
    @property
    def visible(self): return self.spr.visible
    @visible.setter
    def visible(self, value): self.spr.visible = value

    @property
    def scale(self): return self.spr.scale
    @scale.setter
    def scale(self, value): self.spr.scale = value

    @property
    def opacity(self): return self.spr.opacity
    @opacity.setter
    def opacity(self, value): self.spr.opacity = value

    def draw(self, x, y):
        self.spr.x, self.spr.y = x, y
        self.spr.draw()


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