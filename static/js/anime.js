function setEpisodeType(type) {
    const currentEpisode = {{ episode }};
    localStorage.setItem('{{ anime_name }}_episode_type', type); // Store episode type (sub/dub) in local storage
    window.location.href = `/anime/{{ anime_name }}?episode=${currentEpisode}&type=${type}`;
}

function setEpisodeStart(start) {
    const episodeType = localStorage.getItem('{{ anime_name }}_episode_type') || '{{ episode_type }}'; // Retrieve episode type (sub/dub) from local storage
    window.location.href = `/anime/{{ anime_name }}?episode=${start}&type=${episodeType}`;
}

document.getElementById('anime-iframe').addEventListener('load', function() {
    localStorage.setItem('{{ anime_name }}_last_episode', {{ episode }});
});

document.getElementById('theme-toggle').addEventListener('click', function () {
    document.body.classList.toggle('dark-theme');
    const isDark = document.body.classList.contains('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

document.addEventListener('DOMContentLoaded', function () {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }

    // Retrieve and apply the episode type (sub/dub) from local storage if it differs from the current type
    const savedEpisodeType = localStorage.getItem('{{ anime_name }}_episode_type');
    const currentType = new URLSearchParams(window.location.search).get('type');

    if (savedEpisodeType && savedEpisodeType !== currentType) {
        const currentEpisode = new URLSearchParams(window.location.search).get('episode') || {{ episode }};
        window.location.href = `/anime/{{ anime_name }}?episode=${currentEpisode}&type=${savedEpisodeType}`;
    }
});