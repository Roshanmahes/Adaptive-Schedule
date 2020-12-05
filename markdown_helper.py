import dash_html_components as html
import dash_core_components as dcc
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
                            dcc.Markdown(
                                children=dedent(
                                r"""
                                ##### What am I looking at?
                                
                                This app finds an optimal schedule for $n$ clients, that is, a sequence of arrival epochs $t_1,\dots,t_n$ 
                                that minimizes the objective function

                                $$\sum_{i=1}^{n}\omega\mathbb{E}I_i + (1-\omega)\mathbb{E}W_i.$$

                                In here, $I_i$ is the idle time prior to the arrival of client $i$ and $W_i$ is the waiting time of client $i$.
                                The factor $\omega$ reflects the relative importance of both components. The arrival epoch of client $i$ is
                                denoted by $t_i$, whereas the corresponding interarrival times are denoted by $x_i$.

                                The minimization is done by performing a so-called phase-type fit. The scheduler inserts the mean and squared 
                                coefficient of variation (that is, the ratio of the variance to the mean) of the service time $B$ of the clients.
                                For ease, the webapp assumes that all service times $B_i$ are independent and stem from the same distribution $B$.
                                Given these parameters of the true distribution, we determine the optimal schedule for a phase-type distribution 
                                with the same parameters. It has been shown that the error introduced by this fit can be considered as negligible.

                                After obtaining the initial schedule, the schedule can be made adaptive by rescheduling at any time point. The
                                key difference between precalculated and adaptive schedules is that the relevant information at each point of 
                                rescheduling can be used. While the number of clients $n$ that still remain to be scheduled also needs to be updated, 
                                the (relevant) information at each time point is the number of clients that are waiting in the system \#$wis$ and the 
                                time $u$ that the currently served client is in service (if any).

                                ##### More about this app
                                
                                The purpose of this app is to determine optimal schedules at the start of and during any service process with a single
                                server given the characteristics of the clients. The schedules are generated in real time using Python. To read
                                more about it, please send an email to Roshan Mahes ([roshan-1@live.com](mailto:roshan-1@live.com)), Michel Mandjes
                                ([m.r.h.mandjes@uva.nl](mailto:M.R.H.Mandjes@uva.nl)) or Marko Boon ([m.a.a.boon@tue.nl](mailto:m.a.a.boon@tue.nl)).
                                """
                                )
                            )
                        ],
                    ),
                ],
            )
        ),
    )
