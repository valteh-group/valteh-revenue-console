from decimal import Decimal

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def bar_chart(data: dict[str, Decimal], title: str) -> go.Figure:
    df = pd.DataFrame({"label": list(data.keys()), "value": [float(v) for v in data.values()]})
    fig = px.bar(df, x="label", y="value", title=title, text_auto=".2s")
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20), yaxis_title="MXN", xaxis_title="")
    return fig


def line_chart(df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    fig = px.line(df, x=x, y=y, markers=True, title=title)
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig


def pie_chart(data: dict[str, Decimal], title: str) -> go.Figure:
    fig = px.pie(names=list(data.keys()), values=[float(v) for v in data.values()], title=title, hole=0.45)
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig
