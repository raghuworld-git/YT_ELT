import requests
import os
from dotenv import load_dotenv


load_dotenv(dotenv_path="./.env")
API_KEY = os.getenv("API_KEY")

CHANNEL_HANDLE = "MrBeast"
maxResults = 50

def get_playlist_id()-> str:
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

        response = requests.get(url=url)
        data = response.json()
        channel_items = data["items"][0]
        channel_playlist_id = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]
        return channel_playlist_id

    except requests.exceptions.RequestException as e:
        raise e
    

    
def get_video_ids(playlist_id:str):

    video_ids = []
    pageToken=None
    baseURL = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlist_id}&key={API_KEY}"

    try:
        while True:
            url = baseURL
            if pageToken:
                url += f"&pageToken={pageToken}"
            response = requests.get(url=url)
            data = response.json()

            for item in data.get("items",[]):
               id =  item["contentDetails"]["videoId"]
               video_ids.append(id)

            pageToken = data.get("nextPageToken")
            if not pageToken:
                break
        return video_ids

    except requests.exceptions.RequestException as e:
        raise e

if __name__ == "__main__":
    playlist_id = get_playlist_id()
    print(get_video_ids(playlist_id))
