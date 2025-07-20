#pages\data.py
import dash

from dash import html, dcc, Input, Output, State, callback
from pages.functions import insert_trade, delete_recent, top_recent, base64_to_bytes, no_updates
from components.components import update_flag_store

import dash_bootstrap_components as dbc
import pandas as pd
import datetime as dt

dash.register_page(__name__, order=2)

layout = html.Div([
    #data entry form
    html.H2("Data Entry", className="text-center"),
    dbc.Container([
        dbc.Form([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Ticker", className="mt-3"),
                    dbc.Input(id="input-ticker", placeholder="Enter ticker", type="text"),

                    dbc.Label("P&L", className="mt-3"),
                    dbc.Input(id="input-pl", placeholder="Enter P&L", type="number"),

                    dbc.Label("Risk", className="mt-3"),
                    dbc.Input(id="input-risk", placeholder="Enter risk", type="number"),

                    dbc.Label("Entry", className="mt-3"),
                    dbc.Input(id="input-entry", placeholder="Enter entry price", type="number"),

                    dbc.Label("Exit", className="mt-3"),
                    dbc.Input(id="input-exit", placeholder="Enter exit price", type="number"),

                    
                ], width=6),

                dbc.Col([
                    dbc.Label("Entry Time", className="mt-3"),
                    dbc.Input(id="input-entryT", placeholder="Enter entry time", type="time"),

                    dbc.Label("Exit Time", className="mt-3"),
                    dbc.Input(id="input-exitT", placeholder="Enter exit time", type="time"),

                    dbc.Label("Fees", className="mt-3"),
                    dbc.Input(id="input-fees", placeholder="Enter fees", type="number"),

                    dbc.Label("Tags", className="mt-3"),
                    dbc.Input(id="input-tags", placeholder="Enter tags", type="text"),

                    dbc.Label("Type", className="mt-3"),
                    html.Div(
                        [
                            
                            dbc.RadioItems(
                                id="input-longshort",
                                options=[
                                    {"label": "Long", "value": "Long"},
                                    {"label": "Short", "value": "Short"},
                                ],
                                value="Long",
                                inline=True,
                                className="w-auto",
                            ),
                        ],
                        className="d-flex flex-column justify-content-center align-items-center"
                    ),
                ], width=6),
            ]),

            dbc.Row([
                dbc.Label("Grade", className="mt-3"),
                dcc.Slider(id='input-grade', min=1, max=10, step=1, value=1, className="slider-custom"),
            ]),

            dbc.Row([
                #enable upload
                dcc.Upload(
                    id="upload-image",
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select an Image')
                    ]),
                    multiple=False,
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin": "10px 0"
                    },
                ),
           
            ]),

            dbc.Row([
                dbc.Col(
                    dbc.Button("Submit Trade", id="submit-btn", size="sm", className="rounded-pill custom-submit w-100"),
                    width=4
                ),
                dbc.Col(
                    dbc.Button("Clear Items", id="clear-items-btn", size="sm", className="rounded-pill custom-clear w-100"),
                    width=4
                ),
                dbc.Col(
                    dbc.Button("Delete Recent", id="delete-recent-btn", size="sm", className="rounded-pill custom-delete w-100"),
                    width=4
                ),
            ], className="pt-4"),

            html.Div(id="submit-message", className="pt-3"),
        ], style={"maxWidth": "600px", "margin": "auto"})
    ]),

    #trade data table
    html.H2("Recent Trade Data", className="pt-4 pb-4 text-center"),
    html.Div(id="trade-data-table", style={"overflowX": "auto", "maxWidth": "100%"}),

    dcc.Store(id='stored-image-data', data=None), 
    update_flag_store,
], className="px-4 pb-4")

