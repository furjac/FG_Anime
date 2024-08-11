from flask import Flask, render_template, request, redirect, url_for, make_response, send_from_directory
import requests

app = Flask(__name__)


def format_anime_name(name):
    if '  ' in name:
        name = ' '.join(name.split())
    elif name.endswith(" "):
        name = name.rstrip()
    name = name.lstrip()
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


def fetch_anime_details_from_anilist(name):
    # Define the GraphQL query
    query = '''
    query ($search: String) {
      Media(search: $search, type: ANIME) {
        id
        title {
          romaji
          english
          native
        }
        description
        episodes
        startDate {
          year
          month
          day
        }
        status
        averageScore
        coverImage {
          large
        }
      }
    }
    '''

    # Define the variables for the query
    variables = {
        'search': name
    }

    # Define the endpoint and send the request
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    
    if response.status_code != 200:
        return None

    data = response.json()

    # Extract the data
    media = data.get('data', {}).get('Media', {})
    if media:
        return {
            'title_romaji': media.get('title', {}).get('romaji', 'No title available.'),
            'title_english': media.get('title', {}).get('english', 'No title available.'),
            'title_native': media.get('title', {}).get('native', 'No title available.'),
            'description': media.get('description', 'No description available.'),
            'episodes': media.get('episodes', 'Not specified.'),
            'start_date': f"{media.get('startDate', {}).get('year', 'Unknown Year')}-{media.get('startDate', {}).get('month', '00')}-{media.get('startDate', {}).get('day', '00')}",
            'status': media.get('status', 'No status available.'),
            'average_score': media.get('averageScore', 'No score available.'),
            'cover_image': media.get('coverImage', {}).get('large', 'No cover image available.')
        }
    else:
        return None


@app.route('/details/<name>')
def details(name):
    anime_details = fetch_anime_details_from_anilist(name)
    
    if anime_details:
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


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')


if __name__ == '__main__':
    app.run()
