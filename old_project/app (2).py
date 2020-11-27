# imports
import csv
import dash
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from markdown_helper import markdown_popup
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
# with open(f'csv_files/SCV_1.00_omega_0.5_minima.csv','r') as csvfile:
#     reader = csv.reader(csvfile)
#     old_minima = list(reader)

n = 15
# m = 0
# Delta = 0.01

# minima = [[None] * (n-1) for k in range(n-1)]

# for i in range(n-1):
#     for k in range(i+1):
#         minima[i][k] = f'{round(eval(old_minima[i][k])[m] * Delta, 2):.2f}'
        
# minima
# df = pd.DataFrame(minima, index=range(1,15), columns=range(1,15)).fillna('')
# df.index.name = 'i'
# df.reset_index(level=0, inplace=True)
# # print(df.to_dict('records'))

# main app
app = dash.Dash(__name__, external_scripts=['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'])
server = app.server

app.title = "Adaptive Schedule"

app.layout = html.Div(id='main',children=[
    dcc.Interval(id="interval-updating-graphs", interval=1000, n_intervals=0),
    html.Div(id="top-bar"),
    # html.P(children=r'Delicious \(\pi\) is inline with my goals (TODO).'),
    # html.P(children=r'$$\omega \sum_{i=1}^{n}\mathbb{E}I_i + (1 - \omega)\sum_{i=1}^{n}\mathbb{E}W_i$$',
    #   style={'text-align': 'center'}),
    
    html.Div(
        className="container",
        children=[
            html.Div(
                id="left-side-column",
                className="eight columns",
                children=[
                    html.Div(
                        id="header-section",
                        children=[
                            html.H4("Adaptive Schedule"),
                            html.P(
                                "TODO"
                            ),
                            html.P(children=r'$$\omega \sum_{i=1}^{n}\mathbb{E}I_i + (1 - \omega)\sum_{i=1}^{n}\mathbb{E}W_i$$',
                                style={'text-align': 'center'}),
                            html.Button(
                                "Learn more", id="learn-more-button", n_clicks=0
                            )
                        ],
                    ),
                    html.Div(
                        className="control-section",
                        children=[
                            html.Div(
                                className="control-element",
                                children=[
                                    html.Div(children=[r"\(\mathbb{E}B \) (mean)"]),
                                    dcc.Input(id="mean",
                                              min=0.01,
                                              value=1,
                                              type="number"
                                    ),
                                ],
                            ),
                            html.Div(
                                className="control-element",
                                children=[
                                    html.Div(children=[r"\(\mathbb{S}(B)\) (SCV)"]),
                                    dcc.Input(id="SCV",
                                              min=0.2,
                                              max=1.5,
                                              step=0.01,
                                              value=1,
                                              type="number"
                                    ),
                                ],
                            ),
                            html.Div(
                                className="control-element",
                                children=[
                                    html.Div(children=[r"\(\omega\)"]),
                                    dcc.Input(id="omega",
                                              min=0.1,
                                              max=0.9,
                                              step=0.1,
                                              value=0.5,
                                              type="number"
                                    ),
                                ],
                            ),
                            html.Div(
                                className="control-element",
                                children=[
                                    html.Div(children=[r"\(n\)"]),
                                    dcc.Input(id="n",
                                              min=1,
                                              max=20,
                                              step=1,
                                              value=15,
                                              type="number"
                                    ),
                                ],
                            ),
                            html.Div(
                                className="control-element",
                                children=[
                                    html.Div(children=[r"#clients waiting in system"]),
                                    dcc.Input(id="wis",
                                              min=0,
                                              max=n,
                                              step=0.1,
                                              value=0,
                                              type="number"
                                    ),
                                ],
                            ),
                            html.Div(
                                className="control-element",
                                children=[
                                    html.Div(children=[r"\(u\)"]),
                                    dcc.Input(id="u",
                                              min=0,
                                              max=5,
                                              step=0.1,
                                              value=0,
                                              type="number"
                                    ),
                                ],
                            ),
                        ],
                    ),
                ]
            ),
            html.Div(
                id="right-side-column",
                className="dynamic schedule",
                children=[
                    html.Div(
                                # className="control-element",
                                children=[
                                    html.Div(
                                        children=[r"\(u\) (slider)"] # served time client in service at time 0
                                    ),
                                    html.Div(
                                        dcc.Slider(
                                            id="u_slide",
                                            min=0,
                                            max=5,
                                            step=0.1,
                                            marks={
                                                i: f"{i}"
                                                for i in [i for i in range(6)]
                                            },
                                            value=0,
                                            updatemode="drag",
                                        ),
                                    ),
                                ],
                            ),
                    html.Div(
                        dt.DataTable(
                            id='my_table',
                            columns=[{"name": ["k", k], "id": k} for k in df.columns],
                            data=df.to_dict('records'),
                            merge_duplicate_headers=True,
                            # style_header={'textAlign': 'center'},
                            style_cell={'textAlign': 'center'},
                            style_cell_conditional=[
                                {
                                    'if': {'column_id': 'i'},
                                    # 'textAlign': 'right',
                                    'background-color': '#FAFAFA'
                                }
                            ],
                            # style_cell={
                            #     # 'backgroundColor': 'rgb(50, 50, 50)',
                            #     'accent': 'blue',
                            #     'selected-background': 'rgba(255, 65, 54, 0.2)',
                            # },
                            # css= [{'selector': '.dash-cell--selected *, .dash-cell.focused *', 'rule': 'background-color: blue; color: red; border-color: green; accent: blue'}]
                        # css= [{'selector': 'tr:hover', 'rule': 'background-color: #009688;'}],
                        # css=[{ # override default css for selected/focused table cells
                        #     'selector': '.td.cell--selected *, td.focused *',
                        #     'rule': "border: lightgrey; color: #3c3c3c; hover: #3c3c3c" #; --background-color-ellipses: #fdfdfd; --faded-text: #fafafa; --faded-text-header: #b4b4b4; --selected-background: rgba(255, 65, 54, 0.2); --faded-dropdown: #f0f0f0; --muted: #c8c8c8;"
                        #     # 'background-color: rgba(0, 150, 136, 0.1);'
                        # # }, {
                        #     # 'selector': 'td.cell--selected *, td.focused *',
                        #     # 'rule': 'color: rgba(0, 150, 136, 0.1) !important;'
                        # }],
                    ),
                    ),
                    
                ],
            ),
        ],
    ),
    markdown_popup(),
])

