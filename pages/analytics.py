#pages\analytics.py
import dash
from dash import html, callback, Input, Output, State, dcc

import dash_bootstrap_components as dbc

from components.components import update_flag_store
from pages.functions import get_stats, eur, percent, get_cum_pnl

dash.register_page(__name__, path="/", order=1)

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="total-pnl"),
                    html.P("Total P&L"),
                    html.H6(id="total-pnl-long", style={"color": "blue"}),
                    html.H6(id="total-pnl-short", style={"color": "red"}),
                ]),
            ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),
            
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="win-rate"),
                    html.P("Win Rate"),
                    html.H6(id="wr-long", style={"color": "blue"}),
                    html.H6(id="wr-short", style={"color": "red"}),
                ]),
            ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),
            
       dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="avg-rr"),
                    html.P("Average RR"),
                    html.H6(id="avg-rr-long", style={"color": "blue"}),
                    html.H6(id="avg-rr-short", style={"color": "red"}),
                ]),
            ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="profit-factor"),
                    html.P("Profit Factor"),
                    html.H6(id="p-factor-long", style={"color": "blue"}),
                    html.H6(id="p-factor-short", style={"color": "red"}),
                ]),
            ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="avg-win"),
                    html.P("Average Win"),
                    html.H6(id="avg-win-long", style={"color": "blue"}),
                    html.H6(id="avg-win-short", style={"color": "red"}),
                ]),
            ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="avg-loss"),
                    html.P("Average Loss"),
                    html.H6(id="avg-loss-long", style={"color": "blue"}),
                    html.H6(id="avg-loss-short", style={"color": "red"}),
                ]),
            ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),
    ]),

    dbc.Row([
        dbc.Card([
            dbc.CardBody([
                html.Div(id="cum-pnl"),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dcc.Dropdown(
                                id="time-filter",
                                options=[
                                    {"label": "All Time", "value": "all"},
                                    {"label": "This Month", "value": "monthly"},
                                    {"label": "This Week", "value": "weekly"},
                                    {"label": "Today", "value": "daily"},
                                ],
                                value="monthly",
                                clearable=False,
                                style={"width": "200px"}
                            ),
                        ], width="auto"),

                        dbc.Col([
                            dcc.Dropdown(
                                id="tag-filter",
                                options=[
                                    {"label": "Breakout", "value": "Breakout"},
                                    {"label": "Reversal", "value": "Reversal"},
                                    {"label": "News", "value": "News"},
                                    {"label": "Range", "value": "Range"},
                                    {"label": "Momentum", "value": "Momentum"},
                                    {"label": "Gap", "value": "Gap"},
                                    {"label": "Trend", "value": "Trend"},
                                ],
                                multi=True,
                                placeholder="Select tags...",
                                style={"width": "300px"}
                            ),
                        ], width="auto"),

                        dbc.Col([
                            html.Div([
                                html.Span("↑ Long", style={"color": "blue", "margin-right": "20px"}),
                                html.Span("↓ Short", style={"color": "red"}),
                            ], style={"display": "flex", "justify-content": "flex-end", "align-items": "center", "height": "100%"})
                        ], className="d-flex justify-content-end align-items-center", width=True),
                    ]),
                ], className="mt-2")
            ],
            className="mt-3 mb-3", 
            style={"background-color": "#DBDBDB", "color": "black"}),
        ]),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([  
                    html.H4(id="t-count"),
                    html.P("Total Trades"),
                    html.H6(id="t-long", style={"color": "blue"}),
                    html.H6(id="t-short", style={"color": "red"}),
                ]),  
            ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([  
                    html.H4(id="t-win"),
                    html.P("Wins"),
                ]),  
            ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([  
                    html.H4(id="t-loss"),
                    html.P("Losses"),
                ]),  
            ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([  
                    html.H4(id="t-breakeven"),
                    html.P("Break-Evens"),
                ]),  
            ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),
    ]),
    update_flag_store,
], className="px-4 pb-4")


#update on update flag
@callback(
    Output("total-pnl", "children"),
    
    Output("profit-factor", "children"),
    #t-p
    #t-l
    Output("win-rate", "children"),
    Output("avg-rr", "children"),
    Output("avg-win", "children"),
    Output("avg-loss", "children"),
    Output("t-count", "children"),
    Output("t-win", "children"),
    Output("t-loss", "children"),
    Output("t-breakeven", "children"),
    Output("wr-long", "children"),
    Output("wr-short", "children"),
    Output("total-pnl-long", "children"),
    Output("total-pnl-short", "children"),
    Output("avg-rr-long", "children"),
    Output("avg-rr-short", "children"),
    Output("p-factor-long", "children"),
    Output("p-factor-short", "children"),
    Output("avg-win-long", "children"),
    Output("avg-win-short", "children"),
    Output("avg-loss-long", "children"),
    Output("avg-loss-short", "children"),
    Output("t-long", "children"),
    Output("t-short", "children"),
    Output("cum-pnl", "children"),
    Input("update-flag", "data"),
    Input("time-filter", "value"),
    Input("tag-filter", "value"),
    prevent_initial_call=False,
)

def update(flag, period, tags):
    tags_tuple = tuple(tags) if tags else ()
    stats = get_stats(period, tags_tuple)
    return [
        eur(stats[0]), #t-pnl
        #eur(stats[1]), #t-p
        #eur(stats[2]), #t-l
        stats[3], #p-factor
        percent(stats[4]), #win-rate
        stats[5], #avg RR
        eur(stats[6]), #avg win
        eur(stats[7]), #avg loss
        stats[8], #t-count
        stats[9], #wins
        stats[10], #losses
        stats[11], #break-evens
        percent(stats[12]), #long wr
        percent(stats[13]), #short wr
        eur(stats[14]), #t-pnl long
        eur(stats[15]), #t-pnl short
        stats[16],
        stats[17],
        stats[18],
        stats[19],
        eur(stats[20]),
        eur(stats[21]),
        eur(stats[22]),
        eur(stats[23]),
        stats[24],
        stats[25],
        get_cum_pnl(period, tags_tuple), #cum pnl
    ]


