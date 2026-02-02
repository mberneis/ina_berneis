---
noteId: "293ae2c0ffd411f0af7d4b0a7e6fe571"
tags: []

---

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a bilingual (English/German) static website for photographer Ina Berneis (1927-2003). The site showcases her photography work, biography, and career.

## Build Commands

```bash
# Full build: generates HTML pages from JSON data and compiles CSS
yarn run build

# Generate HTML pages only (from JSON data)
python3 build.py

# Compile Tailwind CSS only
yarn run build-css
```

## Architecture

### Static Site Generation

The site uses a Python-based static site generator (`build.py`) that:
- Reads content from JSON files in `data/`
- Applies a single HTML template (`template.html`) with Python string formatting placeholders
- Generates bilingual pages in `public/en/` and `public/de/`
- Creates an index page with automatic language detection based on browser settings

### Data Structure

Content is stored in JSON files under `data/`:
- `life.json` - Biography timeline with dates and events
- `career.json` - Career information
- `photos.json` - Photography subjects (actors, celebrities)
- `movies.json` - Film-related photography

Each JSON entry contains bilingual fields: `title_en`, `title_de`, `description_en`, `description_de`.

### Output Structure

```
public/
├── index.html           # Language detection redirect
├── en/                  # English pages
├── de/                  # German pages
└── assets/
    ├── css/style.css    # Compiled Tailwind CSS
    └── images/          # Photo assets
```

### Styling

- Tailwind CSS 4 with PostCSS
- Custom theme defined in `input.css` using `@theme` directive
- Monochromatic color palette for black & white photography aesthetic
- Dark mode support via system preference and manual toggle
- Custom components: timeline, lightbox, navigation

### Key Functions in build.py

- `slugify()` - Converts titles to URL-friendly page names
- `create_page()` - Generates HTML for different page types (life/career/photo/movie)
- `get_nav_items()` / `get_movie_nav_items()` - Builds navigation menus from JSON data

### Template Placeholders

The `template.html` uses Python format strings: `{lang}`, `{title}`, `{content}`, `{nav_items}`, `{movie_nav_items}`, etc.
