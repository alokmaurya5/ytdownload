from flask import Flask, render_template, request, send_file, Response
from pytube import YouTube
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    link = request.form['link']
    try:
        yt = YouTube(link)
        video_qualities = yt.streams.filter(progressive=True).order_by('resolution').desc().all()
        quality_options = [f"{stream.resolution} - {stream.filesize_mb:.2f} MB" for stream in video_qualities]
        return render_template('download.html', quality_options=quality_options, link=link)
    except Exception as e:
        return render_template('error.html', error=str(e))
    
@app.route('/download/<resolution>', methods=['POST'])
def download_video(resolution):
    link = request.form['link']
    yt = YouTube(link)
    stream = yt.streams.filter(progressive=True, resolution=resolution).first()

    if not stream:
        # No stream found for the requested resolution
        return render_template('error.html', error=f"No stream found for resolution {resolution}")

    video_path = stream.download()
    video_name = os.path.basename(video_path)

    # Check if the file exists and is a file
    if not os.path.isfile(video_path):
        abort(404)

    # Send the file with the appropriate headers
    with open(video_path, 'rb') as f:
        data = f.read()
    headers = {
        'Content-Disposition': f'attachment; filename="{video_name}"',
        'Content-Type': 'video/mp4'
    }
    return Response(data, headers=headers)


if __name__ == '__main__':
    app.run(debug=True)
