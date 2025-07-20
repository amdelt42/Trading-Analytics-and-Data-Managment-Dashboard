import dash
from dash import html

import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", order=1) #"/" is the home page

layout = html.Div([
    html.H3("Home Page"),


], className="px-4 pb-4")
