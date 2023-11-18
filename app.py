import dash
import plotly.express as px
from dash import dcc, Output, Input
from dash import html
import dash_bootstrap_components as dbc

from preprocessing import get_data, get_time_series

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

indicator = ["Human Development Index", "Female Smokers", "Male Smokers",
             "Life Expectancy", "Total Deaths Per Million", "Total Cases Per Million",
             "Alcoholic Beverages", 'Eggs', 'Fruits - Excluding Wine',
             'Plant Based Products', 'Animals Products']

dietary = ['Alcoholic Beverages', 'Eggs', 'Fruits - Excluding Wine', 'Meat',
           'Milk - Excluding Butter', 'Miscellaneous', 'Spices', 'Stimulants',
           'Animals Products', 'Sugas Crops & Sweeteners', 'Plant Based Products']

units = {col: "%" for col in dietary}
units.update({"Female Smokers": "%", "Male Smokers": "%", "Life Expectancy": "years", "Human Development Index": ""})

controls = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("The first indicator (global) / Diet component (Country specific)"),
                dcc.Dropdown(
                    id="x-variable",
                    options=[
                        {"label": f"{col})", "value": col} for col in indicator
                    ],
                    value="Plant Based Products",
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("The second indicator (global) / Disabled (Country specific)"),
                dcc.Dropdown(
                    id="y-variable",
                    options=[
                        {"label": col, "value": col} for col in indicator
                    ],
                    value="Total Deaths Per Million",
                ),
            ]
        ),
    ],
    body=True,
)

df = get_data("data/Food_Supply_Quantity_kg_Data.csv")
food = get_data("data/Food_Supply_Quantity_kg_Data.csv")
protein = get_data("data/Protein_Supply_Quantity_Data.csv")
fat = get_data("data/Fat_Supply_Quantity_Data.csv")
app.layout = html.Div(children=[
    dbc.Container(dbc.Row(
        [
            html.H1('COVID-19 Healthy Diet and Extra Factors'),
            html.H4(children='This visualizations shows different dietary or social factors and their interaction with '
                             'COVID-19 mortality.'),
        ], justify="center", align="center"
    )),

    dbc.Container(dbc.Row(
        "The dietary parts are measured in percentages to the whole intake. For example eggs=1.6 means, "
        "that in average, the diet consists of 1.6% of eggs. "

    )),

    html.Div(
        style={'position': 'relative'},
        children=[
            html.Div(
                html.Button('Reset World', id='world', n_clicks=0, className="btn btn-success"),
                style={'vertical-align': 'top', 'width': '10%',
                       'display': 'inline-block'}
            ),
            html.Div(
                children=dcc.Graph(id='main_map'),
                style={'vertical-align': 'top', 'width': '69%',
                       'display': 'inline-block'}
            ),
            html.Div(
                children=dbc.RadioItems(id='main_map_radios',
                                        options=[{'label': col.capitalize().replace("_", " "), 'value': col} for col in
                                                 indicator],
                                        value="Human Development Index",
                                        className="btn-group",
                                        inputClassName="btn-check",
                                        labelStyle={'display': 'block'},
                                        labelClassName="btn btn-success",
                                        labelCheckedClassName="active",
                                        style={'display': 'inline-block'}
                                        ),
                style={'vertical-align': 'top', 'width': '10%',
                       'display': 'inline-block'}
            ),
        ]),
    html.Hr(),
    dbc.Container(dbc.Row(
        [
            html.H1(id="my_h1"),
        ])),
    html.Div(
        children=dcc.Graph(id='time_series'),
        style={'vertical-align': 'top', 'width': '40%',
               'display': 'inline-block'}
    ),
    html.Div(
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(controls, md=4),
                        dbc.Col(dcc.Graph(id="fig2"), md=8),
                    ],
                    align="center",
                ),
            ],
            fluid=True,
        ),
        style={'vertical-align': 'top', 'width': '60%',
               'display': 'inline-block'}
    ),

    dbc.Row(dbc.Col(html.Div(["The visualizations are based on ",
                              html.A(children="Kaggle Dataset",
                                     href="https://www.kaggle.com/mariaren/covid19-healthy-diet-dataset"),
                              " and ",
                              html.A(children="Our World in Data",
                                     href="https://github.com/owid/covid-19-data/tree/master/public/data"),
                              ]), width={"size": 6, "offset": 3}, ), justify="center", align="center"),

])

