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

    def solo_conversations_bars(self, stat, users):
        """
        Make a bar chart of some statistic for some users
        :param stat The func name of the statistic (see stats.py) e.g. "total_messages_sent"
        :param users: List of the names of users e.g. ["bob_geldof", "mother_superior"]
        :return: Dash graph
        """
        data = self.transform_per_user_bar_data([self.get_data(user, stat) for user in users])
        self.make_app(self.make_chart(data, "%s in Solo Conversations" % (stat,)))

    def conversation_time_chunks(self, users, resolution="day", cumulative=True):
        """
        Make a line graph of messages sent over time
        :param users: List of the names of users e.g. ["bob_geldof", "mother_superior"]
        :param resolution: year, month, day, hour, minute, second
        :return: Dash graph
        """
        transform = self.transform_cumulative_data if cumulative else self.transform_line_data
        data = transform(
            [self.get_data(user, "time_chunks", resolution) for user in users],
            self.snake_case_to_names(users)
        )
        c_string = 'Cumulative ' if cumulative else ''
        self.make_app(self.make_chart(data, "%sMessages Sent Over Time (per %s)" % (c_string, resolution,)))

    @staticmethod
    def snake_case_to_names(users):
        return [' '.join((map(lambda x: x.title(), user.split('_')))) for user in users]

    def get_data(self, conversation, stat, *args):
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
            "average_message_length": self.stats.average_message_length,
            "time_chunks": self.stats.time_chunks
        }[stat](conversation, *args)

    def transform_per_user_bar_data(self, data):
        """
        Transform data of form
        [{'100000793057611': 10501, '100000134684929': 12101}...]
        into a go.Bar object
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

    def transform_line_data(self, data, names, scatter=True):
        """
        Transform data of form
        [[{'count': 1939, 'timestamp': '2015'}, ...], ...]
        into a go.Scatter object for a scatter graph
        """
        data = self.pad_time_data(data)
        mode = 'markers' if scatter else 'lines'
        transformed_data = []
        for name, conversation in zip(names, data):
            x, y = [], []  # TODO do this in one list comp?
            for c in conversation:
                x.append(c["timestamp"])
                y.append(c["count"])
            transformed_data.append(go.Scatter(
                x=x,
                y=y,
                # fill='tozeroy',  # can use tonexty to stack
                mode=mode,
                name=name
                # stackgroup='one'
            ))

        return transformed_data

    def transform_cumulative_data(self, data, names):
        """
        Transform data of form
        [[{'count': 1939, 'timestamp': '2015'}, ...], ...]
        into a go.Scatter object for a cumulative line graph
        """
        data = self.pad_time_data(data)
        transformed_data = []
        for name, conversation in zip(names, data):
            x, y, count = [], [], 0
            for c in conversation:
                x.append(c["timestamp"])
                y.append(c["count"] + count)
                count += c["count"]
            transformed_data.append(go.Scatter(
                x=x,
                y=y,
                fill='tozeroy',  # if first else 'tonexty',
                mode='lines',
                name=name,
                # stackgroup='one'
            ))

        return transformed_data

    def pad_time_data(self, data):
        """ Pad time data with 0s to make sure it stays ordered """
        # TODO
        # every dict in the data needs to share the same x values (timestamp)
        # if there is no corresponding count value, set to 0
        return data

    def make_chart(self, transformed_data, title):
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
                'data': [{
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
                    }, {
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


def get_names_from_logs(type="user"):
    # TODO temp way of getting all user chats
    import os
    all_files = filter(lambda x: type in x, list(map(lambda x: x.split('.')[0], os.listdir('logs'))))
    return [x[len(type)+1:] for x in all_files]

if __name__ == '__main__':
    dc = DashCharts(Statistics("messages_oliver_gratton"))
    all_names = get_names_from_logs("user") + get_names_from_logs("group")
    dc.conversation_time_chunks(all_names, "month", cumulative=False)
    dc.start_app()
