import io
from flask import Flask, redirect, render_template, request, session, jsonify, url_for, send_from_directory, send_file
from google.cloud import storage
from datetime import datetime
from pymongo import MongoClient

# Initialize MongoDB client
mongo_client = MongoClient(
    'mongodb+srv://amedikusettor:Skaq0084@myflixproject.soxjrzv.mongodb.net/?retryWrites=true&w=majority')
db = mongo_client['recommendationInput']  # Change to the new database name
selected_videos_collection = db['selectedVideos']

app = Flask(__name__)

# Google Cloud Storage Configuration
BUCKET_NAME = 'my-flix-videos'
BUCKET_FOLDER = 'ad-tier'
AD_TIER_FOLDER = 'ad-tier'

PAID_TIER_FOLDER = 'paid-tier'

# Define a secret key for session management
app.secret_key = 'your_secret_key'

# Check if the user is authenticated before processing each request
@app.before_request
def check_authentication():
    if request.endpoint and 'videoCatalogue' in request.endpoint:
        # Check if the user is authenticated
        if 'user_id' not in session:
            return redirect(url_for('login'))


@app.route('/ad-tier')
def ad_tier():
    # List all objects (videos) in the 'ad-tier' Google Cloud Storage bucket folder
    ad_tier_videos = list_videos(AD_TIER_FOLDER)

    # Each row will contain 4 videos
    rows_of_videos = [ad_tier_videos[i:i + 4]
                      for i in range(0, len(ad_tier_videos), 4)]

    return render_template('home_ads.html', rows_of_videos=rows_of_videos)


@app.route('/paid-tier')
def paid_tier():
    # List all objects (videos) in both 'ad-tier' and 'paid-tier' Google Cloud Storage bucket folders
    ad_tier_videos = list_videos(AD_TIER_FOLDER)
    paid_tier_videos = list_videos(PAID_TIER_FOLDER)

    # Combine the videos from both tiers
    all_videos = ad_tier_videos + paid_tier_videos

    # Each row will contain 4 videos
    rows_of_videos = [all_videos[i:i + 4]
                      for i in range(0, len(all_videos), 4)]

    return render_template('home_paid.html', rows_of_videos=rows_of_videos)


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

    # Extract video names from blob names (remove folder prefix)
    videos = [blob.name.split('/')[-1] for blob in blobs]

    return videos

@app.route('/videos/<path:video_name>')
def get_video(video_name):
    # Serve the videos from the Google Cloud Storage bucket
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)

    # Specify the folder in the bucket where the videos are stored
    folder = BUCKET_FOLDER

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
    app.run(host = "0.0.0.0",debug=True,port=5001)