time_series = get_time_series()


@app.callback(Output('my_h1', 'children'),
              Input('main_map', 'clickData'),
              Input("world", "n_clicks"))
def update_h1(main_map, n_clicks):
    if main_map and not dash.callback_context.triggered[0]['prop_id'].split('.')[0] == "world":
        country = main_map['points'][0]['customdata'][0]
    else:
        country = "World"
    return country


@app.callback(
    Output('x-variable', 'options'),
    Output('y-variable', 'options'),
    Input("main_map", "clickData"),
    Input("world", "n_clicks")
)
def update_dropdown_variable(main_map, n_clicks):
    if main_map and not dash.callback_context.triggered[0]['prop_id'].split('.')[0] == "world":
        options = ["Food Source", "Protein Source", "Fat Source"]
        return [{'label': i, 'value': i} for i in options], []
    else:
        return [{'label': i, 'value': i} for i in indicator], [{'label': i, 'value': i} for i in indicator]


@app.callback(
    Output('fig2', 'figure'),
    Input('x-variable', 'value'),
    Input('y-variable', 'value'),
    Input("main_map", "clickData"),
)
def update_fig2(x_variable, y_variable, main_map):
    iso_code = ""
    country = ""
    if main_map:
        iso_code = main_map['points'][0]['location']
        country = main_map['points'][0]['customdata'][0]
    if x_variable == "Food Source":
        src = food[food.iso_code == iso_code][dietary].T.reset_index()
        src.columns = ["Items", "Percentages"]
        return px.pie(src, values="Percentages", names="Items", title=f"{x_variable} in {country}")

    elif x_variable == "Protein Source":
        src = protein[protein.iso_code == iso_code][dietary].T.reset_index()
        src.columns = ["Items", "Percentages"]
        return px.pie(src, values="Percentages", names="Items", title=f"{x_variable} in {country}")

    elif x_variable == "Fat Source":
        src = fat[fat.iso_code == iso_code][dietary].T.reset_index()
        src.columns = ["Items", "Percentages"]
        return px.pie(src, values="Percentages", names="Items", title=f"{x_variable} in {country}")

    else:
        return px.scatter(df, x=x_variable, y=y_variable, hover_name="Country", title="")


@app.callback(
    Output("time_series", "figure"),
    Input("main_map", "clickData"),
    Input("world", "n_clicks")
)
def update_time_series(main_map, n_clicks):
    country = "world"
    if main_map and not dash.callback_context.triggered[0]['prop_id'].split('.')[0] == "world":
        iso_code = main_map['points'][0]['location']
        country = main_map['points'][0]['customdata'][0]
        iso_ts = time_series[time_series.iso_code == iso_code]

    else:
        iso_ts = time_series.groupby("Date").agg(
            {"New Cases Per Million": "sum", "New Deaths Per Million": "sum"}).reset_index()
    fig = px.bar(iso_ts, x="Date", y=["New Cases Per Million", "New Deaths Per Million"], barmode='overlay',
                 title=f"New cases and mortality caused by COVID-19 trends in the {country}",
                 )
    fig.update_layout(legend_title_text=f'Evolution of COVID-19 pandemic in the {country}')
    fig.layout.xaxis.dtick = 'M1'
    return fig


@app.callback(
    Output('main_map', 'figure'),
    Input('main_map_radios', 'value'))
def update_figure(main_map):
    fig = px.choropleth(df, locations="iso_code",
                        color=main_map,
                        hover_data=["Country", 'Total Deaths Per Million'],
                        scope="world",
                        color_continuous_scale='aggrnyl',
                        title=f"World map"
                        )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout(coloraxis_colorbar=dict(
        thicknessmode="pixels", thickness=35,
        yanchor="top", y=0.99,
        xanchor="left", x=0.01,

    ))
    fig.update_layout(transition_duration=500)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

# TODO add title to all graphs
# TODO show selected country somewhere
