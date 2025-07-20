#pages\analytics.py
import dash
from dash import html, callback, Input, Output, State, dcc

import dash_bootstrap_components as dbc

from components.components import update_flag_store
from pages.functions import get_total_pnl, get_win_rate

dash.register_page(__name__, path="/", order=1)

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="total-pnl"),
                    html.P("Total P&L")]),
                ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),
            
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="win-rate"),
                    html.P("Win Rate")]),
                ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),
            
       dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("1.48"),
                    html.P("Average RR")]),
                ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("2.62"),
                    html.P("Profit Factor")]),
                ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("442.65"),
                    html.P("Average Win")]),
                ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("-336.72"),
                    html.P("Average Loss")]),
                ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),
    ]),

    dbc.Row([

    ]),
    update_flag_store,
], className="px-4 pb-4")


#update on update flag
@callback(
    Output("total-pnl", "children"),
    Output("win-rate", "children"),
    Input("update-flag", "data"),
    prevent_initial_call=False,
)

def update(current_flag):
    total_pnl = str(get_total_pnl())
    win_rate = str(get_win_rate())+"%"
    return total_pnl, win_rate