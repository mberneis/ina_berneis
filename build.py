import json
import os

def get_nav_items(lang, current_page):
    """Generate navigation items dynamically from data files"""
    nav_items = []
    photography_files = [f for f in os.listdir('data') if f not in ['life.json', 'career.json']]

    for file in sorted(photography_files):
        page_name = file.replace('.json', '')
        with open(f'data/{file}', 'r') as f:
            data = json.load(f)
            title = data[f'title_{lang}']
            active_class = 'font-semibold bg-gray-200 dark:bg-gray-800' if current_page == page_name else ''
            nav_items.append(f'<li><a href="{page_name}.html" class="nav-link {active_class}">{title}</a></li>')

    return '\n                        '.join(nav_items)

def create_page(lang, page_name, data, template):
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
        content = f'<h1 class="text-5xl font-bold mb-6 text-gray-900 dark:text-gray-100">{data[f"title_{lang}"]}</h1>\n'
        content += f'<p class="text-lg text-gray-700 dark:text-gray-300 mb-12 leading-relaxed">{data[f"description_{lang}"]}</p>\n'
        content += '<div class="space-y-0">\n'
        for event in data["events"]:
            content += '    <div class="timeline-item">\n'
            content += f'        <h2 class="text-2xl font-bold mb-3 text-gray-900 dark:text-gray-100">{event["date"]}</h2>\n'
            content += f'        <p class="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">{event[f"description_{lang}"]}</p>\n'
            if "photo" in event:
                content += '        <div class="photo-container max-w-md">\n'
                content += f'            <img src="../{event["photo"]}" alt="Photo from {event["date"]}" class="w-full h-auto">\n'
                content += '        </div>\n'
            content += '    </div>\n'
        content += '</div>'

    # Create career page
    elif page_name == 'career':
        content = f'<h1 class="text-5xl font-bold mb-6 text-gray-900 dark:text-gray-100">{data[f"title_{lang}"]}</h1>\n'
        content += '<div class="prose prose-lg dark:prose-invert max-w-none">\n'
        # Iterate over all key/value pairs in content section
        for key, value in data[f"content_{lang}"].items():
            # Use the key as the header (capitalize first letter of each word)
            header = key.replace('_', ' ').title()
            content += f'    <h2 class="text-3xl font-bold mt-8 mb-4 text-gray-900 dark:text-gray-100">{header}</h2>\n'
            content += f'    <p class="text-gray-700 dark:text-gray-300 leading-relaxed mb-8">{value}</p>\n'
        content += '</div>'

    # Create photography pages
    else:
        content = f'<h1 class="text-5xl font-bold mb-6 text-gray-900 dark:text-gray-100">{data[f"title_{lang}"]}</h1>\n'
        content += f'<p class="text-lg text-gray-700 dark:text-gray-300 mb-12 leading-relaxed">{data[f"description_{lang}"]}</p>\n'
        content += '<div class="grid grid-cols-1 md:grid-cols-2 gap-8">\n'
        for photo in data["photos"]:
            content += '    <div class="space-y-4">\n'
            content += '        <div class="photo-container">\n'
            content += f'            <img src="../{photo["photo"]}" alt="{data[f"title_{lang}"]}" class="w-full h-auto">\n'
            content += '        </div>\n'
            if f"description_{lang}" in photo:
                content += f'        <p class="text-sm text-gray-600 dark:text-gray-400 italic">{photo[f"description_{lang}"]}</p>\n'
            content += '    </div>\n'
        content += '</div>'

    # Navigation items
    nav_items = get_nav_items(lang, page_name)

    # Active states
    life_active = 'font-semibold bg-gray-200 dark:bg-gray-800' if page_name == 'life' else ''
    career_active = 'font-semibold bg-gray-200 dark:bg-gray-800' if page_name == 'career' else ''
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

    # Create pages from data files
    data_files = sorted(os.listdir('data'))
    for file in data_files:
        if file.endswith('.json'):
            print(f"  Processing {file}...")
            with open(f'data/{file}', 'r', encoding='utf-8') as f:
                data = json.load(f)
                page_name = file.split('.')[0]
                create_page('en', page_name, data, template)
                create_page('de', page_name, data, template)

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
<body class="bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100">
    <div class="min-h-screen flex items-center justify-center p-8">
        <div class="text-center">
            <h1 class="text-5xl font-bold mb-4">Ina Berneis</h1>
            <p class="text-xl text-gray-600 dark:text-gray-400 mb-8">Photographer (1927-2003)</p>
            <p class="text-gray-600 dark:text-gray-400 mb-4">Redirecting...</p>
            <p class="text-gray-600 dark:text-gray-400 mb-6">If you are not redirected, please choose your language:</p>
            <div class="flex gap-4 justify-center">
                <a href="en/life.html" class="px-6 py-3 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded hover:bg-gray-700 dark:hover:bg-gray-300 transition-colors">English</a>
                <a href="de/life.html" class="px-6 py-3 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded hover:bg-gray-700 dark:hover:bg-gray-300 transition-colors">Deutsch</a>
            </div>
        </div>
    </div>
</body>
</html>''')

    print("✓ Build complete! Run 'npm run build-css' to generate CSS.")


if __name__ == '__main__':
    main()
