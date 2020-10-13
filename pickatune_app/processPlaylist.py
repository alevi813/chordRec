def processPlaylist(pl_link, dblist):
    import pandas as pd
    import spotipy
    
    spotifyCred = pd.read_csv('spotifyCred.csv')
    from spotipy.oauth2 import SpotifyClientCredentials
    client_credentials_manager = SpotifyClientCredentials(client_id= spotifyCred['0'][0],
                                                         client_secret= spotifyCred['0'][1])
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

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