@callback(
    Output("submit-message", "children"),
    Output('stored-image-data', 'data'),
    Output("input-ticker", "value"),
    Output("input-entry", "value"),
    Output("input-exit", "value"),
    Output("input-pl", "value"),
    Output("input-risk", "value"),
    Output("input-longshort", "value"),
    Output("input-grade", "value"),
    Output("input-entryT", "value"),
    Output("input-exitT", "value"),
    Output("input-fees", "value"),
    Output("input-tags", "value"),
    Output("update-flag", "data"),
    Input("submit-btn", "n_clicks"),
    Input('clear-items-btn', 'n_clicks'),
    Input('delete-recent-btn', 'n_clicks'),
    Input('upload-image', 'contents'),
    State("input-ticker", "value"),
    State("input-entry", "value"),
    State("input-exit", "value"),
    State("input-pl", "value"),
    State("input-risk", "value"),
    State("input-longshort", "value"),
    State("input-grade", "value"),
    State("input-entryT", "value"),
    State("input-exitT", "value"),
    State("input-fees", "value"),
    State('upload-image', 'filename'),
    State('stored-image-data', 'data'),
    State("input-tags", "value"),
    State("update-flag", "data"),
    prevent_initial_call=True
)

#unified callback to handle data validation and all buttons
def unified_callback(submit, clear, delete, upload_contents, ticker, entry, exit, pl, risk, longshort, grade, entryT, exitT, fees, filename, stored_image, tags, current_flag):
    trigger_id = dash.callback_context.triggered_id
    if trigger_id == "delete-recent-btn":
        delete_recent()
        return *no_updates(13), (0 if current_flag is None else current_flag + 1)

    if trigger_id == "clear-items-btn":
        return "", None, None, "", None, None, None, "Long", 1, None, None, None, "", (0 if current_flag is None else current_flag + 1)

    if trigger_id == "submit-btn":
        required_fields = [ticker, entry, exit, pl, risk, longshort, grade, entryT, exitT, fees]
        if any(field in (None, "") for field in required_fields):
            return (
                dbc.Alert("Please fill in all required fields.", color="danger", dismissable=True, fade=True),
                *no_updates(13)
            )
        
        if not stored_image:
            return (
                dbc.Alert("Please upload an image.", color="danger", dismissable=True, fade=True),
                *no_updates(13)
            )

        #convert image to bytes
        if stored_image:
            img_bytes = base64_to_bytes(stored_image['contents'])
        else:
            img_bytes = None

        #save to db
        insert_trade((
            dt.datetime.now().strftime('%Y-%m-%d'),
            ticker,
            longshort,
            entry,
            exit,
            entryT,
            exitT,
            risk,
            pl,
            fees,
            tags,
            grade,
            img_bytes,
            ))

        return (
                dbc.Alert("Trade submitted successfully!", color="success", dismissable=True, fade=True),
                None, None, "", None, None, None, "Long", 1, None, None, None, "", (0 if current_flag is None else current_flag + 1)
        )
    
    if trigger_id == "upload-image":
        if not upload_contents:
            return None, None, *no_updates(12)
        return (
            dbc.Alert("Image uploaded successfully!", color="success", dismissable=True, fade=True),
            {'contents': upload_contents, 'filename': filename}, *no_updates(12)
        )


#update on update flag
@callback(
    Output("trade-data-table", "children"),
    Input("update-flag", "data"),
    prevent_initial_call=False,
)

def update(current_flag):
    df = top_recent()
    if 'Image' in df.columns:
        df = df.drop(columns=['Image'])
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=False).dt.strftime('%Y-%m-%d')
    
    #self construct table iteratively by row for conditional formatting
    header = [html.Th(col) for col in df.columns]
    
    body = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col == "P&L":
                color = "green" if value > 0 else "red" if value < 0 else "black"
                cells.append(html.Td(f"{value:.2f}", style={"color": color}))
            else:
                cells.append(html.Td(value))
        body.append(html.Tr(cells))

    table = dbc.Table(
        [html.Thead(html.Tr(header)), html.Tbody(body)],
        bordered=True,
        striped=True,
        hover=False,
        className="table-custom"
    )
    return table

