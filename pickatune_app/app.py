import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
# import sqlite3


# get spotify credentials
import spotipy
spotifyCred = pd.read_csv('spotifyCred.csv')
from spotipy.oauth2 import SpotifyClientCredentials
client_credentials_manager = SpotifyClientCredentials(client_id= spotifyCred['0'][0],
                                                     client_secret= spotifyCred['0'][1])
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# conn = sqlite3.connect('/Users/aaronlevi/Documents/sql_db/chords_list.db')
# cur = conn.cursor()
# get db...
# song_info = pd.read_sql_query("SELECT * FROM basic_info", conn)
song_info = pd.read_csv('song_info.csv')
dblist    = song_info['Song'].tolist()
# song_info.drop('index', axis=1, inplace=True)
# allFeatures = pd.read_sql_query("SELECT * FROM features", conn)    
allFeatures = pd.read_csv('allFeatures.csv')
# allFeatures.drop('index', axis=1, inplace=True)
# isAdv = pd.read_sql_query("SELECT model_isAdv FROM label", conn) 
isAdv = pd.read_csv('isAdv.csv')

def dbCheck_track(track):
    known_song   = str(track).split(', ')[1]
    artist = str(track).split(', ')[0]        

    if known_song.replace(' ', '-').lower() in dblist:
        knownSong_ix = dblist.index(known_song.replace(' ', '-').lower())

        # get chords and features for the known song
        known_df = pd.DataFrame(song_info.loc[knownSong_ix]).transpose()
        known_df['isAdv'] = isAdv.loc[knownSong_ix][0]
        known_df['nChords'] = allFeatures['n_unique_chords'].loc[knownSong_ix]

    known_df.drop('index', axis=1, inplace=True)
    known_df.reset_index(drop=True, inplace=True)
    
    return known_df

def processPlaylist(pl_link):
    # get playlist tracks        
    pl_id   = pl_link.split('playlist/')[1]
    pl_id   = pl_id.split('?')[0]

    pl_tracks  = []
    pl_artists = []
    pl_indb    = []

    results = sp.user_playlist('Spotify', pl_id,
                                fields='tracks,next,name')

    # check if their in the db
    for nItem in range(0, len(results['tracks']['items'])):
        pl_tracks.append(results['tracks']['items'][nItem]['track']['name'].split(' -')[0].replace(' ', '-').lower() )
        #     pl_tracks.append(results['tracks']['items'][nItem]['track']['name'].replace(' ', '-').lower())
        pl_artists.append(results['tracks']['items'][nItem]['track']['artists'][0]['name'].replace(' ', '-').lower())

        if pl_tracks[nItem] in dblist:
            pl_indb.append(dblist.index(pl_tracks[nItem]))

    return pl_indb


def chordSimilarity(known_df, input_df):
    isAdvList = input_df['isAdv'].tolist()
    targDifficulty = known_df['isAdv'][0]

    if targDifficulty is 1:
        sameDiff = [i for i, x in enumerate(isAdvList) if x]
    else:
        sameDiff = [i for i, x in enumerate(isAdvList) if not x]
        
    # narrow to only sameDiff songs
    sameDiff_df = input_df.loc[sameDiff]

    # get a list of songs with the same or few n unique chords
    close_n    = sameDiff_df['nChords'] <= known_df['nChords'][0]
    close_n_ix = [i for i, x in enumerate(close_n) if x]

    close_df = sameDiff_df.loc[close_n_ix]
    close_df.reset_index(drop=True, inplace=True)

    # if the known song is in the playlist, get rid of it.
    if known_df['Song'][0] in close_df['Song'].tolist():
        k_ix = close_df['Song'].tolist().index(known_df['Song'][0].replace(' ', '-').lower())

        close_df.drop(k_ix, axis=0, inplace=True)
        close_df.reset_index(drop=True, inplace=True)

    # get chords of known song
    known_chords_list = known_df['Chords'][0].split(',')

    close_nSameChords = []
    close_propSameChords = []

    far_nSameChords = []
    far_propSameChords = []

    # compare to list of chords in all other playlist songs
    for iSong in range(0, len(close_df)):
        close_nSameChords.append( len([ele for ele in known_chords_list if(ele in close_df['Chords'][iSong].split(','))]) )
        close_propSameChords.append( len([ele for ele in known_chords_list if(ele in close_df['Chords'][iSong].split(','))]) / len(close_df['Chords'][iSong].split(','))  )
            
    # take the ones with the highest proportion overlap        
    maxOverlap = np.argmax(close_propSameChords)
    minOverlap = np.argmin(close_propSameChords)

    easy_rec   = close_df.iloc[maxOverlap]
    medium_rec = close_df.iloc[minOverlap]

    # # DO SAME FOR AN ADVANCED SONG
    # get index of playlist songs in same class
    targDifficulty = 1

    if targDifficulty is 1:
        sameDiff = [i for i, x in enumerate(isAdvList) if x]
    else:
        sameDiff = [i for i, x in enumerate(isAdvList) if not x]

    # narrow to only sameDiff songs
    sameDiff_df = input_df.loc[sameDiff]    

    close_df = sameDiff_df
    close_df.reset_index(drop=True, inplace=True)

    nSameChords = []
    propSameChords = []
    cnt = 1

    for iSong in range(0, len(close_df)):
        if isinstance(close_df['Chords'][iSong], str):
            nSameChords.append( len([ele for ele in known_chords_list if(ele in close_df['Chords'][iSong].split(','))]) )
            propSameChords.append( len([ele for ele in known_chords_list if(ele in close_df['Chords'][iSong].split(','))]) / len(close_df['Chords'][iSong].split(','))  )
        else:
            nSameChords.append(0)
            propSameChords.append(0)
            
    maxOverlap = np.argmax(propSameChords)

    hard_rec = close_df.iloc[maxOverlap]    

    return easy_rec, medium_rec, hard_rec


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
    known_df = dbCheck_track(track)
    pl_indb  = processPlaylist(playlist)

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
