from airflow import DAG
import pendulum
from datetime import datetime,timedelta
from api.video_status import get_video_ids,extract_video_details,save_to_json,get_playlist_id

# Define local timezone
local_tz = pendulum.timezone('Asia/Kolkata')

# Default Args
default_args = {
    "owner":"dataengineers",
    "depends_on_past":False,
    "email_on_failures":False,
    "email_on_retry":False,
    "email":"raghuworld1992@gmail.com",
    "max_active_runs":1,
    "dagrun_timeout":timedelta(hours=1),
    "start_date":datetime(2025,1,1,tzinfo=local_tz)
}

with DAG (
    dag_id ='produce_json',
    default_args = default_args,
    description="DAG to produce JSON file with raw data",
    schedule = '0 14 * * *' ,
    catchup=False  
) as dag:
    
    # Define tasks
    playlist_id = get_playlist_id()
    videos_ids = get_video_ids(playlist_id)
    extract_data = extract_video_details(videos_ids)
    save_to_json_task = save_to_json(extract_data)

    # Define dependencies
    playlist_id >> videos_ids >> extract_data >> save_to_json_task
