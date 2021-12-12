import json
import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pandas as pd

# import callbacks

with open("src/app/configs/dash-config.json", "r") as file:
    dash_config = json.load(file)
# df = pd.read_csv('/home/jovyan/src/app/data/iranian_students.csv')
profile_df = pd.read_csv(dash_config["profile_data_path"])
post_df = pd.read_csv(dash_config["post_data_path"])
comment_df = pd.read_csv(dash_config["comment_data_path"])

# process data
kol_positivity_df = comment_df[["pos", "neu", "neg", "post_id"]].merge(
    post_df[["post_id", "kol_username"]],
    how="left",
    on="post_id"
).groupby(["kol_username"])[["pos", "neu", "neg", "post_id"]].mean().reset_index()

sentiment_overall_df = comment_df[["post_id", "pos", "neg", "neu"]].merge(
    post_df[["kol_username", "post_id", "videos"]],
    how="left",
    on="post_id"
).drop(["post_id"], axis=1)
kol_sentiment = sentiment_overall_df.groupby(["kol_username"]).mean().reset_index()
colors = px.colors.qualitative.T10
kol_sentiment_array = kol_sentiment[['pos', 'neg', 'neu']].to_numpy()
kol_names = kol_sentiment["kol_username"].to_list()

# set app variable with dash, set external style to bootstrap theme SUPERHERO or SANDSTONE
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.SANDSTONE],
    meta_tags=[
        {
            'name': 'viewport', 
            'content': 'width=device-width, initial-scale=1'
        }
    ]
)

# add server for production mode, it's fine to leave it here is debug mode
server = app.server

# set applicaiton title
app.title = 'Instagram KOL Anlysis'

navbar = html.Div(
    children = \
        [
            dbc.NavbarSimple(
                children=[
                    dbc.NavItem(dbc.NavLink("Project Overview", href="/", active="exact")),
                    dbc.NavItem(dbc.NavLink("Advanced Posts Analysis", href="/page-1", active="exact")),
                    dbc.NavItem(dbc.NavLink("Advanced Comments Analysis", href="/page-2", active="exact"))
                ],
                brand="Instagram KOL Anlysis",
            )
        ],
    className="nav-bar"
)

content = html.Div(
    id="page-content", 
    children=[], 
    className="content-style"
)

app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    content
])

fig_profile_1 = px.bar(
    profile_df, 
    x='kol_username', 
    y='followers_count'
)
fig_profile_1.update_layout(
    plot_bgcolor='#f8f5f0',
    paper_bgcolor='white',
    font={'color':'darkslategray'},
    legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1)
)
fig_profile_1.update_traces(
    marker_color="#AE8F6F",
    opacity=0.8
)
fig_profile_2 = px.scatter(
    profile_df, 
    x="followers_count", 
    y="postss_count", 
    color="kol_username",
    size="followers_count",
    hover_data=["kol_username"]
)
fig_profile_2.update_layout(
    plot_bgcolor='#f8f5f0',
    paper_bgcolor='white',
    font={'color':'darkslategray'},
    legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1)
)

fig_comments_1 = go.Figure(data=[
    go.Bar(
        name='Positive Sentiment', 
        x=kol_positivity_df["kol_username"], 
        y=kol_positivity_df["pos"], 
        marker_color="#AE8F6F", 
        opacity=0.8),
    go.Bar(name='neu', x=kol_positivity_df["kol_username"], y=kol_positivity_df["neu"], marker_color="#6FAE70", opacity=0.8),
    go.Bar(name='neg', x=kol_positivity_df["kol_username"], y=kol_positivity_df["neg"], marker_color="#6F8EAE", opacity=0.8)
])
# Change the bar mode
fig_comments_1.update_layout(
    barmode='group', 
    plot_bgcolor='#f8f5f0',
    paper_bgcolor='white')

fig_comments_2 = go.Figure()
for i in range(kol_sentiment_array.shape[0]):
    fig_comments_2.add_trace(go.Violin(x=kol_sentiment_array[i, :], line_color=colors[i], name=kol_names[i], meanline_visible=True))
fig_comments_2.update_traces(orientation='h', side='positive', width=2, points=False)
fig_comments_2.update_layout(
    # title="Overall Sentiments of each KOL", 
    title_xanchor="left", 
    title_font_size=18,
    plot_bgcolor='#f8f5f0',
    paper_bgcolor='white')
# fig_comments_3.update_layout(width=800)

@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return [
                html.Div(
                    [   
                        html.Div(
                            id="project-intro",
                            children=[
                                html.H2("Project Introduction"),
                                dcc.Markdown(
                                    '''
                                    This application is a portfolio project built by Jia-Pei Wu using Plotly's Dash. 
                                    In this project, I selected 9 KOLs related to "Parent-child" Series. The analysis
                                    consisted of using open source called [intagram-scraping](https://github.com/arc298/instagram-scraper) 
                                    library to scrape profile, posts, and comments.  Then, I used pandas to process 
                                    the data and load to Heroku Postgres. I loaded back the data again with some 
                                    filters into Dash App to generate the plots and the local website.

                                    The porject is built under Docker and Docker compose for development phase. Then
                                    all codes are packaged up by Docker Images and push to Docker Registery in Heroku.

                                    See my repository for this project: [instagram-kol-analysis](https://github.com/jiapei-wu/insta-kol-analysis)

                                    NOTE: Due to the sensitivity of instagram scraping, the project is solely for personal learning purpose.
                                    It does not have any business or profitable purpose. Hence, I keep all right of the code, 
                                    which mean you have no permission to use, modify, or share the code for your acedemic or business purpose.
                                    '''
                                )
                            ], 
                        )
                    ]
                ),
                html.H2(
                    'KOLs Followers',
                    style={'textAlign':'center'}
                ),
                dcc.Graph(
                    id='profile-1',
                    figure=fig_profile_1
                ),
                html.H2(
                    'Relationship Between Posts and Followers',
                    style={'textAlign':'center'}
                ),
                html.P(
                    'You can see that number of posts does not guarantee '\
                    'that you have more followers. Only very little relationship '\
                    'is observed',
                    style={'textAlign':'center'}
                ),
                dcc.Graph(
                    id='profile-2',
                    figure=fig_profile_2
                )
        ]

    elif pathname == "/page-1":
        return [
                html.H2('Relationship Between Posts and Followers',
                        style={'textAlign':'center'}),
                dcc.Graph(
                    id='post-1',
                    figure=fig_profile_2
                    )
                ]
    elif pathname == "/page-2":
        return [
            html.H2('Which KOL is more positive',
                    style={'textAlign':'center'}),
            dcc.Graph(
                id='comments-1',
                figure=fig_comments_1
            ),
            html.H2('Overall Positive Sentiment Distribution',
                    style={'textAlign':'center'}),
            dcc.Graph(
                id='comments-2',
                figure=fig_comments_2
            )
        ]
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

if __name__=='__main__':
    app.run_server(debug=True, port=3000)