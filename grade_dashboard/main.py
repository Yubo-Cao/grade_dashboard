import asyncio

import dash
from dash import dcc
from dash import html as h

from .analyze import plot_blame, plot_contrib, plot_score_by_type, plot_scores
from .parse import parse
from .spider import fetch, on_exit


async def run():
    data = parse(await fetch("202016378", "202016378"))
    try:
        app = dash.Dash()
        app.layout = h.Div(
            [
                dcc.Graph(
                    figure=plot_scores(
                        data,
                        type="radar",
                        normalize=True,
                        weighted=True,
                    ),
                    id="scores",
                ),
            ]
        )
        app.run_server(debug=True)
    finally:
        await on_exit()


if __name__ == "__main__":
    asyncio.run(run())
