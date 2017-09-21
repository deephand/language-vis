#modified from: https://matplotlib.org/examples/api/radar_chart.html
#and here: https://datascience.stackexchange.com/questions/6084/how-do-i-create-a-complex-radar-chart
from dataset_functions import *

import argparse

import numpy as np

import pandas as pd

import matplotlib.pyplot as plt

import _thread
import os

from math import ceil


def waitForQ():
	while True:
		c = input()
		if c is 'q' or c is 'Q':
			os._exit(0)
		print('enter q to exit')

###Option 1
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
###Option 1

### Option 2
def _invert(x, limits):
    """inverts a value x on a scale from
    limits[0] to limits[1]"""
    return limits[1] - (x - limits[0])

def _scale_data(data, ranges):
    """scales data[1:] to ranges[0],
    inverts if the scale is reversed"""
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        assert (y1 <= d <= y2) or (y2 <= d <= y1)
    x1, x2 = ranges[0]
    d = data[0]
    if x1 > x2:
        d = _invert(d, (x1, x2))
        x1, x2 = x2, x1
    sdata = [d]
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        if y1 > y2:
            d = _invert(d, (y1, y2))
            y1, y2 = y2, y1
        sdata.append((d-y1) / (y2-y1)
                     * (x2 - x1) + x1)
    return sdata

class ComplexRadar():
    def __init__(self, fig, variables, ranges,
                 n_ordinate_levels=6):
        angles = np.arange(0, 360, 360./len(variables))

        axes = [fig.add_axes([0.07,0.05,0.87,0.85],polar=True,
                label = "axes{}".format(i))
                for i in range(len(variables))]
        l, text = axes[0].set_thetagrids(angles,
                                         labels=variables)
        [txt.set_rotation(angle-90) for txt, angle
             in zip(text, angles)]
        for ax in axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)
        for i, ax in enumerate(axes):
            grid = np.linspace(*ranges[i],
                               num=n_ordinate_levels)
            gridlabel = ["{}".format(round(x,2))
                         for x in grid]
            if ranges[i][0] > ranges[i][1]:
                grid = grid[::-1] # hack to invert grid
                          # gridlabels aren't reversed
            gridlabel[0] = "" # clean up origin
            ax.set_rgrids(grid, labels=gridlabel,
                         angle=angles[i])
            #ax.spines["polar"].set_visible(False)
            ax.set_ylim(*ranges[i])
        # variables for plotting
        self.angle = np.deg2rad(np.r_[angles, angles[0]])
        self.ranges = ranges
        self.ax = axes[0]
    def plot(self, data, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.plot(self.angle, np.r_[sdata, sdata[0]], *args, **kw)
    def fill(self, data, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.fill(self.angle, np.r_[sdata, sdata[0]], *args, **kw)
## Option 2

if __name__ == '__main__':

	plt.ion()

	languages = ['de', 'en', 'fr', 'nl', 'tr', 'sv', 'ms', 'fi']
	colors = ['red', 'green', 'yellow', 'blue', 'magenta','darkblue','darkgreen','orange']
	plt.style.use('ggplot')
	#languages = ['de', 'en', 'tr', 'sv', 'fi']
	#colors = ['red', 'green', 'yellow', 'blue', 'magenta']

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
	dataFrames = remove_intruders_all(dataFrames, consonants, vowels, refresh_cache=args.refresh)
	print("calculating 2-gram and 3-gram features of the dataset...")
	df = calculate_features_all(dataFrames, consonants, vowels, refresh_cache=args.refresh)
	df_n = normalize_toall(df)
	print(df_n.iloc[:,:])


	spoke_labels = ['consonant-consonant', 'consonant-vowel', 'vowel-consonant',
					'vowel-vowel', 'same vowel-vowel', 'same consonant-consonant']

	N_AXES = 6
	data = np.array(df_n.iloc[:,0:N_AXES])
	##choose either this or the other one
	# theta = radar_factory(N_AXES, frame='polygon')
	#
	# fig, axes = plt.subplots(figsize=(8,8), nrows=1, ncols=1,
	# 						subplot_kw=dict(projection='radar'))
	# #fig.subplots_adjust(wspace=0,hspace=0,top=1,bottom=0)
	#
	# ax = axes
	# ax.set_rgrids([0.1, 0.2, 0.3, 0.4])
	# for d,c in zip(data, colors):
	# 	ax.plot(theta, d, color=c)
	# 	ax.fill(theta, d, alpha=0.25, color=c)
	#
	# ax.set_varlabels(
	# labels = languages
	# ax.legend(labels, fontsize='small')

	##option 2:
	variables = ['consonant-consonant', 'consonant-vowel', 'vowel-consonant',
					'vowel-vowel', 'same vowel-vowel', 'same consonant-consonant']
	ranges1 = [(0.00001, ceil(10*max(df_n.iloc[:,i]))/10) for i in range(3)]
	ranges2 = [(0.00001, ceil(100*max(df_n.iloc[:,i]))/100) for i in range(3,6)]
	ranges = ranges1 + ranges2
	print(ranges)
	# plotting
	plt.style.use('ggplot')

	fig1 = plt.figure(figsize=(8, 8))
	variables = [variables[i] for i in range(N_AXES)]
	ranges = [ranges[i] for i in range(N_AXES)]
	radar = ComplexRadar(fig1, variables, ranges)
	colors = ['red', 'green', 'yellow', 'blue', 'magenta','darkblue','darkgreen','orange']
	for d,c in zip(data, colors):
		radar.plot(d, color=c)
		radar.fill(d, color=c, alpha=0.1)
	###
	radar.ax.legend(languages)
	_thread.start_new_thread(waitForQ, ())

	plt.suptitle("Distribution of 2-grams in various languages", size=16)
	plt.show()
	plt.pause(0)
