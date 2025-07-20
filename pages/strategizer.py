import dash

from dash import html
from components.components import update_flag_store

import dash_bootstrap_components as dbc

dash.register_page(__name__, order=3)

layout = html.Div([
    html.H3("Strategizing Page"),
    update_flag_store,
], className="px-4 pb-4")
