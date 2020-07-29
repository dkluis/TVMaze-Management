import time
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from db_lib import connect_pd

print(f'Starting Visualize Statistics Plots')

refresh = 1800

con = connect_pd()
df = pd.read_sql_query('select * from statistics where statrecind = "TVMaze" order by statepoch asc', con)
df2 = pd.read_sql_query('select * from statistics where statrecind = "Downloaders" order by statepoch asc', con)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

fig9 = go.Figure()
fig9.add_trace(go.Scatter(x=df['statdate'], y=df['tvmshows'], name='All TV Shows', mode='lines'))
fig9.update_layout(xaxis_title='All TV Shows in TVMaze', title_text='All TV Shows in TVMaze', yaxis_title='Shows')

showfig = make_subplots(rows=1, cols=5)
showfig.append_trace(go.Scatter(x=df['statdate'], y=df['myshows'], name='All',
                                showlegend=False), row=1, col=1)
showfig.update_xaxes(title_text="'All'", row=1, col=1)
showfig.append_trace(go.Scatter(x=df['statdate'], y=df['myshowsended'], name='Ended',
                                showlegend=False), row=1, col=2)
showfig.update_xaxes(title_text="'Ended'", row=1, col=2)
showfig.append_trace(go.Scatter(x=df['statdate'], y=df['myshowstbd'], name='In Limbo',
                                showlegend=False), row=1, col=3)
showfig.update_xaxes(title_text="'In Limbo'", row=1, col=3)
showfig.append_trace(go.Scatter(x=df['statdate'], y=df['myshowsrunning'], name='Running',
                                showlegend=False), row=1, col=4)
showfig.update_xaxes(title_text="'Running'", row=1, col=4)
showfig.append_trace(go.Scatter(x=df['statdate'], y=df['myshowsindevelopment'], name='In Development',
                                showlegend=False), row=1, col=5)
showfig.update_xaxes(title_text="'In Development'", row=1, col=5)
showfig.update_layout(title_text="All the 'Followed' shows related Stats", yaxis_title="Shows")

epifig = make_subplots(rows=1, cols=6)
epifig.append_trace(go.Scatter(x=df['statdate'], y=df['myepisodes'], name='Total',
                               showlegend=False), row=1, col=1)
epifig.update_xaxes(title_text="'All'", row=1, col=1)
epifig.append_trace(go.Scatter(x=df['statdate'], y=df['myepisodesskipped'], name='Skipped',
                               showlegend=False), row=1, col=2)
epifig.update_xaxes(title_text="'Skipped'", row=1, col=2)
epifig.append_trace(go.Scatter(x=df['statdate'], y=df['myepisodeswatched'], name='Watched',
                               showlegend=False), row=1, col=3)
epifig.update_xaxes(title_text="'Watched'", row=1, col=3)
epifig.append_trace(go.Scatter(x=df['statdate'], y=df['myepisodestowatch'], name='To Watch',
                               showlegend=False), row=1, col=4)
epifig.update_xaxes(title_text="'To Watch'", row=1, col=4)
epifig.append_trace(go.Scatter(x=df['statdate'], y=df['myepisodestodownloaded'], name='To Acquire',
                               showlegend=False), row=1, col=5)
epifig.update_xaxes(title_text="'To Acquire'", row=1, col=5)
epifig.append_trace(go.Scatter(x=df['statdate'], y=df['myepisodesannounced'], name='Coming Soon',
                               showlegend=False), row=1, col=6)
epifig.update_xaxes(title_text="'Coming Soon'", row=1, col=6)
# epifig.update_layout(xaxis_title='', title_text="All the episodes related Stats for 'Followed' Shows")
epifig.update_layout(title_text="All the episode related Stats for 'Followed' Shows", yaxis_title="Episodes")

dwnldfig = make_subplots(rows=1, cols=11)
dwnldfig.update_layout(title_text="All the 'Downloader' assignment Stats", yaxis_title="Shows")
dwnldfig.append_trace(go.Scatter(x=df2['statdate'], y=df2['showrss'], name='ShowRSS',
                                 showlegend=False), row=1, col=1)
dwnldfig.update_xaxes(title_text="'ShowRSS'", row=1, col=1)
dwnldfig.append_trace(go.Scatter(x=df2['statdate'], y=df2['rarbgapi'], name='rarbgAPI',
                                 showlegend=False), row=1, col=2)
dwnldfig.update_xaxes(title_text="'rarbgAPI'", row=1, col=2)
dwnldfig.append_trace(go.Scatter(x=df2['statdate'], y=df2['rarbg'], name='rarbg',
                                 showlegend=False), row=1, col=3)
dwnldfig.update_xaxes(title_text="'rarbg'", row=1, col=3)
dwnldfig.append_trace(go.Scatter(x=df2['statdate'], y=df2['eztvapi'], name='eztvAPI',
                                 showlegend=False), row=1, col=5)
dwnldfig.update_xaxes(title_text="'eztvAPI'", row=1, col=5)
dwnldfig.append_trace(go.Scatter(x=df2['statdate'], y=df2['eztv'], name='eztv',
                                 showlegend=False), row=1, col=6)
dwnldfig.update_xaxes(title_text="'eztv'", row=1, col=6)
dwnldfig.append_trace(go.Scatter(x=df2['statdate'], y=df2['rarbgmirror'], name='rarbgmirror',
                                 showlegend=False), row=1, col=4)
dwnldfig.update_xaxes(title_text="'rarbgmirror'", row=1, col=4)
dwnldfig.append_trace(go.Scatter(x=df2['statdate'], y=df2['magnetdl'], name='magnetdl',
                                 showlegend=False), row=1, col=7)
dwnldfig.update_xaxes(title_text="'magnetdl'", row=1, col=7)
dwnldfig.append_trace(go.Scatter(x=df2['statdate'], y=df2['torrentfunk'], name='torrentfunk',
                                 showlegend=False), row=1, col=8)
dwnldfig.update_xaxes(title_text="'torrentfunk'", row=1, col=8)
dwnldfig.append_trace(go.Scatter(x=df2['statdate'], y=df2['nodownloader'], name='Not Assigned',
                                 showlegend=False), row=1, col=9)
dwnldfig.update_xaxes(title_text="'Not Assigned'", row=1, col=9)
dwnldfig.append_trace(go.Scatter(x=df2['statdate'], y=df2['skipmode'], name='Skip Mode',
                                 showlegend=False), row=1, col=10)
dwnldfig.update_xaxes(title_text="'Skip Mode'", row=1, col=10)
dwnldfig.append_trace(go.Scatter(x=df2['statdate'], y=df2['piratebay'], name='Piratebay',
                                 showlegend=False), row=1, col=11)
dwnldfig.update_xaxes(title_text="'Piratebay'", row=1, col=11)

app.layout = html.Div(children=[
    html.H2(children='TVMaze Statistics'),
    html.Div(children=''),
    dcc.Graph(id='TVMazeShows', figure=fig9),
    html.Div(children=''),
    dcc.Graph(id='MyShows', figure=showfig),
    html.Div(children=''),
    dcc.Graph(id='MyEpisodes', figure=epifig),
    html.Div(children=''),
    dcc.Graph(id='Downloaders', figure=dwnldfig),
    html.H6("Change the refresh interval"),
    html.Div(["Interval (Seconds): ",
             dcc.Input(id='my-input', value=refresh, type='number')]),
    html.Br(),
    html.Div(id='my-output'),
])


@app.callback(
    Output('my-output', 'children'),
    [Input('my-input', 'value')]
    )
def update_output_div(input_value):
    refresh = input_value
    update_metrics()
    return refresh
    # return 'Output: {}'.format(input_value)


def update_metrics():
    time.sleep(refresh)
    df1 = pd.read_sql_query('select * from statistics order by statepoch asc', con)
    print(refresh)
    return df1


if __name__ == '__main__':
    app.run_server(debug=True)

