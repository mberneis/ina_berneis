import json
import os
import re
import unicodedata

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

def load_thea():
    """Load thea.json data"""
    with open('data/thea.json', 'r', encoding='utf-8') as f:
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

def create_page(lang, page_name, data, template, photos, movies, hollywood=None):
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

def create_thea_page(data):
    """Generate the standalone thea subsite page"""
    # Generate photo grid HTML
    photos_html = ''
    for photo in data["photos"]:
        photos_html += '                <div class="photo-container">\n'
        photos_html += f'                    <img src="images/{os.path.basename(photo["photo"])}" alt="Thea" class="w-full h-auto">\n'
        photos_html += '                </div>\n'

    html = f'''<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thea Ziesemar</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400;1,500&display=swap" rel="stylesheet">
    <link href="../assets/css/style.css?v=3" rel="stylesheet">
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
                <h1 class="text-xl font-bold text-gray-900 md:text-2xl dark:text-gray-100">Thea Ziesemar</h1>
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
            <div class="mb-12">
                <h2 class="mb-4 text-3xl font-bold text-gray-900 md:text-5xl dark:text-gray-100">{data["title"]}</h2>
                <p id="description" class="text-lg leading-relaxed text-gray-700 dark:text-gray-300">{data["description_en"]}</p>
            </div>
            <div class="grid grid-cols-1 gap-8 lg:grid-cols-2">
{photos_html}            </div>
        </div>
    </main>

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
                en: "{data["description_en"]}",
                de: "{data["description_de"]}"
            }};

            let currentLang = localStorage.getItem('thea-lang') || 'en';

            function setLanguage(lang) {{
                currentLang = lang;
                localStorage.setItem('thea-lang', lang);
                description.textContent = texts[lang];
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

    # Write the thea page
    os.makedirs('public/thea', exist_ok=True)
    with open('public/thea/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    """Main function to build the static site"""
    print("Building Ina Berneis website...")

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
            create_page('en', page_name, data, template, photos, movies)
            create_page('de', page_name, data, template, photos, movies)

    # Create hollywood page
    print(f"  Processing hollywood.json...")
    create_page('en', 'hollywood', hollywood, template, photos, movies)
    create_page('de', 'hollywood', hollywood, template, photos, movies)

    # Create photo pages from photos.json
    print(f"  Processing photos.json...")
    for item in photos:
        page_name = slugify(item['title_en'])
        print(f"    Creating {page_name} pages...")
        create_page('en', page_name, item, template, photos, movies)
        create_page('de', page_name, item, template, photos, movies)

    # Create movie pages from movies.json
    print(f"  Processing movies.json...")
    for item in movies:
        page_name = 'movie-' + slugify(item['title_en'])
        print(f"    Creating {page_name} pages...")
        create_page('en', page_name, item, template, photos, movies)
        create_page('de', page_name, item, template, photos, movies)

    # Create thea subsite
    print("  Processing thea.json...")
    thea = load_thea()
    create_thea_page(thea)

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
