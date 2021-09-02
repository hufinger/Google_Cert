import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

def get_schedule():
    HomeTeam = []
    AwayTeam = []
    Week = []
    for i in range(1,19):
        url = "https://www.pro-football-reference.com/years/2021/week_" + str(i) + ".htm"
        soup = requests.get(url).text
        soup = BeautifulSoup(soup, 'html.parser')

        my_divs = soup.find("div", class_= 'game_summaries').find_all("div", class_='game_summary nohover')


        for n in range(len(my_divs)):
            HomeTeam.append(my_divs[n].find_all('a')[2].text)
            AwayTeam.append(my_divs[n].find_all('a')[0].text)
            Week.append(i)
    return pd.DataFrame({'HomeTeam' : HomeTeam,
                         'AwayTeam' : AwayTeam,
                         'Week': Week})


def join_tax(df, schedule):
    df2 = pd.merge(df, schedule, left_on='Team', right_on='HomeTeam')
    return df2

def plot(df):
    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.P("Team:"),
        dcc.Dropdown(id = 'dropdown', options=[{'label' : i, 'value' : i} for i in df.Team.unique()], multi=False, placeholder = "Please select a team..."),
        dcc.Graph(id = 'choropleth'),
        html.Div(id='dd-output-container')
    ])


    @app.callback(Output("choropleth", 'figure'),
                  [Input('dropdown', 'value')])

    def display_choropleth(selector):
        filtered = df.loc[((df['HomeTeam'] == selector) | (df['AwayTeam'] == selector)),
                            ['States', 'TaxRate']]
        fig = px.choropleth(filtered, locations = filtered.States, color = filtered.TaxRate, scope = 'usa', locationmode="USA-states")
        fig.update_geos(fitbounds = 'locations', visible = False)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return fig

    #TODO change output above to datatable filtered by value and then use data table to graph
    app.run_server(debug=True)

if __name__ == '__main__':
    teams = ['New York Jets', 'New England Patriots', 'Buffalo Bills', 'Miami Dolphins',
    'Cleveland Browns', 'Cincinnati Bengals', 'Baltimore Ravens', 'Pittsburgh Steelers',
    'Indianapolis Colts', 'Houston Texans', 'Jacksonville Jaguars', 'Tennessee Titans',
    'Kansas City Chiefs', 'Las Vegas Raiders', 'Denver Broncos', 'Los Angeles Chargers',
    'Carolina Panthers', 'Tampa Bay Buccaneers', 'Atlanta Falcons', 'New Orleans Saints',
    'Chicago Bears', 'Green Bay Packers', 'Detroit Lions', 'Minnesota Vikings',
    'Seattle Seahawks', 'Los Angeles Rams', 'San Francisco 49ers', 'Arizona Cardinals',
    'New York Giants', 'Philadelphia Eagles', 'Dallas Cowboys', 'Washington Football Team']
    states = ['NJ', 'MA', 'NY', 'FL',
              'OH', 'OH', 'MD', 'PA',
              'IN', 'TX', 'FL', 'TN',
              'MO', 'NV', 'CO', 'CA',
              'NC', 'FL', 'GA', 'LA',
              'IL', 'WI', 'MI', 'MN',
              'WA', 'CA', 'CA', 'AZ',
              'NJ', 'PA', 'TX', 'VA']
    rates = [10.75, 5, 8.82, 0,
             4.797, 4.797, 5.75, 3.07,
             3.23, 0, 0, 0,
             5.4, 0, 4.55, 13.3,
             5.25, 0, 5.75, 6,
             4.95, 7.65, 4.25, 9.85,
             0, 13.3, 13.3, 8,
             10.75, 3.07, 0, 5.75]
    df = pd.DataFrame({'Team' : teams,
                       'States' : states,
                       'TaxRate' : rates})
    schedule = get_schedule()
    joined  = join_tax(df, schedule)
    plot(joined)