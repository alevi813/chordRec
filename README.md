# PICK-a-tune

There are many people out there who own guitars, but barely play them. Learning guitar is difficult, and can be especially frustrating if you attempt to learn songs that are just too advanced. 
To help solve this problem, Pick-a-Tune classifies songs by their difficulty and suggests songs to users based on their current skill level and musical taste. The goal is to deliver recommendations based on scaffolded difficulty, so that using the app over time would provide a personalized curriculum for learning guitar. 

## Initial scraping and ML pipeline
1. ug_scrapeLinks --- scapes the web for 20 pages of links in three difficulty categories: novice, intermediate and advanced
2. ug_scrapeChords --- scrapes each link for chord information 
3. add_to_db --- adds basic song info, chord information, and spotify song features to a sqlite database
4. train_lr_models --- some pre-processing, plus fitting, testing, and saving various classifiers to be used later

## App pipeline
Pick-a-Tune takes two inputs: a song that the user knows, and a playlist of songs that the user enjoys. It returns songs two songs from the playlist: an easy recommendation, and a slightly more challenging recommendation

1. dbCheck_track --- check if the "known song" is in the database
2. processPlaylist --- read playlist info using the Spotify API, and check for those songs in the database
3. classifyDifficulty --- classify difficulty of the known song and all songs in the playlist. Either read this from the database, or calculate it on the fly using the pickled model.
4. chordSimilarity --- take a look at all songs with the same difficulty label as the "known song." Rate their similarity to the known song using the proportion of overlapping chords, and Euclidean distance between the top 3 features. 
