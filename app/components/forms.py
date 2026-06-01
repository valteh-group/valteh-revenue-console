import dash_bootstrap_components as dbc
from dash import html


def numeric_input(
    label: str,
    component_id: str,
    value: float,
    step: float = 1.0,
    tooltip: str | None = None,
) -> dbc.Col:
    return dbc.Col(
        [
            field_label(label, component_id, tooltip),
            dbc.Input(id=component_id, type="number", value=value, step=step),
        ],
        md=3,
    )


def field_label(label: str, component_id: str, tooltip: str | None = None) -> html.Div:
    if not tooltip:
        return html.Div(label, className="form-label")
    tooltip_id = f"{component_id}-info-tooltip"
    return html.Div(
        [
            html.Span(label),
            html.Span(
                [
                    html.Span("i", className="field-info-icon", **{"aria-label": "Information"}),
                    html.Span(tooltip, className="field-tooltip", id=tooltip_id, role="tooltip"),
                ],
                className="field-info-wrapper",
                **{"aria-describedby": tooltip_id},
            ),
        ],
        className="field-label-row",
    )
