# imports
import dash
from dash import dash_table as dt
from dash import html, dcc
from dash.dependencies import Input, Output, State
from markdown_helper import markdown_popup
import numpy as np
import pandas as pd
import plotly.graph_objs as go

from new_adaptive_scheduling import optimal_schedule as Schedule


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
        html.Div(
            className='container',
            children=[
                html.Div(id='top-bar'),
                html.Div(
                    id='left-side-column',
                    className='eight columns',
                    children=[
                        html.H4('Adaptive Schedule'),
                        html.P(
                            ['This webapp solves the optimization problem' +
                            r'$$\min_{t_1,\dots,t_n}\omega \sum_{i=1}^{n}\mathbb{E}I_i + (1 - \omega)\sum_{i=1}^{n}\mathbb{E}W_i,$$' +
                            r'where \(I_i\) and \(W_i\) are the idle time and waiting time associated to client \(i\), respectively. ' +
                            r'The sequence of arrival epochs \(t_1,\dots,t_n\) is called the schedule. By entering the state ' + 
                            r'information \((k, u)\), this application can be used to generate adaptive schedules. ' +
                            r'One also has the option to leave the schedule fixed until a certain time \(\tau\). ',
                            'Click ', html.A('here', id='learn-more-button', n_clicks=0), ' to learn more.']
                        ),
                        html.P('Please fill in the parameters below.'),
                        html.Table(
                            id='my_table',
                            children=
                            # Header
                            [html.Tr([html.Td(''), html.Th('Parameter'), html.Th('Value'), html.Th('Range'), html.Th('Explanation')])] +
                            # Body
                            [html.Tr([html.Th('Schedule Characteristics'),
                                html.Td(r'\(\omega\)'),
                                dcc.Input(id='omega', min=0.001, max=0.999, type='number', value=0.5, placeholder="e.g. '0.5'"),
                                html.Td(r'\((0,1)\)'),
                                html.Td('idle : waiting time')])] +
                            [html.Tr([html.Td(''),
                                html.Td(r'\(n\)'),
                                dcc.Input(id='n', min=1, max=20, step=1, type='number', value=5, placeholder="e.g. '5'"),
                                html.Td(r'\(\mathbb{N}_{\leq 20}\)'),
                                html.Td('#clients to serve')])] +

                            [html.Tr([html.Th('Client Characteristics'),
                                html.Td(r'\(\mathbb{E}B_i\)'),
                                html.Div(dcc.Input(id='means', type='text', value=1, placeholder="e.g. '1' or '(1,1,1,1,1)'")),
                                html.Td(r'\((0,\infty)^n\)'),
                                html.Td('mean(s)')])] +
                            [html.Tr([html.Td(''),
                                html.Td(r'\(\mathbb{S}(B_i)\)'),
                                html.Div(dcc.Input(id='SCVs', type='text', value='(0.8,1.0,1.1,0.9,1.0)', placeholder="e.g. '(0.8,1.0,1.1,0.9,1.0)'")),
                                html.Td(r'\((0,\infty)^n\)'),
                                html.Td('SCV(s)')])] +

                            [html.Tr([html.Th('State Information'),
                                html.Td(r'\(k\)'),
                                dcc.Input(id='k', min=0, max=19, step=1, type='number', placeholder="optional, e.g. '2'"),
                                html.Td(r'\(\mathbb{N}_{< n}\)'),
                                html.Td('#clients in system')])] +
                            [html.Tr([html.Td(''),
                                html.Td(r'\(u\)'),
                                dcc.Input(id='u', min=0, type='number', placeholder="optional, e.g. '0.33'"),
                                html.Td(r'\([0,\infty)\)'),
                                html.Td('elapsed service time')])] +

                            [html.Tr([html.Th('Optional Constraints'),
                                html.Td(r'\(t_{k+1},\dots,t_{\ell}\)'),
                                dcc.Input(id='fixed_t', type='text', placeholder="optional, e.g. '(0.6,1.58)'"),
                                html.Td(r'\([0,\infty)^{\ell-k}\)'),
                                html.Td('fixed arrival times')])] +
                            [html.Tr([html.Td(''),
                                html.Td(r'\(\tau\)'),
                                dcc.Input(id='tau', min=0, type='number', placeholder="optional, e.g. '1.8'"),
                                html.Td(r'\([t_\ell,\infty)\)'),
                                html.Td('fixed schedule time length')])], style={'width': '100%'}
                        ),
                        html.Button(id='submit-button', n_clicks=0, children='Compute Appointment Schedule'),
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
    [State('omega', 'value'), State('n', 'value'),
     State('means', 'value'), State('SCVs', 'value'),
     State('k', 'value'), State('u', 'value'),
     State('fixed_t', 'value'), State('tau', 'value')],
)
def updateTable(n_clicks, omega, n, means, SCVs, k, u, fixed_t, tau):

    error = None
    try:
        means = eval(str(means), {'__builtins__': {}})
    except:
        error = 'Error! No means entered.'
    try:
        SCVs = eval(str(SCVs), {'__builtins__': {}})
    except:
        error = 'Error! No SCVs entered.'

    if type(means) == float or type(means) == int:
        means = [means] * n
    if type(SCVs) == float or type(SCVs) == int:
        SCVs = [SCVs] * n
    if len(means) != n:
        error = 'Error! Not enough means entered.'
    elif len(SCVs) != n:
        error = 'Error! Not enough SCVs entered.'

    if not k:
        k = 0
    if not u:
        u = 0
    if not tau:
        tau = 0
    
    if k >= n:
        error = r'Error! Note that \(k < n\).'
    elif k == 0 and u > 0:
        error = r'Error! Note that \(u > 0 \implies k > 0\).'

    try:
        fixed_t = eval(str(fixed_t), {'__builtins__': {}})

        if not fixed_t:
            fixed_t = []
        else:
            if type(fixed_t) == float or type(fixed_t) == int:
                fixed_t = np.array([fixed_t])
            else:
                fixed_t = np.array(fixed_t)

            if len(fixed_t) > 1 and not all(i < j for i, j in zip(fixed_t, fixed_t[1:])):
                error = r'Error! Note that the fixed arrival times must be increasing.'
            elif len(fixed_t) >= n-k:
                error = r'Error! Note that \(\ell < n\).'
            elif len(fixed_t) and tau < fixed_t[-1]:
                error = r'Error! Note that \(\tau \geq t_\ell\).'
    except:
        error = f'Error! Wrongly entered fixed arrival times.'

    if error:  # error handling
        df = pd.DataFrame({r'Client (\(i\))': [''],
                   r'Interarrival time (\(x_i\))': [error],
                   r'Arrival time (\(t_i\))': ['']})

        figure = go.Figure(data=[go.Scatter(x=[0], y=[0], marker={'color': 'rgba(0,0,0,0)'})],
            layout= {
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0)'
           })
        figure.update_layout(title=r'Please enter the correct parameters.')
        columns = [{'name': [f'Appointment Schedule', k], 'id': k} for k in df.keys()]

    else:
        if not k and not u:  # system is idle
            if not len(fixed_t):
                print('Case 1')
                t, cost = Schedule(means,SCVs,omega,[],0,k=1,u=0)
                t += tau
                cost += omega * tau
            else:
                print('Case 2')
                min_time_next = tau - fixed_t[-1]
                fixed_inter_times = [(fixed_t[i] - fixed_t[i-1]) for i in range(1,len(fixed_t))]
                print(fixed_inter_times, min_time_next)
                t, cost = Schedule(means,SCVs,omega,fixed_inter_times,min_time_next,k=1,u=0)
                print(t)
                t += fixed_t[0]
                cost += omega * fixed_t[0]

        else:  # a client is in service
            if not len(fixed_t):
                print('Case 3')
                t, cost = Schedule(means,SCVs,omega,[],tau,k,u)
            else:
                print('Case 4')
                min_time_next = tau - fixed_t[-1]
                fixed_inter_times = [fixed_t[0]] + [(fixed_t[i] - fixed_t[i-1]) for i in range(1,len(fixed_t))]
                t, cost = Schedule(means,SCVs,omega,fixed_inter_times,min_time_next,k,u)


        inter_t = [t[0]] + list(np.diff(t))
        df = pd.DataFrame({r'Client (\(i\))': list(np.arange(n+1-len(t),n+1)),
            r'Interarrival time (\(x_i\))': [f'{np.round(i,4):.4f}' for i in inter_t],
            r'Arrival time (\(t_i\))': [f'{np.round(i,4):.4f}' for i in t]})

        figure = go.Figure(data=[go.Scatter(x=df.iloc[:,0], y=inter_t, marker={'color': '#242582'},
            showlegend=False, name='Interarrival time')],
            layout=go.Layout(
                title=go.layout.Title(text='Optimal interarrival times', x=0.5, xanchor='center'), # Plotly 4
                xaxis={'title': 'Client', 'tick0': 1, 'dtick': 1},
                yaxis={'title': 'Interarrival time'},
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'))

        m = len(fixed_t)
        if m:
            figure.add_trace(go.Scatter(x=list(range(k+1,k+m+1)), y=inter_t[:m], marker=dict(
                color='#dce9f9'),
                showlegend=False,
                name='Fixed interarrival time'
            ))

        columns = [{'name': [f'Appointment Schedule (Cost: {cost:.4f})', k], 'id': k} for k in df.columns]

    return columns, df.to_dict('records'), figure


app.layout = app_layout

if __name__ == '__main__':
    app.run_server()
