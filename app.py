#app.py
import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from components.components import get_navbar, get_footer
from pages.functions import init_db

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div([
    get_navbar(),
    dbc.Container(dash.page_container, className="pt-4 flex-fill"),
    get_footer(),
], className="d-flex flex-column min-vh-100")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
