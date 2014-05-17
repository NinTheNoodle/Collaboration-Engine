__author__ = 'Docopoper'

from globals import *
import os

if __name__ == '__main__':
    if os.getenv("PROFILE") is not None:
        import subprocess
        from pycallgraph import PyCallGraph
        from pycallgraph import Config
        from pycallgraph import GlobbingFilter
        from pycallgraph.output import GraphvizOutput
        from time import sleep

        config = Config()
        config.trace_filter = GlobbingFilter()#include=['Objects.*', "pyglet.*", "Ctrl.*"],
                                             #exclude=['Objects.Menu.*'])

        if os.getenv("PNG") is None:
            graphviz = GraphvizOutput(output_file='filter_exclude.xdot', output_type='xdot')
        else:
            graphviz = GraphvizOutput(output_file='filter_exclude.png', output_type='png')

        with PyCallGraph(output=graphviz, config=config):
            pyglet.app.run()

        if os.getenv("PNG") is None:
            sleep(1)
            subprocess.call("python -m xdot \"" + os.path.dirname(os.path.realpath(__file__)) + "\\filter_exclude.xdot\"")
    else:
        pyglet.app.run()