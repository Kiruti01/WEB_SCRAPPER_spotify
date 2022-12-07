from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# CLIENT_ID = "92700427a3ed41a6943c156d45c5c3d0"
# CLIENT_SECRET = "a684026048eb4886a2edb3e5edc80c26"
#
# date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
#
# response = requests.get("https://www.billboard.com/charts/hot-100/" + date)
#
# soup = BeautifulSoup(response.text, 'html.parser')
# song_names_spans = soup.find_all("span", class_="chart-element__information__song")
# song_names = [song.getText() for song in song_names_spans]

# sp = spotipy.Spotify(
#     auth_manager=SpotifyOAuth(
#         scope="playlist-modify-private",
#         redirect_uri="http://example.com/callback",
#         client_id=CLIENT_ID,
#         client_secret=CLIENT_SECRET,
#         show_dialog=True,
#         cache_path="token.txt"
#     )
# )
# user_id = sp.current_user()["id"]

URL_billboard = "https://www.billboard.com/charts/hot-100/"

date = input("What year do you want to travel to? Type the date in this format, YYYY-MM-DD: ")
year = date[:4]

response = requests.get(f"{URL_billboard}{date}/")
webpage = response.text

soup = BeautifulSoup(webpage, "html.parser")

scraped = [song.getText().strip("\n") for song in soup.find_all(name="h3", class_="c-title", id="title-of-a-story")][5:]

scraped_art = [artist.getText().strip("\n") for artist in soup.find_all(name="span", class_="c-label")]

song_names = [name.replace("'", "").replace("!", "") for name in scraped
              if 'Songwriter(s):' not in name
              if 'Producer(s):' not in name
              if 'Imprint/Promotion Label:' not in name
              if 'Additional Awards' not in name
              ][:100]

artist_names = [artist.split(" Featuring")[0].split(" Duet")[0].replace("Ke$ha", "Kesha") for artist in scraped_art
                if not artist.isnumeric()
                if artist != "-"
                if artist != "NEW"
                if 'ENTRY' not in artist
                ]

spotify_client_id = "92700427a3ed41a6943c156d45c5c3d0"
spotify_client_secret = "a684026048eb4886a2edb3e5edc80c26"
redirect = "http://example.com"


spotify_auth = spotipy.oauth2.SpotifyOAuth(client_id=spotify_client_id,
                                           client_secret=spotify_client_secret,
                                           redirect_uri=redirect,
                                           scope="playlist-modify-private",
                                           cache_path="token.txt")

# spotify.get_access_token()

sp = spotipy.Spotify(oauth_manager=spotify_auth)

user_name = sp.current_user()["display_name"]
user_id = sp.current_user()["id"]

song_urls = []
for song, artist in zip(song_names, artist_names):
    items = sp.search(q=f"track: {song} artist: {artist}", type="track")["tracks"]["items"]
    if len(items) > 0:
        song_urls.append(items[0]["uri"])

playlist_id = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)["id"]

sp.playlist_add_items(playlist_id=playlist_id, items=song_urls)
