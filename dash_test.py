from stats import Statistics
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go


class DashCharts:

    def __init__(self, stats):
        self.stats = stats
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        self.colours = {
            'background': '#FFFFFF',
            'text': '#0E3E8C'
        }

    def transform_data(self, data):
        """
        Convert data of form
        {'100000793057611': 10501, '100000134684929': 12101}
        to
        [{'x': [1], 'y': [10501], 'type': 'bar', 'name':'Oliver Gratton'},
         {'x': [1], 'y': [12101], 'type': 'bar', 'name':'Maurice Hewins'}]
        """
        # TODO account for value being a list
        # TODO change how data is made in stats so this isn't silly
        return [
            {'x': [1], 'y': [v], 'type': 'bar', 'name': stats.retrieve_name(k)}
            for (k, v) in data.items()
        ]

    def make_bar_graph(self, transformed_data, title):
        # return dcc.Graph(
        #         id='bar-chart',
        #         figure={
        #             'data': transformed_data,
        #             'layout': {
        #                 'plot_bgcolor': self.colours['background'],
        #                 'paper_bgcolor': self.colours['background'],
        #                 'font': {
        #                     'color': self.colours['text']
        #                 },
        #                 'title': title
        #             }
        #         }
        #     )
        return dcc.Graph(
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=[1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
                           2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012],
                        y=[219, 146, 112, 127, 124, 180, 236, 207, 236, 263,
                           350, 430, 474, 526, 488, 537, 500, 439],
                        name='Rest of world',
                        marker=go.bar.Marker(
                            color='rgb(55, 83, 109)'
                        )
                    ),
                    go.Bar(
                        x=[1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
                           2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012],
                        y=[16, 13, 10, 11, 28, 37, 43, 55, 56, 88, 105, 156, 270,
                           299, 340, 403, 549, 499],
                        name='China',
                        marker=go.bar.Marker(
                            color='rgb(26, 118, 255)'
                        )
                    )
                ],
                layout=go.Layout(
                    title='US Export of Plastic Scrap',
                    showlegend=True,
                    legend=go.layout.Legend(
                        x=0,
                        y=1.0
                    ),
                    margin=go.layout.Margin(l=40, r=0, t=40, b=30)
                )
            ),
            style={'height': 300},
            id='my-graph'
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


if __name__ == '__main__':
    stats = Statistics("messages_oliver_gratton")
    title, data = stats.total_message_count("maurice_hewins")
    print(dict(data))

    d = DashCharts(stats)
    d.make_app(d.make_pie_chart(d.transform_data(data), title))
    d.start_app()
