def chordSimilarity(known_df, input_df):
    import numpy as np

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