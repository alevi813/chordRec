import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
# import sqlite3

# import app-specific functions
from dbCheck_track import *
from processPlaylist import *
from chordSimilarity import *

# GET THE DATA
# conn = sqlite3.connect('/Users/aaronlevi/Documents/sql_db/chords_list.db')
# cur = conn.cursor()
# song_info = pd.read_sql_query("SELECT * FROM basic_info", conn)
song_info = pd.read_csv('song_info.csv')
dblist    = song_info['Song'].tolist()
# song_info.drop('index', axis=1, inplace=True)
# allFeatures = pd.read_sql_query("SELECT * FROM features", conn)    
allFeatures = pd.read_csv('allFeatures.csv')
# allFeatures.drop('index', axis=1, inplace=True)
# isAdv = pd.read_sql_query("SELECT model_isAdv FROM label", conn) 
isAdv = pd.read_csv('isAdv.csv')


# ------------------------------------------------------------------------------
# DASH DASH DASH DASH DASH DASH DASH

# app = JupyterDash(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    # html.Img(src='/assets/guitarHole.jpg', style={'background-image'}), 

    html.H1("PICK-A-TUNE", style={'textAlign': 'center',
            'color': 'white',
            'background-image': "url('/assets/guitarHole.jpg')",
            'background-repeat': 'no-repeat',
            'background-position': 'center',
            'background-size': 'cover',
    #         'position': 'fixed',
            'min-width': '100%',
    #         'min-height':'100%',
    #         }),
    # html.Div(style={'textAlign': 'center',
    #         'background-image': "url('/assets/guitarHole.jpg')",
    #         'background-repeat': 'no-repeat',
    #         'background-position': 'center',
    #         'background-size': 'cover',
    #         'position': 'fixed',
         }),
    
    html.H4("Enter a playlist you enjoy", style={'textAlign': 'center'}),

    html.Div([#"Input: ",
          dcc.Input(id='playlist', 
                    placeholder='spotify url',
                    debounce= True,
                    type='text', 
                        )],
            style=dict(display='flex', justifyContent='center')
    ),
    
    html.Br(),
    
    html.H4("Enter a song you know", style={'textAlign': 'center'}),
    
    html.Div([#"Input: ",
              dcc.Input(id='known_song', 
                        placeholder='artist, title',
                        debounce= True,
                        type='text',
                        
                        )],
              style=dict(display='flex', justifyContent='center')
              ),   

    html.Div(id='in_song_chords', style={'textAlign': 'center'}),
    html.Br(),

    html.H4("Here's a song at your level", style={'textAlign': 'center'}),
    html.Div(id='ez_out_song', style={'textAlign': 'center'}),
    # html.A(id='ez_out_song', href= 'ez_out_link', target='_blank', style={'textAlign': 'center'}),
    # html.A(id='ez_out_song', href='https://www.ultimate-guitar.com/', target='_blank', style={'textAlign': 'center'}),
    html.Div(id='ez_out_artist', style={'textAlign': 'center'}),
    html.Div(id='ez_out_chords', style={'textAlign': 'center'}),
    
    html.H4("Here's a song to challenge yourself", style={'textAlign': 'center'}),
    html.Div(id='ch_out_song', style={'textAlign': 'center'}),
    # html.A(id='ch_out_song', href='ch_out_link', target='_blank', style={'textAlign': 'center'}),
    # html.A(id='ch_out_song', href='https://www.ultimate-guitar.com/', target='_blank', style={'textAlign': 'center'}),
    html.Div(id='ch_out_artist', style={'textAlign': 'center'}),
    html.Div(id='ch_out_chords', style={'textAlign': 'center'}),

])

# ------------------------------------------------------------------------------
# Callbacks
@app.callback(
#     Output("out-all-types", "children"),
#     [Input("input_{}".format(_), "value") for _ in ALLOWED_TYPES],

#    Output(component_id='out_song', component_property='children'),
    [Output(component_id='in_song_chords', component_property='children'),
     Output(component_id='ez_out_song', component_property='children'),
     # Output(component_id='ez_out_link', component_property='children'), # link!!
     Output(component_id='ez_out_artist', component_property='children'),
     Output(component_id='ez_out_chords', component_property='children'),
     
     Output(component_id='ch_out_song', component_property='children'),
     # Output(component_id='ch_out_link', component_property='children'), # link!!
     Output(component_id='ch_out_artist', component_property='children'),
     Output(component_id='ch_out_chords', component_property='children')
    ],
    
    [Input(component_id='known_song', component_property='value'),
     Input(component_id='playlist', component_property='value')]
)
def getRec(track, playlist):
    # process initial inputs
    known_df, known_ix = dbCheck_track(track, song_info)
    known_df['isAdv'] = isAdv.loc[known_ix][0]
    known_df['nChords'] = allFeatures['n_unique_chords'].loc[known_ix]

    pl_indb  = processPlaylist(playlist, dblist)

    # get chords and features for playlist songs in db
    input_df = song_info.loc[pl_indb]
    input_df['isAdv'] = isAdv.loc[pl_indb]
    input_df['nChords'] = allFeatures['n_unique_chords'].loc[pl_indb]

    input_df.drop('index', axis=1, inplace=True)
    input_df.reset_index(drop=True, inplace=True)

    easy_rec, medium_rec, hard_rec = chordSimilarity(known_df, input_df)

    # return known_df['Chords'][0], easy_rec['Song'].replace('-', ' ').title(), easy_rec['Link'], easy_rec['Artist'].replace('-', ' ').title(), easy_rec['Chords'], hard_rec['Song'].replace('-', ' ').title(), hard_rec['Link'], hard_rec['Artist'].replace('-', ' ').title(), hard_rec['Chords']
    return known_df['Chords'][0], easy_rec['Song'].replace('-', ' ').title(), easy_rec['Artist'].replace('-', ' ').title(), easy_rec['Chords'], hard_rec['Song'].replace('-', ' ').title(), hard_rec['Artist'].replace('-', ' ').title(), hard_rec['Chords']
    # return known_df['Chords'][0], easy_rec['Song'].replace('-', ' ').title(), easy_rec['Link'], easy_rec['Artist'].replace('-', ' ').title(), easy_rec['Chords'], hard_rec['Song'].replace('-', ' ').title(), hard_rec['Artist'].replace('-', ' ').title(), hard_rec['Chords']

    
if __name__ == "__main__":
     app.run_server(debug=False)
