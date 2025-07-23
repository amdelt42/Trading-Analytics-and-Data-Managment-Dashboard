#pages\analytics.py
import dash
from dash import html, callback, Input, Output, State, dcc

import dash_bootstrap_components as dbc

from components.components import update_flag_store
from pages.functions import get_stats, eur, percent

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
                    html.H4(id="avg-rr"),
                    html.P("Average RR")]),
                ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="profit-factor"),
                    html.P("Profit Factor")]),
                ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="avg-win"),
                    html.P("Average Win")]),
                ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="avg-loss"),
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
    Output("avg-rr", "children"),
    Output("profit-factor", "children"),
    Output("avg-win", "children"),
    Output("avg-loss", "children"),
    Input("update-flag", "data"),
    prevent_initial_call=False,
)

def update(current_flag):
    total_pnl, _, _, profit_factor, win_rate, avg_rr, avg_win, avg_loss = get_stats()
    total_pnl = eur(total_pnl)
    win_rate = percent(win_rate)
    avg_win = eur(avg_win)
    avg_loss = eur(avg_loss)
    return total_pnl, win_rate, avg_rr, profit_factor, avg_win, avg_loss


