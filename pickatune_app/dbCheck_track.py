def dbCheck_track(track, song_info):
    import pandas as pd

    known_song   = str(track).split(', ')[1]
    artist = str(track).split(', ')[0]     

    dblist    = song_info['Song'].tolist()   

    if known_song.replace(' ', '-').lower() in dblist:
        known_ix = dblist.index(known_song.replace(' ', '-').lower())

        # get chords and features for the known song
        known_df = pd.DataFrame(song_info.loc[known_ix]).transpose()
        # known_df['isAdv'] = isAdv.loc[knownSong_ix][0]
        # known_df['nChords'] = allFeatures['n_unique_chords'].loc[knownSong_ix]

    known_df.drop('index', axis=1, inplace=True)
    known_df.reset_index(drop=True, inplace=True)
    
    return known_df, known_ix