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

def get_nav_items(lang, current_page, photos):
    """Generate navigation items from photos array (order preserved)"""
    nav_items = []
    for item in photos:
        page_name = slugify(item['title_en'])
        title = item[f'title_{lang}']
        active_class = 'font-semibold bg-gray-200 dark:bg-gray-800 dark:text-gray-100' if current_page == page_name else ''
        nav_items.append(f'<li><a href="{page_name}.html" class="nav-link {active_class}">{title}</a></li>')

    return '\n                        '.join(nav_items)

def create_page(lang, page_name, data, template, photos):
    """Generate HTML page from data"""
    labels = {
        'en': {
            'life': 'Life',
            'career': 'Career',
            'photography': 'Photography',
            'photographer': 'Photographer'
        },
        'de': {
            'life': 'Leben',
            'career': 'Karriere',
            'photography': 'Fotografie',
            'photographer': 'Fotografin'
        }
    }

    # Create life page with timeline
    if page_name == 'life':
        content = '<div class="flex flex-col-reverse mb-12 md:flex-row md:items-start md:gap-8">\n'
        content += '    <div class="flex-1">\n'
        content += f'        <h1 class="mb-6 text-3xl font-bold text-gray-900 md:text-5xl dark:text-gray-100">{data[f"title_{lang}"]}</h1>\n'
        content += f'        <p class="text-lg leading-relaxed text-gray-700 dark:text-gray-300">{nl2br(data[f"description_{lang}"])}</p>\n'
        content += '    </div>\n'
        content += '    <div class="w-1/3 mb-6 md:mb-0 shrink-0">\n'
        content += '        <img src="../assets/images/ina.png" alt="Ina Berneis" class="w-full h-auto rounded-lg shadow-lg">\n'
        content += '    </div>\n'
        content += '</div>\n'
        content += '<div class="space-y-0">\n'
        for event in data["events"]:
            content += '    <div class="timeline-item">\n'
            content += f'        <h2 class="mb-3 text-xl font-bold text-gray-900 md:text-2xl dark:text-gray-100">{event["date"]}</h2>\n'
            content += f'        <p class="mb-4 leading-relaxed text-gray-700 dark:text-gray-300">{nl2br(event[f"description_{lang}"])}</p>\n'
            if "photo" in event:
                content += '        <div class="max-w-md photo-container">\n'
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

    # Create photography pages
    else:
        content = f'<h1 class="mb-6 text-3xl font-bold text-gray-900 md:text-5xl dark:text-gray-100">{data[f"title_{lang}"]}</h1>\n'
        content += f'<p class="mb-12 text-lg leading-relaxed text-gray-700 dark:text-gray-300">{nl2br(data[f"description_{lang}"])}</p>\n'
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

    # Active states
    life_active = 'font-semibold bg-gray-200 dark:bg-gray-800 dark:text-gray-100' if page_name == 'life' else ''
    career_active = 'font-semibold bg-gray-200 dark:bg-gray-800 dark:text-gray-100' if page_name == 'career' else ''
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
            life_active=life_active,
            career_active=career_active,
            lang_en_active=lang_en_active,
            lang_de_active=lang_de_active,
            life_label=labels[lang]['life'],
            career_label=labels[lang]['career'],
            photography_label=labels[lang]['photography'],
            photographer_label=labels[lang]['photographer']
        ))

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

    # Load photos from photos.json
    photos = load_photos()

    # Create life and career pages
    for page_name in ['life', 'career']:
        print(f"  Processing {page_name}.json...")
        with open(f'data/{page_name}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            create_page('en', page_name, data, template, photos)
            create_page('de', page_name, data, template, photos)

    # Create photo pages from photos.json (order preserved)
    print(f"  Processing photos.json...")
    for item in photos:
        page_name = slugify(item['title_en'])
        print(f"    Creating {page_name} pages...")
        create_page('en', page_name, item, template, photos)
        create_page('de', page_name, item, template, photos)

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

    print("✓ Build complete! Run 'npm run build-css' to generate CSS.")


if __name__ == '__main__':
    main()
