# fix_plex_collections
A script to fix PLEX collections if they go crazy.

I accidentally had my PLEX set to build auto-collections.  While some of them were actually cool to have, 99% of them were single movie collections which was completely pointless.

This is a quick script to use plexapi and python to remove collections based on your criteria (TV or Movies)

1) Install plexapi for pip
2) Set PLEX_URL as an env or in the top of the script to reflect your server location (i.e. http://192.168.1.5:32400)
3) Set PLEX_TOKEN as an env or in the top of the script based on the retrieved token
       instructions: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

Other Options in the script:
MIN_ITEMS = X   #Set to the minimum number of items a collection should have to be valid (kept)
DRY_RUN = True  #Verify the potential changes to Plex before making them
LIBRARY_TYPES = ["movie"]. ["show"]. or ["movie", "show"].  Alone will do Movie or TV collections, together does both.

Then just run python3 fix_collections.py and watch your Plex library magically be cleaned from rogue collections.
