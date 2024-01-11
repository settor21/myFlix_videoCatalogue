import io
from flask import Flask, redirect, render_template, request, session, jsonify, url_for, send_from_directory, send_file
from google.cloud import storage

app = Flask(__name__)

# Google Cloud Storage Configuration
BUCKET_NAME = 'my-flix-videos'
BUCKET_FOLDER = 'ad-tier'

# Define a secret key for session management
app.secret_key = 'your_secret_key'

# Check if the user is authenticated before processing each request


@app.before_request
def check_authentication():
    if request.endpoint and 'videoCatalogue' in request.endpoint:
        # Check if the user is authenticated
        if 'user_id' not in session:
            return redirect(url_for('login'))


@app.route('/home')
def home():
    # List all objects (videos) in the specified Google Cloud Storage bucket folder
    videos = list_videos()

    # Each row will contain 4 videos
    rows_of_videos = [videos[i:i+4] for i in range(0, len(videos), 4)]

    return render_template('home.html', rows_of_videos=rows_of_videos)


@app.route('/api/videos')
def get_videos_api():
    # List all objects (videos) in the specified Google Cloud Storage bucket folder
    videos = list_videos()

    return jsonify({'videos': videos})


def list_videos():
    # Initialize Google Cloud Storage client
    client = storage.Client()

    # Get the bucket and list all objects (videos) in the specified folder
    bucket = client.get_bucket(BUCKET_NAME)
    blobs = bucket.list_blobs(prefix=BUCKET_FOLDER)

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
if __name__ == '__main__':
    app.run(debug=True,port=5001)
