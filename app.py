from flask import Flask, render_template, request, redirect, url_for, make_response, send_from_directory
import requests

app = Flask(__name__)


def format_anime_name(name):
    return name.lower().replace(' ', '-')


@app.route('/')
def index():
    episode = int(request.args.get('episode', '1'))
    episode_type = request.args.get('type', 'sub')
    embed_url = f"https://2anime.xyz/embed/one-piece{'-dub' if episode_type == 'dub' else ''}-episode-{episode}"
    response = make_response(render_template('index.html', embed_url=embed_url, episode=episode, episode_start=(
        episode - 1) // 100 * 100 + 1, episode_type=episode_type))
    response.set_cookie('last_episode', str(episode),
                        max_age=30*24*60*60)  # Save for 30 days
    return response


@app.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        formatted_name = format_anime_name(query)
        return redirect(url_for('details', name=formatted_name))
    return redirect(url_for('index'))


@app.route('/details/<name>')
def details(name):
    # Fetch anime details from Kitsu API
    search_url = f"https://kitsu.io/api/edge/anime?filter[text]={name}"
    search_response = requests.get(search_url)
    search_data = search_response.json()

    if search_data['data']:
        anime_data = search_data['data'][0]['attributes']
        total_episodes = anime_data.get('episodeCount')
        synopsis = anime_data.get('synopsis', 'No synopsis available.')
        start_date = anime_data.get('startDate', 'No start date available.')
        status = anime_data.get('status', 'No status available.')
        rating = anime_data.get('averageRating', 'No rating available.')
        poster_image = anime_data.get('posterImage', {}).get('original', '')

        if total_episodes is None:
            total_episodes = "Total episodes not specified."

        anime_details = {
            'title': name.replace('-', ' ').title(),
            'total_episodes': total_episodes,
            'synopsis': synopsis,
            'start_date': start_date,
            'status': status,
            'rating': rating,
            'poster_image': poster_image
        }

        return render_template('details.html', anime=anime_details)
    else:
        return "Anime not found."


@app.route('/anime/<name>')
def anime(name):
    episode = int(request.args.get(
        'episode', request.cookies.get(f'{name}_last_episode', '1')))
    episode_type = request.args.get('type', 'sub')
    episode_start = (episode - 1) // 100 * 100 + 1
    embed_url = f"https://2anime.xyz/embed/{name}{'-dub' if episode_type == 'dub' else ''}-episode-{episode}"
    response = make_response(render_template('anime.html', embed_url=embed_url, anime_name=name, episode=episode, episode_start=episode_start, episode_type=episode_type))
    response.set_cookie(f'{name}_last_episode', str(episode), max_age=30*24*60*60)  # Save for 30 days
    return response

# Route to serve the favicon


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')


if __name__ == '__main__':
    app.run(debug=True)
