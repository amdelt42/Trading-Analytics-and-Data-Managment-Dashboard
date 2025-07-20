#pages\ai.py
import dash
from dash import html

import dash_bootstrap_components as dbc

dash.register_page(__name__, order=4)

layout = html.Div([
    html.H3("AI Page"),

], className="px-4 pb-4")
