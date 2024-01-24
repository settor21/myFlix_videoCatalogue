import io
from flask import Flask, redirect, render_template, request, session, jsonify, url_for, send_from_directory, send_file
from google.cloud import storage
from datetime import datetime
from pymongo import MongoClient
from urllib.parse import quote_plus
# Initialize MongoDB client
username = 'amedikusettor'
password = 'Praisehim69%'

# Escape the username and password
escaped_username = quote_plus(username)
escaped_password = quote_plus(password)

# Construct the MongoDB URI with escaped username and password
mongo_uri = f'mongodb://{escaped_username}:{escaped_password}@35.239.170.49:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.1.1'

# Create the MongoClient
mongo_client = MongoClient(mongo_uri)

db = mongo_client['userInput']  # Change to the new database name
selected_videos_collection = db['selectedVideos']

app = Flask(__name__)

# Google Cloud Storage Configuration
BUCKET_NAME = 'my-flix-videos'
BUCKET_FOLDER = 'ad-tier'
AD_TIER_FOLDER = 'ad-tier'

PAID_TIER_FOLDER = 'paid-tier'
CURRENT_FOLDER = None
# Define a secret key for session management
app.secret_key = 'your_secret_key'

# Check if the user is authenticated before processing each request


@app.before_request
def check_authentication():
    if request.endpoint and 'videoCatalogue' in request.endpoint:
        # Check if the user is authenticated
        if 'user_id' not in session:
            # home page from userAccess in docker container
            return redirect("http://127.0.0.1:5000")


@app.route('/logout')
def logout():
    # home page from userAccess in docker container
    return redirect("http://127.0.0.1:5000")


@app.route('/renew')
def renew_subscription():
    return render_template('renewSubscription.html')


@app.route('/ad-tier')
def ad_tier():
    global CURRENT_FOLDER
    # List all objects (videos) in the 'ad-tier' Google Cloud Storage bucket folder
    ad_tier_videos = list_videos(AD_TIER_FOLDER)

    # Each row will contain 4 videos
    rows_of_videos = [ad_tier_videos[i:i + 4]
                      for i in range(1, len(ad_tier_videos), 4)]

    CURRENT_FOLDER = 'ad-tier'

    return render_template('home_ads.html', rows_of_videos=rows_of_videos)


@app.route('/paid-tier')
def paid_tier():
    global CURRENT_FOLDER
    paid_tier_videos = list_videos(PAID_TIER_FOLDER)
    # Each row will contain 4 videos
    paid_videos = [paid_tier_videos[i:i + 4]
                   for i in range(1, len(paid_tier_videos), 4)]
    all_videos = paid_videos
    CURRENT_FOLDER = 'paid-tier'

    return render_template('home_paid.html', rows_of_videos=all_videos)


@app.route('/api/videos')
def get_videos_api():
    # List all objects (videos) in the specified Google Cloud Storage bucket folder
    videos = list_videos()

    return jsonify({'videos': videos})


def list_videos(folder):
    # Initialize Google Cloud Storage client
    client = storage.Client()

    # Get the bucket and list all objects (videos) in the specified folder
    bucket = client.get_bucket(BUCKET_NAME)
    blobs = bucket.list_blobs(prefix=folder)

    # Extract video names from blob names (remove folder prefix) and include the index
    videos = [{'name': blob.name.split('/')[-1], 'index': i + 1}
              for i, blob in enumerate(blobs)]

    return videos


@app.route('/videos/<path:video_name>')
def get_video(video_name):
    # Serve the videos from the Google Cloud Storage bucket
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)

    # Specify the folder in the bucket where the videos are stored
    folder = CURRENT_FOLDER

    # Build the blob path
    blob_path = f'{folder}/{video_name}'

    # Download the video file
    video_blob = bucket.blob(blob_path)
    video_data = video_blob.download_as_string()

    # Create a BytesIO object to serve the video data
    video_io = io.BytesIO(video_data)

    return send_file(video_io, mimetype='video/mp4', as_attachment=True, download_name=video_name)


@app.route('/log-video', methods=['POST'])
def log_video():
    if request.method == 'POST':
        data = request.get_json()
        video_name = data.get('videoName')
        timestamp = datetime.utcnow()

        # Log the selected video in MongoDB
        selected_videos_collection.insert_one({
            'video_name': video_name,
            'timestamp': timestamp
        })

        return jsonify({'message': 'Video logged successfully'})
    



if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5001)
