from pathlib import Path

import dash
import dash_bootstrap_components as dbc

from app.config import get_settings
from app.layout import app_layout
from app.routes import register_routes


def create_app() -> dash.Dash:
    settings = get_settings()
    assets_folder = Path(__file__).resolve().parent / "assets"
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True,
        assets_folder=str(assets_folder),
        title=settings.app_name,
    )
    app.layout = app_layout()
    register_routes(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=get_settings().debug, host="0.0.0.0", port=8050)
