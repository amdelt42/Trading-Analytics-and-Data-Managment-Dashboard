import dash
from dash import html
import dash_bootstrap_components as dbc

def get_footer():
    return html.Footer(
    dbc.Container(
        dbc.Row(
            dbc.Col("© 2025 ∇Dash", className="text-center")
        )
    ),
    className="footer-custom"
    )

def get_navbar():
    return dbc.Navbar(
        dbc.Container([
            dbc.Nav(
                [
                    dbc.NavLink(page["name"], href=page["path"], active="exact")
                    for page in dash.page_registry.values() 
                ],
                className="px-4"
            ),
            dbc.NavbarBrand("∇Dash", className="px-4"),
        ]),
        sticky="top",
        className="navbar-custom",
    )