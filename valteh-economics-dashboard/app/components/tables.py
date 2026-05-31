from dash import dash_table


def data_table(table_id: str, rows: list[dict], page_size: int = 10) -> dash_table.DataTable:
    columns = [{"name": key.replace("_", " ").title(), "id": key} for key in (rows[0].keys() if rows else [])]
    return dash_table.DataTable(
        id=table_id,
        data=rows,
        columns=columns,
        page_size=page_size,
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"fontFamily": "Inter, Arial, sans-serif", "fontSize": 13, "padding": "8px", "textAlign": "left"},
        style_header={"fontWeight": "700", "backgroundColor": "#f8f9fa"},
    )
