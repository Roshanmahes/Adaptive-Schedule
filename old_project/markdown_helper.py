import dash_html_components as html
import dash_core_components as dcc
from textwrap import dedent

def markdown_popup():
    return html.Div(
        id="markdown",
        className="modal",
        style={"display": "none"},
        children=(
            html.Div(
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "Close",
                            id="markdown_close",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.P(children=r'$$\omega \sum_{i=1}^{n}\mathbb{E}I_i + (1 - \omega)\sum_{i=1}^{n}\mathbb{E}W_i$$',
                        style={'text-align': 'center'}),
                    html.Div(
                        className="markdown-text",
                        children=[
                            dcc.Markdown(
                                children=dedent(
                                    r"""
                                ##### What am I looking at?
                                
                                This app solves the minimization problem $t_1,\dots,t_n$ are the patients' arrival epochs)

                                $$\omega \sum_{i=1}^{n}\mathbb{E}I_i + (1 - \omega)\sum_{i=1}^{n}\mathbb{E}W_i$$
                                
                                \begin{align}
                                \omega \sum_{i=1}^{n}\mathbb{E}I_i + (1 - \omega)\sum_{i=1}^{n}\mathbb{E}W_i
                                \end{align}

                                where $I_i$ is the idle time and $W_i$ is the waiting time associated to client $i$. We schedule the
                                jobs one by one: at the moment 

                                enhances visualization of objects detected using state-of-the-art Mobile Vision Neural Networks.
                                Most user generated videos are dynamic and fast-paced, which might be hard to interpret. A confidence
                                heatmap stays consistent through the video and intuitively displays the model predictions. The pie chart
                                lets you interpret how the object classes are divided, which is useful when analyzing videos with numerous
                                and differing objects.

                                ##### More about this app
                                
                                The purpose of this demo is to explore alternative visualization methods for object detection. Therefore,
                                the visualizations, predictions and videos are not generated in real time, but done beforehand. To read
                                more about it, please send an email to Roshan Mahes ([roshan-1@live.com](mailto:roshan-1@live.com)) or Michel Mandjes
                                [M.R.H.Mandjes@uva.nl](mailto:M.R.H.Mandjes@uva.nl).

                                """
                                )
                            )
                        ],
                    ),
                ],
            )
        ),
    )
