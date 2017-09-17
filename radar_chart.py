#modified from: https://matplotlib.org/examples/api/radar_chart.html

"""
======================================
Radar chart (aka spider or star chart)
======================================

This example creates a radar chart, also known as a spider or star chart [1]_.

Although this example allows a frame of either 'circle' or 'polygon', polygon
frames don't have proper gridlines (the lines are circles instead of polygons).
It's possible to get a polygon grid by setting GRIDLINE_INTERPOLATION_STEPS in
matplotlib.axis to the desired number of vertices, but the orientation of the
polygon is not aligned with the radial axes.

.. [1] http://en.wikipedia.org/wiki/Radar_chart
"""
from dataset_functions import *

import argparse

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection

import _thread
import os


def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
    # rotate theta such that the first axis is at the top
    theta += np.pi/2

    def draw_poly_patch(self):
        verts = unit_poly_verts(theta)
        return plt.Polygon(verts, closed=True, edgecolor='k')

    def draw_circle_patch(self):
        # unit circle centered on (0.5, 0.5)
        return plt.Circle((0.5, 0.5), 0.5)

    patch_dict = {'polygon': draw_poly_patch, 'circle': draw_circle_patch}
    if frame not in patch_dict:
        raise ValueError('unknown value for `frame`: %s' % frame)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1
        # define draw_frame method
        draw_patch = patch_dict[frame]

        def fill(self, *args, **kwargs):
            """Override fill so that line is closed by default"""
            closed = kwargs.pop('closed', True)
            return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super(RadarAxes, self).plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            return self.draw_patch()

        def _gen_axes_spines(self):
            if frame == 'circle':
                return PolarAxes._gen_axes_spines(self)
            # The following is a hack to get the spines (i.e. the axes frame)
            # to draw correctly for a polygon frame.

            # spine_type must be 'left', 'right', 'top', 'bottom', or `circle`.
            spine_type = 'circle'
            verts = unit_poly_verts(theta)
            # close off polygon by repeating first vertex
            verts.append(verts[0])
            path = Path(verts)

            spine = Spine(self, spine_type, path)
            spine.set_transform(self.transAxes)
            return {'polar': spine}

    register_projection(RadarAxes)
    return theta


def unit_poly_verts(theta):
    """Return vertices of polygon for subplot axes.

    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [0.5] * 3
    verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
    return verts

def waitForQ():
	while True:
		c = input()
		if c is 'q' or c is 'Q':
			os._exit(0)
		print('enter q to exit')

if __name__ == '__main__':

	_thread.start_new_thread(waitForQ, ())

	languages = ['de', 'en', 'fr', 'nl', 'tr']

	parser = argparse.ArgumentParser()
	parser.add_argument("-r", "--refresh", help="refresh data cache",
                    action="store_true")
	args = parser.parse_args()

	CONSOLE_WIDTH = 170
	pd.set_option('display.width', CONSOLE_WIDTH)

	print("setting characters...")
	consonants, vowels = set_characters(languages, True)
	print("reading datasets...")
	dataFrames = read_files(languages, refresh_cache=args.refresh)
	print("removing erroneous words...")
	dataFrames = remove_intruders_all(dataFrames, consonants, vowels)
	print("calculating 2-gram and 3-gram features of the dataset...")
	df = calculate_features_all(dataFrames, consonants, vowels, refresh_cache=args.refresh)
	df_n = normalize_toall(df)
	print(df_n.iloc[:,0:6])

	data = np.array(df_n.iloc[:,0:6])
	spoke_labels = ['consonant-consonant', 'consonant-vowel', 'vowel-consonant',
					'vowel-vowel', 'same vowel-vowel', 'same consonant-consonant']

	N_AXES = 6
	#plt.style.use('ggplot')
	theta = radar_factory(N_AXES, frame='polygon')

	fig, axes = plt.subplots(figsize=(8,8), nrows=1, ncols=1,
							subplot_kw=dict(projection='radar'))
	#fig.subplots_adjust(wspace=0,hspace=0,top=1,bottom=0)

	ax = axes
	ax.set_rgrids([0.1, 0.2, 0.3, 0.4])
	ax.set_title("Distribution of 2-grams in various languages")
	colors = ['red', 'green', 'yellow', 'blue', 'magenta']
	for d,c in zip(data, colors):
		ax.plot(theta, d, color=c)
		ax.fill(theta, d, alpha=0.25, color=c)

	ax.set_varlabels([spoke_labels[i] for i in range(N_AXES)])
	labels = languages
	ax.legend(labels, fontsize='small')

	plt.show()
