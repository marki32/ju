from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
import re

app = Flask(__name__)

if not os.path.exists('downloads'):
    os.makedirs('downloads')

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)

def download_audio(url):
    output_template = os.path.join('downloads', '%(title)s.%(ext)s')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'prefer_ffmpeg': True,
        'keepvideo': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'video')
        sanitized_title = sanitize_filename(title)
        filename = f"{sanitized_title}.mp3"
        return {
            'status': 'success',
            'title': title,
            'filename': filename
        }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    try:
        url = request.form.get('url')
        if not url:
            return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

        result = download_audio(url)
        return jsonify({
            'status': 'success',
            'title': result['title'],
            'filename': result['filename']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/get-file/<filename>')
def get_file(filename):
    file_path = os.path.join('downloads', filename)
    if not os.path.exists(file_path):
        return "File not found", 404
        
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True)
