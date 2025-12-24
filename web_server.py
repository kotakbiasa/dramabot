# Flask Web Server for Drama Streaming
from flask import Flask, render_template, jsonify, redirect, request
import asyncio
from drama import api, config

app = Flask(__name__)

# Helper function to run async code in Flask
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route('/')
def index():
    """Homepage with trending dramas"""
    try:
        dramas = run_async(api.get_trending(limit=20))
        return render_template('index.html', dramas=dramas)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/watch/<book_id>/<int:episode_num>')
def watch(book_id, episode_num):
    """Player page for specific episode"""
    try:
        # Get episode and drama details
        episode = run_async(api.get_episode(book_id, episode_num))
        drama = run_async(api.get_drama_detail(book_id))
        
        if not episode:
            return "Episode not found", 404
        
        return render_template(
            'player.html',
            drama=drama,
            episode=episode,
            book_id=book_id,
            episode_num=episode_num
        )
    except Exception as e:
        return f"Error loading episode: {str(e)}", 500

@app.route('/api/episode/<book_id>/<int:episode_num>')
def api_episode(book_id, episode_num):
    """API endpoint to get episode data"""
    try:
        episode = run_async(api.get_episode(book_id, episode_num))
        drama = run_async(api.get_drama_detail(book_id))
        
        if not episode:
            return jsonify({'error': 'Episode not found'}), 404
        
        # Prepare video URLs with qualities
        video_urls = []
        if episode.urls:
            for url_data in episode.urls:
                video_urls.append({
                    'quality': url_data.get('quality', 720),
                    'url': url_data.get('url', '')
                })
        
        return jsonify({
            'drama_title': drama.title if drama else f'Drama {book_id}',
            'episode_title': episode.title,
            'episode_num': episode_num,
            'duration': episode.duration,
            'thumbnail': drama.cover_url if drama and drama.cover_url else episode.thumbnail,
            'video_urls': video_urls,
            'video_url': episode.video_url  # Default URL
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search')
def search():
    """Search dramas"""
    query = request.args.get('q', '')
    if not query:
        return redirect('/')
    
    try:
        dramas = run_async(api.search(query, limit=20))
        return render_template('search.html', dramas=dramas, query=query)
    except Exception as e:
        return f"Error: {str(e)}", 500


