from stats import Statistics
from collections import defaultdict
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import operator


class DashCharts:

    def __init__(self, stats):
        self.stats = stats
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        self.colours = {
            'background': '#FFFFFF',
            'text': '#0E3E8C'
        }

    def solo_conversations_compare(self, stat, users):
        """
        Make a bar chart of some statistic for some users
        :param stat The func name of the statistic (see stats.py) e.g. "total_messages_sent"
        :param users: List of the names of users e.g. ["bob_geldof", "mother_superior"]
        :return: Dash graph
        """
        data = self.make_bar_data([self.get_data(user, stat) for user in users])
        print(data)
        self.make_app(self.make_bar_chart(data, "%s in Solo Conversations" % (stat,)))

    def get_data(self, conversation, stat):
        """
        Retrieve the data from the database for one conversation
        :param conversation: name of the collection in the database e.g. "celia_imrie"
        :param stat: The func name of the statistic (see stats.py) e.g. "total_messages_sent"
        :return: List of data
        """
        # TODO error handling for bad stats/conversations
        return {
            "total_messages_sent": self.stats.total_messages_sent,
            "total_messages_length": self.stats.total_messages_length,
            "average_message_length": self.stats.average_message_length
        }[stat](conversation)

    def make_bar_data(self, data):
        """
        Convert data of form
        [{'100000793057611': 10501, '100000134684929': 12101}...]
        to
        a go.Bar object
        """
        # need to separate the user's data from their partners'
        # but first we need to know which one the user is
        id_counter = defaultdict(int)
        for dic in data:
            for k, v in dic.items():
                id_counter[k] += 1
        user_id = max(id_counter.items(), key=operator.itemgetter(1))[0]

        names = []
        user_data = []
        partners_data = []
        for dic in data:
            for k, v in dic.items():
                if k == user_id:
                    user_data.append(v)
                else:
                    partners_data.append(v)
                    names.append(self.stats.retrieve_name(k))

        user = go.Bar(
            x=names,
            y=user_data,
            name="You",
            marker=go.bar.Marker(
                color='rgb(55, 83, 109)'
            )
        )
        partners = go.Bar(
            x=names,
            y=partners_data,
            name="Them",
            marker=go.bar.Marker(
                color='rgb(26, 118, 255)'
            )
        )
        return [user, partners]

    def make_bar_chart(self, transformed_data, title):
        return dcc.Graph(
            figure=go.Figure(
                data=transformed_data,
                layout=go.Layout(
                    title=title,
                    showlegend=True,
                    legend=go.layout.Legend(
                        x=0,
                        y=1.0
                    ),
                    # margin=go.layout.Margin(l=40, r=0, t=40, b=30)
                )
            ),
            style={'height': 600},
            id='my-bar-graph'
        )

    def make_pie_chart(self, transformed_data, title):
        return dcc.Graph(
            id='pie',
            figure={
                'data': [
                    {
                        'labels': ['1st', '2nd', '3rd', '4th', '5th'],
                        'values': [38, 27, 18, 10, 7],
                        'type': 'pie',
                        'name': 'Starry Night',
                        'marker': {'colors': ['rgb(56, 75, 126)',
                                              'rgb(18, 36, 37)',
                                              'rgb(34, 53, 101)',
                                              'rgb(36, 55, 57)',
                                              'rgb(6, 4, 4)']},
                        'domain': {'x': [0, .48],
                                   'y': [0, .49]},
                        'hoverinfo': 'label+percent+name',
                        'textinfo': 'none'
                    },
                    {
                        'labels': ['1st', '2nd', '3rd', '4th', '5th'],
                        'values': [28, 26, 21, 15, 10],
                        'marker': {'colors': ['rgb(177, 127, 38)',
                                              'rgb(205, 152, 36)',
                                              'rgb(99, 79, 37)',
                                              'rgb(129, 180, 179)',
                                              'rgb(124, 103, 37)']},
                        'type': 'pie',
                        'name': 'Sunflowers',
                        'domain': {'x': [.52, 1],
                                   'y': [0, .49]},
                        'hoverinfo': 'label+percent+name',
                        'textinfo': 'none'

                    },
                    {
                        'labels': ['1st', '2nd', '3rd', '4th', '5th'],
                        'values': [38, 19, 16, 14, 13],
                        'marker': {'colors': ['rgb(33, 75, 99)',
                                              'rgb(79, 129, 102)',
                                              'rgb(151, 179, 100)',
                                              'rgb(175, 49, 35)',
                                              'rgb(36, 73, 147)']},
                        'type': 'pie',
                        'name': 'Irises',
                        'domain': {'x': [0, .48],
                                   'y': [.51, 1]},
                        'hoverinfo': 'label+percent+name',
                        'textinfo': 'none'
                    },
                    {
                        'labels': ['1st', '2nd', '3rd', '4th', '5th'],
                        'values': [31, 24, 19, 18, 8],
                        'marker': {'colors': ['rgb(146, 123, 21)',
                                              'rgb(177, 180, 34)',
                                              'rgb(206, 206, 40)',
                                              'rgb(175, 51, 21)',
                                              'rgb(35, 36, 21)']},
                        'type': 'pie',
                        'name': 'The Night Café',
                        'domain': {'x': [.52, 1],
                                   'y': [.51, 1]},
                        'hoverinfo': 'label+percent+name',
                        'textinfo': 'none'
                    }
                ],
                'layout': {
                    'title': 'Van Gogh: 5 Most Prominent Colors Shown Proportionally',
                    'showlegend': False
                }
            }
        )

    def make_app(self, graph):
        self.app.layout = html.Div(
            style={'backgroundColor': self.colours['background']},
            children=[
                html.H1(
                    children='Messenger Stats',
                    style={
                        'textAlign': 'center',
                        'color': self.colours['text']
                    }
                ),
                html.Div(
                    # children='Dash: A web application framework for Python.',
                    # style={
                    #     'textAlign': 'center',
                    #     'color': self.colours['text']
                    # }
                ),
                graph
            ]
        )

    def start_app(self):
        self.app.run_server(debug=True)


def get_all_user_names():
    # TODO temp way of getting all user chats
    import os
    all_files = filter(lambda x: "user" in x, list(map(lambda x: x.split('.')[0], os.listdir('logs'))))
    return [x[len("user_"):] for x in all_files]


if __name__ == '__main__':
    dc = DashCharts(Statistics("messages_oliver_gratton"))
    all_names = get_all_user_names()
    dc.solo_conversations_compare("total_messages_sent", all_names)
    dc.start_app()
