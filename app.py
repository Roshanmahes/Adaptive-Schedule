# imports
import dash
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from markdown_helper import markdown_popup
import numpy as np
import pandas as pd
from adaptive_scheduling import Transient_IA

# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

x = np.array([1.06285832, 1.38561383, 1.43545683, 1.45208582, 1.46053431,
       1.46457131, 1.46590595, 1.46558423, 1.46396076, 1.46074191,
       1.45502271, 1.44525078, 1.4288273 , 1.39941651, 1.33281871,
       1.13566431])

df = pd.DataFrame({r'Patient (\(i\))': np.arange(1,len(x)+1),
                   r'Interarrival time (\(x_i\))': [f'{np.round(i,2):.2f}' for i in x],
                   r'Arrival time (\(t_i\))': [f'{np.round(i,2):.2f}' for i in np.cumsum(x)]})

# df = df.to_dict('records')


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

                    html.Table(
                        id="my_table",
                        children=
                        # Header
                        [html.Tr([html.Th('Parameter'), html.Th('Value'), html.Th('Range'), html.Th('Explanation')])] +
                        # Body
                        [html.Tr([html.Td(r'\(\mathbb{E}B \)'),
                            html.Div(dcc.Input(id='mean', min=0.01, value=1, type='number')),
                            html.Td(r'\([0,\infty)\)'),
                            html.Td('mean')])] +
                        [html.Tr([html.Td(r'\(\mathbb{S}(B)\)'),
                            html.Div(dcc.Input(id='SCV', min=0.01, max=2, step=0.01, value=1, type='number')),
                            html.Td(r'\([0.01,2]\)'),
                            html.Td('SCV (squared coefficient of variation)')])] +
                        [html.Tr([html.Td(r'\(\omega\)'),
                            dcc.Input(id='omega', min=0.1, max=0.9, step=0.1, value=0.5, type='number'),
                            html.Td(r'\((0,1)\)'),
                            html.Td('importance idle time')])] +
                        [html.Tr([html.Td(r'\(n\)'),
                            dcc.Input(id='n', min=1, max=30, step=1, value=15, type='number'),
                            html.Td(r'\([1,30]\)'),
                            html.Td('#clients to be scheduled')])] +
                        [html.Tr([html.Td(r'\(\# wis\)'),
                            dcc.Input(id='wis', min=0, max=30, step=1, value=0, type='number'),
                            html.Td(r'\([0,30]\)'),
                            html.Td('#clients already waiting in system')])] + 
                        [html.Tr([html.Td(r'\(u\)'),
                            dcc.Input(id='u', min=0, max=5, step=0.01, value=0, type='number'),
                            html.Td(r'\([0,\infty)\)'),
                            html.Td('service time client in service (so far)')])], style={'width': '100%'}
                        ),
                ]
            ),
            html.Div(
                id="right-side-column",
                className="dynamic schedule",
                children=[
                    html.Div(
                        dt.DataTable(
                            id='schedule_df',
                            columns=[{"name": ["Appointment Schedule", k], "id": k} for k in df.columns],
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
                    ),
                    ),

                        # html.Div([
                        #     html.H3("Column 2"),
                        #     dcc.Graph(
                        #     id="graph high",
                        #     figure={
                        #         "data": [df.to_dict('records')],
                        #         "layout": {
                        #             "title": "Graph 2"
                        #         }
                        #     }, className="graph"
                        #     )
                        # ], className="graphic"),

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


# TODO: update table
@app.callback(
    [Output('schedule_df', 'data')],
    [Input('mean', 'value'), Input('SCV', 'value'), Input('omega', 'value'),
     Input('n', 'value'), Input('wis', 'value'), Input('u', 'value')],
)
def updateTable(mean, SCV, omega, n, wis, u):

    N = n + wis + 1
    x, _ = Transient_IA(SCV, u, omega, N, [], wis)
    x = x * mean

    df = pd.DataFrame({r'Patient (\(i\))': np.arange(1,len(x)+1),
                   r'Interarrival time (\(x_i\))': [f'{np.round(i,2):.2f}' for i in x],
                   r'Arrival time (\(t_i\))': [f'{np.round(i,2):.2f}' for i in np.cumsum(x)]})

    # print([df.to_dict('records')])

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