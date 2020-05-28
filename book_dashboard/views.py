import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
#import matplotlib
#matplotlib.use('TkAgg')
from io import BytesIO
import base64
from plotly.subplots import make_subplots


from book_dashboard.utils import top_5_recommendations,get_output_dataset
def plot_wordcloud(data):
    wc = WordCloud(background_color='black', width=1300, height=600)
    wc.generate(' '.join(data))
    return wc.to_image()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

dash_app = dash.Dash(__name__,
                     external_stylesheets=external_stylesheets)
server = dash_app.server

dash_app.layout = html.Div([

    html.H1("Book Crossing with Dash !", style={"text-align":"center"}),

    html.Div(
        [
            dcc.Input(
                placeholder="Enter User ID",
                id="query-input",
                style={"width":"60%"},
                ),
            html.Button(id='submit-button', n_clicks=0, children='Submit'),
            html.Div(id='dummy'),
            
        ]
        , style={"text-align":"center", "width":"100%", "columnCount":2}),
    html.H2("Top 5 recommended Books", style={"text-align": "center"}),

    html.Table(
        [
            html.Thead(
                html.Tr(
                    [html.Th("Book Title"),
                     html.Th("Book Author"),
                     html.Th("Publisher"),
                     html.Th("Year Of Publication"),
                     html.Th("Cover Image URL"), ]
                )
            ),
             html.Tbody([
                html.Th('-'),
                html.Th('-'),
                html.Th('-'),
                html.Th('-'),
                html.Th('-'),
            ], id="Top5-table")
        ], style={"width": "100%"}
    ),

    html.H2("Top rated Books", style={"text-align": "center"}),

    html.Img(id="image_wc"),

    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # in milliseconds
        n_intervals=0
    ),

])


# ------------------------------- CALLBACKS ---------------------------------------- #

@dash_app.callback(Output("dummy", "children"), [Input("submit-button", "n_clicks")], [State("query-input", "value")])
def new_search(n_clicks, query):
    if not query:
        return "Please enter User ID"
    query =int(query.strip()) 
    print(f"got a query {query}")   
    return f"Dashboard started working on {query}..."

@dash_app.callback(Output('Top5-table', 'children'),[Input('submit-button', 'n_clicks')], [State("query-input", "value")])
                  
def update_table(n_clicks,query1):
    if not query1:
        out_data=get_output_dataset()
    else:
        query1 =int(query1.strip()) 
        out_data=top_5_recommendations(query1)
       
    output_table = []
    for i in range(len(out_data)):
        output_table.append(
        html.Tr([
                html.Th(out_data.iloc[i]['Book-Title'], style={"color": "#3366ff"}),
                html.Th(out_data.iloc[i]['Book-Author'], style={"color": "#009900"}),
                html.Th(out_data.iloc[i]['Publisher'], style={"color": "#009900"}),
                html.Th(out_data.iloc[i]['Year-Of-Publication'], style={"color": "#009900"}),
                html.Th(out_data.iloc[i]['Image-URL-L'], style={"color": "#009900"}),
               
                ]))
    return output_table

@dash_app.callback(Output('image_wc', 'src'),[Input('submit-button', 'n_clicks')], [State("query-input", "value")])
                 
def make_image (n_clicks,query1):
    if not query1:
        out_data=get_output_dataset()
    else:
        query1 =int(query1.strip()) 
        out_data=top_5_recommendations(query1)
    img = BytesIO()
    plot_wordcloud(data=out_data['Book-Title']).save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())