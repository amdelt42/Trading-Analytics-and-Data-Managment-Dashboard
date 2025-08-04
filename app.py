#app.py
import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from components.components import get_navbar, get_footer
from pages.functions import init_db

import threading
import webview

import os

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div([
    get_navbar(),
    dbc.Container(dash.page_container, className="pt-4 flex-fill"),
    get_footer(),
], className="d-flex flex-column min-vh-100")

def start_dash():
    app.run(port=8050, debug=True, use_reloader=False)

if __name__ == "__main__":
    init_db()
    threading.Thread(target=start_dash).start()
    webview.create_window(
        "∇Dash", 
        "http://127.0.0.1:8050", 
        min_size=(1280, 720)
    )
    webview.start()
    os._exit(0)