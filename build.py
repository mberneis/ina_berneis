from html import escape
import json
import os
import re
import time
import unicodedata
from urllib.parse import quote

def nl2br(text):
    """Convert newlines to HTML <br> tags"""
    return text.replace('\n', '<br>')

def slugify(text):
    """Convert text to URL-friendly slug"""
    # Normalize unicode characters (e.g., ö -> o)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Convert to lowercase and replace spaces/special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text

def load_photos():
    """Load all photo entries from photos.json"""
    with open('data/photos.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_movies():
    """Load all movie entries from movies.json"""
    with open('data/movies.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_hollywood():
    """Load hollywood.json data"""
    with open('data/hollywood.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_subsite(slug):
    """Load data/<slug>.json for a standalone subsite"""
    with open(f'data/{slug}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_nav_items(lang, current_page, photos):
    """Generate navigation items from photos array (sorted alphabetically)"""
    nav_items = []
    sorted_photos = sorted(photos, key=lambda x: x[f'title_{lang}'].lower())
    for item in sorted_photos:
        page_name = slugify(item['title_en'])
        title = item[f'title_{lang}']
        active_class = 'font-semibold bg-gray-200 dark:bg-gray-800 dark:text-gray-100' if current_page == page_name else ''
        nav_items.append(f'<li><a href="{page_name}.html" class="py-0 text-sm ml-4 nav-link {active_class}">{title}</a></li>')

    return '\n                        '.join(nav_items)

def get_movie_nav_items(lang, current_page, movies):
    """Generate navigation items from movies array (sorted alphabetically)"""
    nav_items = []
    sorted_movies = sorted(movies, key=lambda x: x[f'title_{lang}'].lower())
    for item in sorted_movies:
        page_name = 'movie-' + slugify(item['title_en'])
        title = item[f'title_{lang}']
        active_class = 'font-semibold bg-gray-200 dark:bg-gray-800 dark:text-gray-100' if current_page == page_name else ''
        nav_items.append(f'<li><a href="{page_name}.html" class="py-0 text-sm ml-4 nav-link {active_class}">{title}</a></li>')

    return '\n                        '.join(nav_items)

def create_page(lang, page_name, data, template, photos, movies, css_version, hollywood=None):
    """Generate HTML page from data"""
    labels = {
        'en': {
            'life': 'Biography',
            'career': 'Career',
            'hollywood': 'Hollywood',
            'photography': 'Photography',
            'movies': 'Movies',
            'photographer': 'Photographer',
            'photolabel': 'Ina in her 20\'s in Berlin'
        },
        'de': {
            'life': 'Biographie',
            'career': 'Karriere',
            'hollywood': 'Hollywood',
            'photography': 'Fotografie',
            'movies': 'Filme',
            'photographer': 'Fotografin',
            'photolabel': 'Ina in ihren 20\'er Jahren in Berlin'
        }
    }

    # Create life page with timeline
    if page_name == 'life':
        content = '<div class="flex flex-col-reverse mb-8 md:flex-row md:items-start md:gap-8">\n'
        content += '    <div class="flex-1">\n'
        content += f'        <h1 class="mb-6 text-3xl font-bold text-gray-900 md:text-5xl dark:text-gray-100">{data[f"title_{lang}"]}</h1>\n'
        content += f'        <p class="text-lg leading-relaxed text-gray-700 dark:text-gray-300">{nl2br(data[f"description_{lang}"])}</p>\n'
        content += '    </div>\n'
        content += '    <div class="w-3/4 mb-6 sm:w-1/2 md:w-1/3 md:mb-0 shrink-0">\n'
        content += '        <img src="../assets/images/Ina.png" alt="Ina Berneis" class="w-full h-auto rounded-lg shadow-lg">\n'
        content += f'        <div class="mt-1 text-xs text-center">{labels[lang]["photolabel"]}</div>\n'
        content += '    </div>\n'
        content += '</div>\n'
        content += '<div class="space-y-0">\n'
        for event in data["events"]:
            content += '    <div class="timeline-item">\n'
            content += f'        <h2 class="mb-3 text-xl font-bold text-gray-900 md:text-2xl dark:text-gray-100">{event["date"]}</h2>\n'
            content += f'        <p class="mb-4 leading-relaxed text-gray-700 dark:text-gray-300">{nl2br(event[f"description_{lang}"])}</p>\n'
            if "photo" in event:
                content += '        <div class="w-32 md:w-48 photo-container">\n'
                content += f'            <img src="../{event["photo"]}" alt="Photo from {event["date"]}" class="w-full h-auto">\n'
                content += '        </div>\n'
            content += '    </div>\n'
        content += '</div>'

    # Create career page
    elif page_name == 'career':
        content = f'<h1 class="mb-6 text-3xl font-bold text-gray-900 md:text-5xl dark:text-gray-100">{data[f"title_{lang}"]}</h1>\n'
        content += '<div class="prose prose-lg dark:prose-invert max-w-none">\n'
        # Iterate over all key/value pairs in content section
        for key, value in data[f"content_{lang}"].items():
            # Use the key as the header (capitalize first letter of each word)
            header = key.replace('_', ' ').title()
            content += f'    <h2 class="mt-8 mb-4 text-2xl font-bold text-gray-900 md:text-3xl dark:text-gray-100">{header}</h2>\n'
            content += f'    <p class="mb-8 leading-relaxed text-gray-700 dark:text-gray-300">{nl2br(value)}</p>\n'
        content += '</div>'

    # Create movie pages
    elif page_name.startswith('movie-'):
        content = '<div class="flex items-center gap-3 mb-6">\n'
        content += f'    <h1 class="text-3xl font-bold text-gray-900 md:text-5xl dark:text-gray-100">{data[f"title_{lang}"]}</h1>\n'
        if "link" in data and data["link"]:
            content += f'    <a href="{data["link"]}" target="_blank" rel="noopener noreferrer" class="text-gray-500 transition-colors hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200" title="More information">\n'
            content += '        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>\n'
            content += '    </a>\n'
        content += '</div>\n'
        if "imdb" in data and data["imdb"]:
            content += f'<a href="{data["imdb"]}" target="_blank" rel="noopener noreferrer" class="inline-block mb-4">\n'
            content += '    <img src="../assets/images/imdb.svg" alt="IMDB" class="h-8">\n'
            content += '</a>\n'
        else:
            content += '<div class="mb-12"></div>\n'
        content += f'<p class="mb-6 text-lg leading-relaxed text-gray-700 dark:text-gray-300">{nl2br(data[f"description_{lang}"])}</p>\n'
        content += '<div class="grid grid-cols-1 gap-8 lg:grid-cols-2">\n'
        for photo in data["photos"]:
            content += '    <div class="space-y-4">\n'
            content += '        <div class="photo-container">\n'
            content += f'            <img src="../{photo["photo"]}" alt="{data[f"title_{lang}"]}" class="w-full h-auto">\n'
            content += '        </div>\n'
            if f"description_{lang}" in photo:
                content += f'        <p class="text-sm italic text-gray-600 dark:text-gray-400">{nl2br(photo[f"description_{lang}"])}</p>\n'
            content += '    </div>\n'
        content += '</div>'

    # Create photography pages
    else:
        content = '<div class="flex items-center gap-3 mb-6">\n'
        content += f'    <h1 class="text-3xl font-bold text-gray-900 md:text-5xl dark:text-gray-100">{data[f"title_{lang}"]}</h1>\n'
        if "link" in data and data["link"]:
            content += f'    <a href="{data["link"]}" target="_blank" rel="noopener noreferrer" class="text-gray-500 transition-colors hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200" title="More information">\n'
            content += '        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>\n'
            content += '    </a>\n'
        content += '</div>\n'
        content += f'<p class="mb-12 text-lg leading-relaxed text-gray-700 dark:text-gray-300">{nl2br(data[f"description_{lang}"])}</p>\n'
        if len(data["photos"]) == 1:
            # Single image: center it under the description
            photo = data["photos"][0]
            content += '<div class="flex justify-center">\n'
            content += '    <div class="space-y-4 w-full lg:w-1/2">\n'
            content += '        <div class="photo-container">\n'
            content += f'            <img src="../{photo["photo"]}" alt="{data[f"title_{lang}"]}" class="w-full h-auto">\n'
            content += '        </div>\n'
            if f"description_{lang}" in photo:
                content += f'        <p class="text-sm italic text-gray-600 dark:text-gray-400">{nl2br(photo[f"description_{lang}"])}</p>\n'
            content += '    </div>\n'
            content += '</div>'
        else:
            # Multiple images: use grid layout
            content += '<div class="grid grid-cols-1 gap-8 lg:grid-cols-2">\n'
            for photo in data["photos"]:
                content += '    <div class="space-y-4">\n'
                content += '        <div class="photo-container">\n'
                content += f'            <img src="../{photo["photo"]}" alt="{data[f"title_{lang}"]}" class="w-full h-auto">\n'
                content += '        </div>\n'
                if f"description_{lang}" in photo:
                    content += f'        <p class="text-sm italic text-gray-600 dark:text-gray-400">{nl2br(photo[f"description_{lang}"])}</p>\n'
                content += '    </div>\n'
            content += '</div>'

    # Navigation items
    nav_items = get_nav_items(lang, page_name, photos)
    movie_nav_items = get_movie_nav_items(lang, page_name, movies)

    # Active states
    life_active = 'font-semibold bg-gray-200 dark:bg-gray-800 dark:text-gray-100' if page_name == 'life' else ''
    career_active = 'font-semibold bg-gray-200 dark:bg-gray-800 dark:text-gray-100' if page_name == 'career' else ''
    hollywood_active = 'font-semibold bg-gray-200 dark:bg-gray-800 dark:text-gray-100' if page_name == 'hollywood' else ''
    lang_en_active = 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900' if lang == 'en' else 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800'
    lang_de_active = 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900' if lang == 'de' else 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800'

    with open(f'public/{lang}/{page_name}.html', 'w', encoding='utf-8') as f:
        f.write(template.format(
            lang=lang,
            title=data[f"title_{lang}"],
            content=content,
            page_name=page_name,
            css_path="../assets/css/",
            css_version=css_version,
            nav_items=nav_items,
            movie_nav_items=movie_nav_items,
            life_active=life_active,
            career_active=career_active,
            hollywood_active=hollywood_active,
            lang_en_active=lang_en_active,
            lang_de_active=lang_de_active,
            life_label=labels[lang]['life'],
            career_label=labels[lang]['career'],
            hollywood_label=labels[lang]['hollywood'],
            photography_label=labels[lang]['photography'],
            movies_label=labels[lang]['movies'],
            photographer_label=labels[lang]['photographer']
        ))

def create_subsite_page(slug, data, css_version):
    """Generate a standalone subsite page (e.g. /thea, /edgar)"""
    def photo_grid_html(photos):
        grid = '            <div class="grid grid-cols-1 gap-8 lg:grid-cols-2">\n'
        for photo in photos:
            caption_en = nl2br(photo.get("description_en", ""))
            caption_de = nl2br(photo.get("description_de", ""))
            has_caption = caption_en or caption_de
            if has_caption:
                grid += '                <div class="space-y-4">\n'
            grid += '                <div class="photo-container">\n'
            grid += f'                    <img src="../{quote(photo["photo"])}" alt="{data["title"]}" class="w-full h-auto">\n'
            grid += '                </div>\n'
            if has_caption:
                grid += f'                <p class="text-sm italic text-gray-600 dark:text-gray-400" data-en="{escape(caption_en)}" data-de="{escape(caption_de)}">{caption_en}</p>\n'
                grid += '                </div>\n'
        grid += '            </div>\n'
        return grid

    def youtube_thumb_html(video_id, title):
        thumb = f'            <button type="button" class="relative block w-full overflow-hidden bg-black cursor-pointer group aspect-video" data-youtube="{escape(video_id)}" aria-label="{escape(re.sub(r'<[^>]+>', '', title))}">\n'
        thumb += f'                <img src="https://i.ytimg.com/vi/{quote(video_id)}/hqdefault.jpg" alt="" class="object-cover w-full h-full transition-opacity group-hover:opacity-80">\n'
        thumb += '                <span class="absolute inset-0 flex items-center justify-center">\n'
        thumb += '                    <span class="flex items-center justify-center w-20 h-20 transition-colors rounded-full bg-black/70 group-hover:bg-black/90">\n'
        thumb += '                        <svg class="w-10 h-10 ml-1 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"></path></svg>\n'
        thumb += '                    </span>\n'
        thumb += '                </span>\n'
        thumb += '            </button>\n'
        return thumb

    # Generate photo grid HTML: either titled sections or a single grid
    if "sections" in data:
        gallery_html = ''
        for section in data["sections"]:
            gallery_html += '            <section class="mb-16">\n'
            gallery_html += f'            <h3 class="mb-6 text-2xl font-semibold text-gray-900 dark:text-gray-100" data-en="{escape(section["title_en"])}" data-de="{escape(section["title_de"])}">{section["title_en"]}</h3>\n'
            if "youtube" in section:
                gallery_html += youtube_thumb_html(section["youtube"], section["title_en"])
            else:
                gallery_html += photo_grid_html(section["photos"])
            gallery_html += '            </section>\n'
    else:
        gallery_html = photo_grid_html(data["photos"])

    # Video modal, only needed when a section embeds a YouTube video
    video_modal_html = ''
    if any("youtube" in section for section in data.get("sections", [])):
        video_modal_html = '''
    <!-- Video Modal -->
    <div id="video-modal" class="lightbox" aria-hidden="true" role="dialog" aria-modal="true">
        <button id="video-modal-close" type="button" class="absolute p-2 text-white transition-opacity top-4 right-4 opacity-70 hover:opacity-100" aria-label="Close">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
        <div class="w-[90vw] max-w-5xl aspect-video">
            <iframe id="video-modal-frame" class="w-full h-full" src="" title="YouTube video" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>
        </div>
    </div>

    <!-- Video Modal Script -->
    <script>
        (function() {
            const modal = document.getElementById('video-modal');
            const frame = document.getElementById('video-modal-frame');

            function openVideo(id) {
                frame.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1&rel=0';
                modal.classList.add('active');
                modal.setAttribute('aria-hidden', 'false');
                document.body.style.overflow = 'hidden';
            }

            function closeVideo() {
                modal.classList.remove('active');
                modal.setAttribute('aria-hidden', 'true');
                frame.src = '';
                document.body.style.overflow = '';
            }

            document.querySelectorAll('[data-youtube]').forEach(button => {
                button.addEventListener('click', () => openVideo(button.dataset.youtube));
            });

            // Close on backdrop or close button, but not on the player itself
            modal.addEventListener('click', function(e) {
                if (e.target === modal || e.target.closest('#video-modal-close')) {
                    closeVideo();
                }
            });

            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && modal.classList.contains('active')) {
                    closeVideo();
                }
            });
        })();
    </script>
'''

    # Optional external links shown below the description
    links_html = ''
    if data.get("links"):
        links_html += '                <div class="flex flex-wrap gap-6 mt-6">\n'
        for link in data["links"]:
            links_html += f'                    <a href="{escape(link["url"])}" target="_blank" rel="noopener" class="text-lg text-gray-700 underline underline-offset-4 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">{link["label"]}</a>\n'
        links_html += '                </div>\n'

    # Optional portrait floated to the right of the intro text
    portrait_html = ''
    if data.get("portrait"):
        portrait_html += '                <div class="float-right w-32 mb-4 ml-6 photo-container md:w-56">\n'
        portrait_html += f'                    <img src="../{quote(data["portrait"])}" alt="{data["site_title"]}" class="w-full h-auto">\n'
        portrait_html += '                </div>\n'

    html = f'''<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data["site_title"]}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400;1,500&display=swap" rel="stylesheet">
    <link href="../assets/css/style.css?v={css_version}" rel="stylesheet">
    <script>
        // Dark mode detection and initialization
        if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
            document.documentElement.classList.add('dark')
        }} else {{
            document.documentElement.classList.remove('dark')
        }}
    </script>
</head>
<body class="min-h-full text-gray-900 transition-colors duration-300 bg-white dark:bg-gray-950 dark:text-gray-100">
    <!-- Photo Lightbox -->
    <div id="lightbox" class="lightbox" aria-hidden="true">
        <img id="lightbox-img" src="" alt="">
    </div>

    <!-- Header with Language Selector and Dark Mode Toggle -->
    <header class="fixed top-0 left-0 right-0 z-40 border-b border-gray-200 bg-gray-50 dark:bg-gray-900 dark:border-gray-800">
        <div class="flex items-center justify-between max-w-5xl px-4 py-3 mx-auto md:px-8">
            <div>
                <h1 class="text-xl font-bold text-gray-900 md:text-2xl dark:text-gray-100">{data["site_title"]}</h1>
            </div>
            <div class="flex items-center gap-4">
                <!-- Dark Mode Toggle -->
                <button id="dark-mode-toggle" class="p-2 transition-colors rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800" aria-label="Toggle dark mode">
                    <svg id="theme-icon" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
                    </svg>
                </button>
                <!-- Language Switcher -->
                <div class="flex gap-2">
                    <button id="lang-en" class="px-3 py-1 text-sm transition-colors rounded bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900">EN</button>
                    <button id="lang-de" class="px-3 py-1 text-sm transition-colors rounded text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800">DE</button>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content Area -->
    <main class="pt-20">
        <div class="max-w-5xl px-4 py-8 mx-auto md:px-8 md:py-12">
            <div class="mb-12 flow-root">
{portrait_html}                <h2 class="mb-4 text-3xl font-bold text-gray-900 md:text-5xl dark:text-gray-100">{data["title"]}</h2>
                <p id="description" class="text-lg leading-relaxed text-gray-700 dark:text-gray-300">{nl2br(data["description_en"])}</p>
{links_html}            </div>
{gallery_html}        </div>
    </main>
{video_modal_html}
    <!-- Footer -->
    <footer class="py-6 mt-8 border-t border-gray-200 dark:border-gray-800">
        <div class="max-w-5xl px-4 mx-auto md:px-8">
            <p class="text-xs text-center text-gray-500 dark:text-gray-500">&copy; <span id="copyright-year"></span> Estate of Ina Berneis</p>
            <script>document.getElementById('copyright-year').textContent = new Date().getFullYear();</script>
        </div>
    </footer>

    <!-- Dark Mode Toggle Script -->
    <script>
        (function() {{
            const toggle = document.getElementById('dark-mode-toggle');
            const icon = document.getElementById('theme-icon');

            // Get current mode: 'dark', 'light', or 'system'
            function getMode() {{
                if (localStorage.theme === 'dark') return 'dark';
                if (localStorage.theme === 'light') return 'light';
                return 'system';
            }}

            function applyMode(mode) {{
                if (mode === 'dark') {{
                    document.documentElement.classList.add('dark');
                    localStorage.theme = 'dark';
                }} else if (mode === 'light') {{
                    document.documentElement.classList.remove('dark');
                    localStorage.theme = 'light';
                }} else {{
                    localStorage.removeItem('theme');
                    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {{
                        document.documentElement.classList.add('dark');
                    }} else {{
                        document.documentElement.classList.remove('dark');
                    }}
                }}
                updateIcon(mode);
            }}

            function updateIcon(mode) {{
                if (mode === 'light') {{
                    // Sun icon for light mode
                    icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>';
                }} else if (mode === 'dark') {{
                    // Moon icon for dark mode
                    icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>';
                }} else {{
                    // Computer/monitor icon for system mode
                    icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>';
                }}
            }}

            // Cycle: light -> dark -> system -> light
            toggle.addEventListener('click', function() {{
                const current = getMode();
                let next;
                if (current === 'light') next = 'dark';
                else if (current === 'dark') next = 'system';
                else next = 'light';
                applyMode(next);
            }});

            // Initialize icon
            updateIcon(getMode());

            // Listen for system preference changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {{
                if (getMode() === 'system') {{
                    if (e.matches) {{
                        document.documentElement.classList.add('dark');
                    }} else {{
                        document.documentElement.classList.remove('dark');
                    }}
                }}
            }});
        }})();
    </script>

    <!-- Language Switcher Script -->
    <script>
        (function() {{
            const langEn = document.getElementById('lang-en');
            const langDe = document.getElementById('lang-de');
            const description = document.getElementById('description');

            const texts = {{
                en: {json.dumps(nl2br(data["description_en"]), ensure_ascii=False)},
                de: {json.dumps(nl2br(data["description_de"]), ensure_ascii=False)}
            }};

            let currentLang = localStorage.getItem('{slug}-lang') || 'en';

            function setLanguage(lang) {{
                currentLang = lang;
                localStorage.setItem('{slug}-lang', lang);
                description.innerHTML = texts[lang];
                document.querySelectorAll('[data-en]').forEach(el => {{
                    el.innerHTML = el.dataset[lang];
                }});
                document.documentElement.lang = lang;

                if (lang === 'en') {{
                    langEn.className = 'px-3 py-1 text-sm transition-colors rounded bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900';
                    langDe.className = 'px-3 py-1 text-sm transition-colors rounded text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800';
                }} else {{
                    langDe.className = 'px-3 py-1 text-sm transition-colors rounded bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900';
                    langEn.className = 'px-3 py-1 text-sm transition-colors rounded text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-800';
                }}
            }}

            // Initialize
            setLanguage(currentLang);

            langEn.addEventListener('click', () => setLanguage('en'));
            langDe.addEventListener('click', () => setLanguage('de'));
        }})();
    </script>

    <!-- Lightbox Script -->
    <script>
        (function() {{
            const lightbox = document.getElementById('lightbox');
            const lightboxImg = document.getElementById('lightbox-img');

            function openLightbox(src, alt) {{
                lightboxImg.src = src;
                lightboxImg.alt = alt || '';
                lightbox.classList.add('active');
                document.body.style.overflow = 'hidden';
            }}

            function closeLightbox() {{
                lightbox.classList.remove('active');
                document.body.style.overflow = '';
            }}

            // Click on photo to open lightbox
            document.querySelectorAll('.photo-container').forEach(container => {{
                container.addEventListener('click', function() {{
                    const img = this.querySelector('img');
                    if (img) {{
                        openLightbox(img.src, img.alt);
                    }}
                }});
            }});

            // Click anywhere on lightbox to close
            lightbox.addEventListener('click', closeLightbox);

            // Close on Escape key
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape' && lightbox.classList.contains('active')) {{
                    closeLightbox();
                }}
            }});
        }})();
    </script>
</body>
</html>'''

    # Write the subsite page
    os.makedirs(f'public/{slug}', exist_ok=True)
    with open(f'public/{slug}/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    """Main function to build the static site"""
    print("Building Ina Berneis website...")

    # Generate cache-buster version based on current timestamp
    css_version = int(time.time())

    # Create output directories
    os.makedirs('public/en', exist_ok=True)
    os.makedirs('public/de', exist_ok=True)
    os.makedirs('public/assets/css', exist_ok=True)
    os.makedirs('public/assets/images', exist_ok=True)

    # Read template
    with open('template.html', 'r', encoding='utf-8') as f:
        template = f.read()

    # Load photos, movies, and hollywood
    photos = load_photos()
    movies = load_movies()
    hollywood = load_hollywood()

    # Create life and career pages
    for page_name in ['life', 'career']:
        print(f"  Processing {page_name}.json...")
        with open(f'data/{page_name}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            create_page('en', page_name, data, template, photos, movies, css_version)
            create_page('de', page_name, data, template, photos, movies, css_version)

    # Create hollywood page
    print(f"  Processing hollywood.json...")
    create_page('en', 'hollywood', hollywood, template, photos, movies, css_version)
    create_page('de', 'hollywood', hollywood, template, photos, movies, css_version)

    # Create photo pages from photos.json
    print(f"  Processing photos.json...")
    for item in photos:
        page_name = slugify(item['title_en'])
        print(f"    Creating {page_name} pages...")
        create_page('en', page_name, item, template, photos, movies, css_version)
        create_page('de', page_name, item, template, photos, movies, css_version)

    # Create movie pages from movies.json
    print(f"  Processing movies.json...")
    for item in movies:
        page_name = 'movie-' + slugify(item['title_en'])
        print(f"    Creating {page_name} pages...")
        create_page('en', page_name, item, template, photos, movies, css_version)
        create_page('de', page_name, item, template, photos, movies, css_version)

    # Create standalone subsites
    for slug in ['thea', 'edgar']:
        print(f"  Processing {slug}.json...")
        create_subsite_page(slug, load_subsite(slug), css_version)

    # Create index page with language detection
    print("  Creating index page...")
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ina Berneis - Photographer</title>
    <link href="assets/css/style.css" rel="stylesheet">
    <script>
        const userLang = navigator.language || navigator.userLanguage;
        if (userLang.startsWith('de')) {
            window.location.replace("de/life.html");
        } else {
            window.location.replace("en/life.html");
        }
    </script>
</head>
<body class="text-gray-900 bg-white dark:bg-gray-950 dark:text-gray-100">
    <div class="flex items-center justify-center min-h-screen p-8">
        <div class="text-center">
            <h1 class="mb-4 text-5xl font-bold">Ina Berneis</h1>
            <p class="mb-8 text-xl text-gray-600 dark:text-gray-400">Photographer (1927-2003)</p>
            <p class="mb-4 text-gray-600 dark:text-gray-400">Redirecting...</p>
            <p class="mb-6 text-gray-600 dark:text-gray-400">If you are not redirected, please choose your language:</p>
            <div class="flex justify-center gap-4">
                <a href="en/life.html" class="px-6 py-3 text-white transition-colors bg-gray-900 rounded dark:bg-gray-100 dark:text-gray-900 hover:bg-gray-700 dark:hover:bg-gray-300">English</a>
                <a href="de/life.html" class="px-6 py-3 text-white transition-colors bg-gray-900 rounded dark:bg-gray-100 dark:text-gray-900 hover:bg-gray-700 dark:hover:bg-gray-300">Deutsch</a>
            </div>
        </div>
    </div>
</body>
</html>''')

    # print("✓ Build complete! Run 'npm run build-css' to generate CSS.")


if __name__ == '__main__':
    main()
