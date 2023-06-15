# import dash_html_components as html
# import dash_core_components as dcc
from dash import html, dcc
from textwrap import dedent

def markdown_popup():
    return html.Div(
        id='markdown',
        className='modal',
        style={'display': 'none'},
        children=(
            html.Div(
                className='markdown-container',
                children=[
                    html.Div(
                        className='close-container',
                        children=html.Button(
                            'Close',
                            id='markdown_close',
                            n_clicks=0,
                            className='closeButton',
                        ),
                    ),
                    html.Div(
                        className='markdown-text',
                        children=[
                            dcc.Markdown(r'##### What am I looking at?'),
                            html.P(r'Consider \(n \in \mathbb{N}\) clients with service times that are represented by the independent, ' +
                                   r"non-negative random variables \(B_1,\dots,B_n\). Classically, the objective is to find an 'a priori' " +
                                   r'schedule that optimally balances the interests of both the clients and the service provider. ' +
                                   r'Our goal is to make updates possible given the relevant information available at the rescheduling epoch. ' +
                                   r'Concretely, the following cost function is minimized: ' +
                                   r'$$f(t_1,\dots,t_n|k,u) := \omega\sum_{i=1}^{n}\mathbb{E}I_i + (1-\omega)\sum_{i=1}^{n}\mathbb{E}W_i.$$' +
                                   r'Here, \(I_i\) is the idle time prior to the arrival of client \(i\) and \(W_i\) is the waiting time of ' +
                                   r'client \(i\). The factor \(\omega\in(0,1)\) reflects the relative importance of both components. ' +
                                   r'At the rescheduling epoch, the state information \((k,u)\) consists of the number of clients in the system ' +
                                   r'and the elapsed service time of the client in service (if any). One also has the ability to keep the ' +
                                   r'schedule of the first clients fixed and to allow updates only after a certain time \(\tau\).'),
                            html.P(r"Given the means \(\mathbb{E}B_i\) and squared coefficients of variation (SCVs) \(\mathbb{S}(B_i)\) (i.e., the ratio's " +
                                   r'of the variances to the square of the means) of the service times, the computations are done for phase-type distributions ' +
                                   r'with the same parameters. We rely on the following well-known phase-type fit: if the SCV is below \(1\), ' +
                                   r'we work with a mixture of two Erlang distributions (with the same scale parameter); if it is above \(1\) ' +
                                   r'a hyperexponential distribution, i.e., a mixture of two exponential distributions, is used. ' +
                                   r'It has been shown that the error introduced by this fit can be considered as negligible.'),
                            dcc.Markdown(r"""
                                    ##### More about this app

                                    The purpose of this app is to determine optimal adaptive schedules during any service process with a single
                                    server given the characteristics of the schedule and the clients, the state information, and some optional constraints.
                                    The schedules are generated in real time using Python. To read more about it, please send
                                    an email to Roshan Mahes ([roshan-1@live.com](mailto:roshan-1@live.com)), Michel Mandjes
                                    ([m.r.h.mandjes@uva.nl](mailto:M.R.H.Mandjes@uva.nl)) or Marko Boon ([m.a.a.boon@tue.nl](mailto:m.a.a.boon@tue.nl)).
                                    """
                            )
                        ],
                    ),
                ],
            )
        ),
    )
