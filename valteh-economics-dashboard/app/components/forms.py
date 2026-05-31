import dash_bootstrap_components as dbc


def numeric_input(label: str, component_id: str, value: float, step: float = 1.0) -> dbc.Col:
    return dbc.Col(
        [
            dbc.Label(label),
            dbc.Input(id=component_id, type="number", value=value, step=step),
        ],
        md=3,
    )