# Learn more popup
@app.callback(
    Output("markdown", "style"),
    [Input("learn-more-button", "n_clicks"), Input("markdown_close", "n_clicks")],
)
def update_click_output(button_click, close_click):
    ctx = dash.callback_context
    prop_id = ""
    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if prop_id == "learn-more-button":
        return {"display": "block"}
    else:
        return {"display": "none"}


@app.callback(
    [Output("u","value")],
    [Input("u_slide","value"),],
)
def update_shocks(value):
    return [value]

@app.callback(
    [Output("u_slide","value")],
    [Input("u","value"),],
)
def update_shocks2(value):
    return [value]

# TODO: update table
@app.callback(
    [Output("my_table", "data")],
    [Input("omega", "value"), Input("SCV", "value"), Input("u", "value"), Input("mean", "value"), Input("n", "value")], ## TODO
)
def updateTable(omega, SCV, u, mean, n):

    with open(f'csv_files/SCV_{SCV:.2f}_omega_{omega}_minima.csv','r') as csvfile:
        reader = csv.reader(csvfile)
        old_minima = list(reader)

    print(n)
    # n = 15
    Delta = 0.01
    m = int(u/Delta)
    
    minima = [[None] * (n-1) for k in range(n-1)]

    for i in range(n-1):
        
        x = 15 - n
        for k in range(i+1):
            minima[i][k] = f'{round(eval(old_minima[x+i][k])[m] * mean * Delta, 2):.2f}'
            
    # minima
    df = pd.DataFrame(minima, index=range(1,n), columns=range(1,n)).fillna('')
    df.index.name = 'i'
    df.reset_index(level=0, inplace=True)
    # df.
    # df.reset_index(level=1, inplace=True)
    print(df.columns)

    return [df.to_dict('records')]


if __name__ == '__main__':
  app.run_server() #debug=True)


# app = dash.Dash(__name__)
# mathjax = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'
# app.scripts.append_script({ 'external_url' : mathjax })

# app = dash.Dash(__name__, external_scripts=[
#       'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML',
#     ])
# server = app.server

# app.title = "Dynamic Appointment Scheduling"

# app.layout = html.Div(id='main',children=[
#   html.P(children=r'∆ Delicious \(\pi\) is inline with my goals.'),
#   html.P(children=r'$$ \lim_{t \rightarrow \infty} \pi = 0$$'),
#   html.P(style={'text-align':'left'}, children=r'\(\leftarrow \pi\)'),
#   html.P(style={'text-align':'left'}, children='not much left.'),
#   html.P(style={'text-align':'right'},children=r'\(\pi \rightarrow\)'),
#   html.P(style={'text-align':'right'},children='but it feels so right.'),
# ])

# if __name__ == '__main__':
#     app.run_server()