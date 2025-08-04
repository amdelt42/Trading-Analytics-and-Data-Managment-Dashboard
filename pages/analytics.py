#pages\analytics.py
import dash
from dash import html, callback, Input, Output, State, dcc

import dash_bootstrap_components as dbc

from components.components import update_flag_store
from pages.functions import\
    get_stats, eur, percent, \
    get_cum_pnl, get_cum_stats, get_tradeFreq_hist, get_tradeDur_hist, get_marketDist_hist

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
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dcc.Dropdown(
                                id="time-filter",
                                options=[
                                    {"label": "All Time", "value": "all"},
                                    {"label": "Year", "value": "1y"},
                                    {"label": "YTD", "value": "ytd"},
                                    {"label": "Month", "value": "1m"},
                                    {"label": "Week", "value": "1w"},
                                    {"label": "Day", "value": "1d"},
                                ],
                                value="1m",
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
                ], className="mb-3"),
                html.Div(id="cum-pnl"),
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
                    html.H6(id="t-win-long", style={"color": "blue"}),
                    html.H6(id="t-win-short", style={"color": "red"}),
                ]),  
            ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([  
                    html.H4(id="t-loss"),
                    html.P("Losses"),
                    html.H6(id="t-loss-long", style={"color": "blue"}),
                    html.H6(id="t-loss-short", style={"color": "red"}),
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
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="max-drawdown"),
                    html.P("Max Drawdown"),
                    html.H6(id="max-drawdown-long", style={"color": "blue"}),
                    html.H6(id="max-drawdown-short", style={"color": "red"}),
                ]),
            ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="expectancy"),
                    html.P("Expectancy"),
                ]),
            ], style={"background-color": "#DBDBDB", "color": "black"}),
        ], width=2),
    ]),
    
    dbc.Row([
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Div(id="avg-trade-freq"),
                    ], width=6),

                    dbc.Col([
                        html.Div(id="trade-dur-hist"),
                    ], width=6), 
                ]),
            ],
            className="mt-3 mb-3", 
            style={"background-color": "#DBDBDB", "color": "black"}
            ),
        ]),
    ]),

    dbc.Row([
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Div(id="pnl-markethours-hist"),
                    ]),
                ]),
            ],
            className="mb-3", 
            style={"background-color": "#DBDBDB", "color": "black"}
            ),
        ]),
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
    Output("t-win-long", "children"),
    Output("t-win-short", "children"),
    Output("t-loss-long", "children"),
    Output("t-loss-short", "children"),
    Output("max-drawdown", "children"),
    Output("max-drawdown-long", "children"),
    Output("max-drawdown-short", "children"),
    Output("expectancy", "children"),
    Output("cum-pnl", "children"),
    Output("avg-trade-freq", "children"),
    Output("trade-dur-hist", "children"),
    Output("pnl-markethours-hist", "children"),
    Input("update-flag", "data"),
    Input("time-filter", "value"),
    Input("tag-filter", "value"),
    prevent_initial_call=False,
)

def update_Stats(flag, period, tags):
    tags_tuple = tuple(tags) if tags else ()
    stats = get_stats(period, tags_tuple)
    cum_graph, _ = get_cum_pnl(period, tags_tuple)
    tradeFreq_hist = get_tradeFreq_hist(period, tags_tuple)
    tradeDur_hist =  get_tradeDur_hist(period, tags_tuple) 
    marketHour_hist = get_marketDist_hist(period, tags_tuple)
    max_dd, max_dd_long, max_dd_short = get_cum_stats(period, tags_tuple)
    expectancy = round(stats[6]*stats[4]/100+stats[7]*(1-stats[4]/100), 2)

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
        stats[16], #avg-rr long
        stats[17], #avg-rr short
        stats[18], #p-factor long
        stats[19], #p-factor short
        eur(stats[20]), #avg win long
        eur(stats[21]), #avg win short
        eur(stats[22]), #avg loss long
        eur(stats[23]), #avg loss short
        stats[24], #t_long
        stats[25], #t_short
        stats[26], #t_win_long
        stats[27], #t_win_short
        stats[28], #t_loss_long
        stats[29], #t_loss_short
        eur(max_dd), #maximum drawdown
        eur(max_dd_long), #maximum drawdown long
        eur(max_dd_short), #maximum drawdown short
        eur(expectancy), #trade expectancy
        cum_graph, #cumulative pnl graph
        tradeFreq_hist, #avg trade frequency vs day of the week histogram
        tradeDur_hist, #avg trade duration vs RR histogram
        marketHour_hist #avg trade pnl vs market hour pnl
    ]


