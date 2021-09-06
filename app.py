# imports
from logging import PlaceHolder
import dash
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from markdown_helper import markdown_popup
import numpy as np
import pandas as pd
from adaptive_scheduling import Transient_IA
import plotly.graph_objs as go
# import plotly.io as pio

# pio.templates.default = 'plotly_white'


# initial table & figure
df = pd.DataFrame({r'Client (\(i\))': [''],
                   r'Interarrival time (\(x_i\))': ['Computing appointment schedule...'],
                   r'Arrival time (\(t_i\))': ['']})
df = df.to_dict('records')

no_fig = {
    'layout': {
        'xaxis': {'visible': False},
        'yaxis': {'visible': False},
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)'
    }
}

columns = [{'name': [f'Appointment Schedule', k], 'id': k} for k in df[0].keys()]

# main app
# app = dash.Dash(__name__, external_scripts=['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'])
app = dash.Dash(__name__, external_scripts=['https://cdn.jsdelivr.net/npm/mathjax@2.7.9/MathJax.js?config=TeX-MML-AM_CHTML'])
# app = dash.Dash(__name__, external_scripts=['https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/node-main.min.js?config=TeX-MML-AM_CHTML'])

app.title = 'Adaptive Schedule'
server = app.server

def app_layout():

    app_layout = html.Div(id='main',children=[
        dcc.Interval(id='interval-updating-graphs', interval=1000, n_intervals=0),
        html.Div(id='top-bar'),
        html.Div(
            className='container',
            children=[
                html.Div(
                    id='left-side-column',
                    className='eight columns',
                    children=[
                        html.H4('Adaptive Schedule'),
                        html.P(
                            ['This webapp solves the minimization problem' +
                            r'$$\min_{t_1,\dots,t_n}\omega \sum_{i=1}^{n}\mathbb{E}I_i + (1 - \omega)\sum_{i=1}^{n}\mathbb{E}W_i,$$' +
                            r'where \(I_i\) and \(W_i\) are the idle time and waiting time associated to client \(i\), respectively. ' +
                            r'The sequence of arrival epochs \(t_1,\dots,t_n\) is called the schedule. ' +
                            r'By entering the state information \((k, u)\), ' +
                            'this application can be used to generate adaptive schedules. ',
                            'Click ', html.A('here', id='learn-more-button', n_clicks=0), ' to learn more.']
                        ),
                        html.P('Please fill in the parameters below.'),
                        html.Table(
                            id='my_table',
                            children=
                            # Header
                            [html.Tr([html.Td(''), html.Th('Parameter'), html.Th('Value'), html.Th('Range'), html.Th('Explanation')])] +
                            # Body
                            # [html.Tr([html.Td('test', style={'text-align': 'center'})])] + 
                            [html.Tr([html.Th('Schedule Characteristics'),
                                html.Td(r'\(\omega\)'),
                                dcc.Input(id='omega', min=0, max=1, type='number', placeholder="e.g. '0.5'"),
                                html.Td(r'\((0,1)\)'),
                                html.Td('idle : waiting time')])] +
                            [html.Tr([html.Td(''),
                                html.Td(r'\(n\)'),
                                dcc.Input(id='n', min=1, max=20, step=1, type='number', placeholder="e.g. '4'"),
                                html.Td(r'\(\mathbb{N}_{\leq 20}\)'),
                                html.Td('#clients to serve')])] +
                            [html.Tr([html.Th('Patient Characteristics'),
                                html.Td(r'\(\mathbb{E}B_i \)'),
                                html.Div(dcc.Input(id='mean', type='text', placeholder="e.g. '1' or '(1,1,1,1)'")), ### TODO: eval, list
                                html.Td(r'\([0,\infty)^n\)'),
                                html.Td('mean(s)')])] +
                            [html.Tr([html.Td(''),
                                html.Td(r'\(\mathbb{S}(B_i)\)'),
                                html.Div(dcc.Input(id='SCV', type='text', placeholder="e.g. '(0.8,1.1,0.9,1.0)'")), ### TODO: eval, list
                                html.Td(r'\([0.2,2]^n\)'),
                                html.Td('SCV(s)')])] +
                            [html.Tr([html.Th('State Information'),
                                html.Td(r'\(k\)'),
                                dcc.Input(id='wis', min=0, max=5, step=1, type='number', placeholder="optional, e.g. '2'"), ### TODO: wis should be k!!!
                                html.Td(r'\(\mathbb{N}_{\leq 5}\)'), ### TODO: optional -> empty == 0
                                html.Td('#clients in system')])] +
                            [html.Tr([html.Td(''),
                                html.Td(r'\(u\)'),
                                dcc.Input(id='u', min=0, type='number', placeholder="optional, e.g. '0.33'"), ### TODO: optional -> empty == 0
                                html.Td(r'\([0,\infty)\)'),
                                html.Td('elapsed service time')])] +
                            [html.Tr([html.Th('Optional Constraints'),
                                html.Td(r'\(k\)'),
                                dcc.Input(id='wis2', min=0, max=5, step=1, type='number', placeholder="optional, e.g. '2'"), ### TODO: wis should be k!!!
                                html.Td(r'\([0,\infty)\times \dots\times [0,\infty)\)'), ### TODO: optional -> empty == 0
                                html.Td('fixed arrivals')])] +
                            [html.Tr([html.Td(''),
                                html.Td(r'\(u\)'),
                                dcc.Input(id='u2', min=0, type='number', placeholder="optional, e.g. '0.33'"), ### TODO: optional -> empty == 0
                                html.Td(r'\([0,\infty)\)'),
                                html.Td('first arrival moment')])], style={'width': '100%'}
                        ),
                        html.Button(id='submit-button', n_clicks=0, children='Compute Appointment Schedule', style={'font-style': 'italic'}),
                    ]
                ),
                html.Div(
                    id='right-side-column',
                    className='dynamic schedule',
                    children=[
                        html.Div(
                            dt.DataTable(
                                id='schedule_df',
                                columns=columns,
                                data=df,
                                merge_duplicate_headers=True,
                                style_header={'textAlign': 'center', 'backgroundColor': '#f9f9f9', 'fontWeight': 'bold'},
                                style_cell={'textAlign': 'center'},
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': '#f9f9f9'
                                    },
                                    {
                                        'if': {'state': 'selected'},
                                        'backgroundColor': '#dce9f9',
                                        'border': '1px solid #242582',
                                    }
                                ],
                            ),
                        ),
                        html.Div([
                            dcc.Graph(
                                id='graph_df',
                                figure = no_fig,
                                config={'displayModeBar': False},
                            )], className='graphic'),
                    ],
                ),
            ],
        ),
        markdown_popup(),
        ])

    return app_layout

