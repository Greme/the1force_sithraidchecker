import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import requests
import json
import pandas as pd
#from statusReturn import *

gearToMedal = {1: 'Training', 2: 'Training', 3: 'Training', 4: 'Training', 5: 'Training', 6: 'Training', 7: 'Training', 8: 'Training', 9: 'Training', 10: 'Bronze', 11: 'Silver', 12: 'Gold'}

def p1resistance(unit_list, tier):
    team_dict = {x['data']['base_id']: x['data'] for x in unit_list if
                 x['data']['base_id'] in ['REYJEDITRAINING', 'BB8', 'RESISTANCETROOPER', 'REY',
                                          'R2D2_LEGENDARY'] and x['data']['rarity'] >= tier}
    if len(team_dict) < 5:
        return "Fail: incomplete"
    # If member doesn't have JTR leader zeta or BB8 roll with punches, it's possible, but score will be bad.
    elif not (('leaderskill_REYJEDITRAINING' in team_dict['REYJEDITRAINING']['zeta_abilities']) and (
            'uniqueskill_BB801' in team_dict['BB8']['zeta_abilities'])):
        return 'Bronze'
    else:
        minGear = min([team_dict[x]['gear_level'] for x in team_dict])
        return gearToMedal[minGear]


def p3sisters(unit_list, tier):
    team_dict = {x['data']['base_id']: x['data'] for x in unit_list if
                 x['data']['base_id'] in ['MOTHERTALZIN', 'ASAJVENTRESS', 'NIGHTSISTERINITIATE', 'DAKA',
                                          'NIGHTSISTERZOMBIE'] and x['data']['rarity'] >= tier}
    if len(team_dict) < 5:
        # probably need to do checks against spirit too in here...
        return "Fail: incomplete"
    # These zetas are required
    elif not (('uniqueskill_ASAJVENTRESS01' in team_dict['ASAJVENTRESS']['zeta_abilities']) and (
            'leaderskill_MOTHERTALZIN' in team_dict['MOTHERTALZIN']['zeta_abilities'])):
        return "Fail: zetas"
    else:
        minGear = min([team_dict[x]['gear_level'] for x in team_dict])
        return gearToMedal[minGear]


def p3chexmix(unit_list, tier):
    team_dict = {x['data']['base_id']: x['data'] for x in unit_list if
                 x['data']['base_id'] in ['COMMANDERLUKESKYWALKER', 'CHIRRUTIMWE', 'DEATHTROOPER', 'PAO',
                                          'HANSOLO'] and x['data']['rarity'] >= tier}
    if len(team_dict) < 5:
        # probably need to do checks against alternative subs too in here...
        return "Fail: incomplete"
    # Pretty much required zeta
    elif not ('uniqueskill_HANSOLO01' in team_dict['HANSOLO']['zeta_abilities']):
        return "Fail: zetas"
    else:
        minGear = min([team_dict[x]['gear_level'] for x in team_dict])
        return gearToMedal[minGear]


def p3greedomix(unit_list, tier):
    team_dict = {x['data']['base_id']: x['data'] for x in unit_list if
                 x['data']['base_id'] in ['BOBAFETT', 'GREEDO', 'DEATHTROOPER', 'PAO', 'CHIRRUTIMWE'] and x['data'][
                     'rarity'] >= tier}
    if len(team_dict) < 5:
        # probably need to do checks against alternative subs too in here...
        return "Fail: incomplete"
    else:
        minGear = min([team_dict[x]['gear_level'] for x in team_dict])
        return gearToMedal[minGear]


def p4sisters(unit_list, tier):
    team_dict = {x['data']['base_id']: x['data'] for x in unit_list if
                 x['data']['base_id'] in ['MOTHERTALZIN', 'ASAJVENTRESS', 'TALIA', 'DAKA', 'NIGHTSISTERZOMBIE'] and
                 x['data']['rarity'] >= tier}
    if len(team_dict) < 5:
        return "Fail: incomplete"
    # These zetas are required
    elif not (('uniqueskill_ASAJVENTRESS01' in team_dict['ASAJVENTRESS']['zeta_abilities']) and (
            'leaderskill_ASAJVENTRESS' in team_dict['ASAJVENTRESS']['zeta_abilities'])):
        return "Fail: zetas"
    else:
        minGear = min([team_dict[x]['gear_level'] for x in team_dict])
        return gearToMedal[minGear]

r = requests.get('https://swgoh.gg/api/guild/12991')
guildData = json.loads(r.content)['players']
startDF = pd.DataFrame({'name': [x['data']['name'] for x in guildData], 'units':[x['units'] for x in guildData]})
		
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    html.H1('The 1 Force (Heroic) Sith Raid readiness tool'),
    dcc.Dropdown(
        id='dropdown',
        options=[{'label': i, 'value': i} for i in [1,2,3,4,5,6,7]],
        value=7
    ),
    html.Div(id='display-table'),
	html.Div(id='hidden-div')
])

@app.callback(dash.dependencies.Output('display-table', 'children'),
              [dash.dependencies.Input('dropdown', 'value')])
def display_table(value, max_rows=50):
	tempDF = startDF.copy()
	tempDF['p1resistance'] = tempDF['units'].apply(lambda row: p1resistance(row, value))
	tempDF['p3sisters'] = tempDF['units'].apply(lambda row: p3sisters(row, value))
	tempDF['p3chexmix'] = tempDF['units'].apply(lambda row: p3chexmix(row, value))
	tempDF['p3greedomix'] = tempDF['units'].apply(lambda row: p3greedomix(row, value))
	tempDF['p4sisters'] = tempDF['units'].apply(lambda row: p4sisters(row, value))
	tempDF.drop(columns=['units'], inplace=True)
	summaryDf = tempDF.apply(pd.value_counts)
	summaryDf = summaryDf.loc[["Gold","Silver","Bronze","Training"]]
	summaryDf.drop(columns=['name'], inplace=True)
	summaryDf = summaryDf.T
	summaryDf.index.name = 'Team'
	summaryDf.reset_index(inplace=True)
	return ([html.H3(f'Summary stats for tier - {value}'),
	html.Table([html.Tr([html.Th(col) for col in summaryDf.columns])] + [html.Tr([html.Td(summaryDf.iloc[i][col]) for col in summaryDf.columns]) for i in range(min(len(summaryDf), max_rows))]),
	html.H3('Full breakdown'),
	html.Table([html.Tr([html.Th(col) for col in tempDF.columns])] + [html.Tr([html.Td(tempDF.iloc[i][col]) for col in tempDF.columns]) for i in range(min(len(tempDF), max_rows))])
	])

if __name__ == '__main__':
    app.run_server(debug=True)