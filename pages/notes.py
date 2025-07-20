import dash
from dash import html

import dash_bootstrap_components as dbc

dash.register_page(__name__, order=3)

layout = html.Div([
    html.H3("Notes Page"),
    html.P("This is where you'll add notes."),
    # Add form components later
], className="px-4 pb-4")
