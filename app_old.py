import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import State
import plotly.graph_objs as go
import numpy as np

inter_times = np.array([0.48522314, 1.32949067, 1.42201037, 1.44684582, 1.45925135, 1.46572348, 1.46881123, 1.470179, 1.47071709,
1.47077861, 1.47043116, 1.46961201, 1.46816852, 1.4658175, 1.46203561, 1.45590878, 1.44591789, 1.42938159, 1.3996955, 1.33255543, 1.13560189])

trace = go.Scatter(x=1+np.arange(len(inter_times)), y=inter_times, name="Interarrival Times", line=dict(color="#f44242"))

data = [trace]
layout = dict(title="Optimal Schedule", showlegend=False)
fig = dict(data=data, layout=layout)

def generate_html_table(num_rows=6):

    table = html.Div(
        [
            html.Div(
                html.Table(
                    # header
                    [html.Tr([html.Th()])]
                    +
                    # body
                    [
                        html.Tr(
                            [
                                html.Td(
                                    html.A(
                                        "mean"
                                        ##
                                    )
                                )
                            ]
                        )
                        # for i in range
                    ]
                ), style={"height": "150px", "overflowY": "scroll"},
            ),
        ], style={"height": "100%"},
    )

    return table

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([html.H2("Hello World!"),
            html.Img(src="/assets/schedule-icon.png")
    ],  className="banner"),

    html.Div([
        html.Div([
            html.H3("Column 2"),
            dcc.Graph(
            id="graph high",
            figure={
                "data": [trace],
                "layout": {
                    "title": "Graph 2"
                }
            }, className="th"
        )
    ], className="bordered"),

    html.Div([
        generate_html_table()
    ])

    ], className="row")
])

# app.css.append_css({
#     "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
# })

if __name__ == "__main__":
    app.run_server(debug=True)