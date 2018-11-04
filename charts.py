from stats import Statistics
from math import sqrt, ceil
from matplotlib import colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import random

"""
This is gross, better off sending the data to a nice web thing. Use flask or something
"""


class Charts(object):

    def __init__(self, db):
        self.stats = Statistics(db)

        self.colours = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

    def _single_pie(self, dic):
        keys, values = self.get_keys_and_values(dic)

        # Pie chart, where the slices will be ordered and plotted counter-clockwise:

        fig1, ax1 = plt.subplots()
        ax1.pie(values, labels=self.map_ids_to_names(keys), autopct='%1.1f%%', shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    def _multi_pies(self, dic):
        # TODO very ugly
        num = len(dic)
        square = int(ceil(sqrt(num)))
        idxs = [(i, j) for i in range(square) for j in range(square)]

        # Make figure and axes
        fig, axs = plt.subplots(square, square)

        for i, t in enumerate(dic.items()):
            name, d = t
            keys, values = self.get_keys_and_values(d)
            idx = idxs[i]
            axs[idx[0], idx[1]].pie(values, labels=self.map_ids_to_names(keys), autopct='%1.1f%%', shadow=True)

    def pie_chart(self, title, dic, nested=False):
        if nested:
            self._multi_pies(dic)
        else:
            self._single_pie(dic)

        plt.title(title)
        plt.show()

    def _single_bar(self, title, dic):
        # TODO colours and spacing are all shite
        keys, values = self.get_keys_and_values(dic)

        keys = self.map_ids_to_names(keys)

        ind = np.arange(len(values))  # the x locations for the groups
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots()
        rects = []
        colours = [self.rand_colour() for _ in range(len(keys))]
        for c, k, v in zip(colours, keys, values):
            rects.append(ax.bar(ind - width / 2, values, width,
                            color=colours, label=k))

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Count')
        ax.set_title(title)
        ax.set_xticks(ind)
        ax.set_xticklabels(keys)
        ax.legend()
        # TODO legend colours are wrong

        def autolabel(rects, xpos='center'):
            """
            Attach a text label above each bar in *rects*, displaying its height.

            *xpos* indicates which side to place the text w.r.t. the center of
            the bar. It can be one of the following {'center', 'right', 'left'}.
            """

            xpos = xpos.lower()  # normalize the case of the parameter
            ha = {'center': 'center', 'right': 'left', 'left': 'right'}
            offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}  # x_txt = x + w*off

            for rect in rects:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() * offset[xpos], 1.01 * height,
                        '{}'.format(height), ha=ha[xpos], va='bottom')

        autolabel(rects[0])

    def _multi_bar(self, dic):
        # TODO
        pass

    def bar_chart(self, title, dic, nested=False):
        if nested:
            self._multi_bar(dic)
        else:
            self._single_bar(title, dic)

        plt.show()

    def line_graph(self, json_data, nested=False):
        # TODO
        print("TODO")

    def map_ids_to_names(self, ids):
        return list(map(lambda x: self.stats.retrieve_name(x), ids))

    @staticmethod
    def get_keys_and_values(dic):
        keys = []
        values = []
        for k, v in dic.items():
            keys.append(k)
            values.append(v)
        return keys, values

    def rand_colour(self):
        keys, values = self.get_keys_and_values(self.colours)
        return random.choice(keys)

if __name__ == "__main__":
    c = Charts("messages_oliver_gratton")
    c.pie_chart(*c.stats.total_message_length("maurice_hewins"), nested=False)
    # c.pie_chart(*c.stats.for_all(c.stats.average_message_length), nested=True)
