# Documentation

This folder contains the static HTML documentation for the Sri Lanka Government Datasets.

## Files

- `index.html` - Main HTML file
- `styles.css` - CSS styling and layout
- `README.md` - This file

## Features

- **Interactive folder tree** with collapsible sections (CSS-only, no JavaScript)
- **Responsive design** that works on all devices
- **Professional styling** with hover effects
- **All 248 datasets** automatically included

## How to Use

1. Open `index.html` in a web browser
2. Click on folder headers to expand/collapse sections
3. Click on dataset links to view JSON files

## Updating Documentation

When you add new data to the `data/` folder:

1. Run: `python3 generate_static_html.py`
2. The `index.html` file will be updated automatically
3. Commit and push to GitHub

## GitHub Pages Deployment

1. Push the `index.html` file to your GitHub repository
2. Enable GitHub Pages in repository settings
3. Select "Deploy from a branch" → `main`
4. Your documentation will be live at `https://yourusername.github.io/datasets/`

## Benefits

- **No JavaScript**: Pure HTML/CSS - works everywhere
- **Clean Separation**: HTML and CSS in separate files for easy maintenance
- **Better SEO**: Search engines can index all content
- **Easy Maintenance**: Just run one Python script to update

## Browser Compatibility

- All modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile responsive design
- Works even with JavaScript disabled