# learn more popup
@app.callback(
    Output('markdown', 'style'),
    [Input('learn-more-button', 'n_clicks'), Input('markdown_close', 'n_clicks')],
)
def update_click_output(button_click, close_click):

    ctx = dash.callback_context
    prop_id = ""
    if ctx.triggered:
        prop_id = ctx.triggered[0]['prop_id'].split(".")[0]

    if prop_id == 'learn-more-button':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# schedule & graph
@app.callback(
    [Output('schedule_df', 'columns'), Output('schedule_df', 'data'), Output('graph_df', 'figure')],
    [Input('submit-button', 'n_clicks')],
    [State('mean', 'value'), State('SCV', 'value'), State('omega', 'value'),
     State('n', 'value'), State('wis', 'value'), State('u', 'value')],
)
def updateTable(n_clicks, mean, SCV, omega, n, wis, u):

    mean = eval(mean)
    SCV = eval(SCV)

    N = n + wis
    tol = None if N < 15 else 1e-4
    u = u / mean

    if not u and not wis:
        N = N - 1
        x, y = Transient_IA(SCV, u, omega, N, [], wis, tol)
        x = np.pad(x, (1,0))
    else:
        x, y = Transient_IA(SCV, u, omega, N, [], wis, tol)

    x = x * mean

    df = pd.DataFrame({r'Client (\(i\))': list(np.arange(1,len(x)+1)),
        r'Interarrival time (\(x_i\))': [f'{np.round(i,4):.4f}' for i in x],
        r'Arrival time (\(t_i\))': [f'{np.round(i,4):.4f}' for i in np.cumsum(x)]})

    figure = go.Figure(data=[go.Scatter(x=df.iloc[:,0], y=x, marker={'color': '#242582'})],
        layout=go.Layout(
            title=go.layout.Title(text=r'$\text{Optimal interarrival times } (x_i)$', x=0.5, xanchor='center'), # Plotly 4
            # title=r'$\text{Optimal interarrival times } (x_i)$', # Plotly 2
            xaxis={'title': r'$\text{Client } (i)$', 'tick0': 1, 'dtick': 1, 'range': [0.7,len(x) + 0.3]},
            yaxis={'title': r'$\text{Interarrival time } (x_i)$'},
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'))

    columns = [{'name': [f'Appointment Schedule (Cost: {y * mean:.4f})', k], 'id': k} for k in df.columns]

    return columns, df.to_dict('records'), figure


app.layout = app_layout

if __name__ == '__main__':
  app.run_server()
