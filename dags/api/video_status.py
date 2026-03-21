import requests
from datetime import date
# import os
# from dotenv import load_dotenv
# load_dotenv(dotenv_path="./.env")
import json
from airflow.decorators import task
from airflow.models import Variable



API_KEY =Variable.get("API_KEY")

CHANNEL_HANDLE = Variable.get("CHANNEL_HANDLE")
maxResults = 50

@task
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
    

@task   
def get_video_ids(playlist_id:str)-> list:

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

@task
def extract_video_details(video_ids)-> list:
    extracted_data = []
    def batch_list(video_list,batch_size):
        for video_id in range(0,len(video_list),batch_size):
            yield video_list[video_id:video_id+batch_size]    

    try : 
        for batch in batch_list(video_ids,maxResults):
            video_ids_str = ",".join(batch)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=snippet&part=contentDetails&part=statistics&id={video_ids_str}&key={API_KEY}"
            response = requests.get(url=url)
            data = response.json()

            for item in data.get("items",[]):
                video_id = item["id"]
                title = item["snippet"]["title"]
                published_at = item["snippet"]["publishedAt"]
                view_count = item["statistics"].get("viewCount",0)
                like_count = item["statistics"].get("likeCount",0)
                comment_count = item["statistics"].get("commentCount",0)

                extracted_data.append({
                    "video_id": video_id,
                    "title": title,
                    "published_at": published_at,
                    "view_count": view_count,
                    "like_count": like_count,
                    "comment_count": comment_count
                })

        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e
@task
def save_to_json(extracted_video_details):
    file_path = f"./data/YT_data_{date.today()}.json"
    with open(file=file_path,mode='w',encoding="utf-8") as json_outfile:
        json.dump(extracted_video_details,json_outfile,indent=4,ensure_ascii=False)

if __name__ == "__main__":
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    save_to_json(extract_video_details(video_ids))
