# Alien Classifier - Google Image Scraper

A Python script that scrapes images from Google Image search results using Selenium. Perfect for building image datasets for machine learning projects.

## Features

- Scrapes images from Google Images based on any search query
- Customizable number of images to download
- Configurable output directory
- Automatic ChromeDriver management (no manual setup required)
- Headless browser operation for efficiency
- Robust error handling

## Installation

### Prerequisites

- Python 3.7 or higher
- Google Chrome browser installed on your system

### Setup

1. Clone or download this repository

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

That's it! The script will automatically download and manage ChromeDriver using `webdriver-manager`.

## Usage

### Basic Usage

```bash
python alienscraper.py "your search query"
```

This will download 10 images (default) to the `results` directory.

### Custom Number of Images

```bash
python alienscraper.py "cute cats" --count 50
```

### Custom Output Directory

```bash
python alienscraper.py "space nebula" --output ./my_images
```

### Full Example

```bash
python alienscraper.py "alien planet concept art" --count 30 --output ./alien_images
```

## Command-Line Arguments

- `query` (required): The search term for Google Images
- `--count`: Number of images to download (default: 10)
- `--output`: Directory where images will be saved (default: "results")

## How It Works

1. The script opens Google Images in a headless Chrome browser
2. Searches for your specified query
3. Scrolls through the page to load image thumbnails
4. Clicks on thumbnails to access full-size image URLs
5. Downloads the images to your specified directory
6. Images are saved with indexed filenames (e.g., `your_query_1.jpg`, `your_query_2.jpg`, etc.)

## Troubleshooting

### ChromeDriver Issues

If you encounter ChromeDriver errors, the script should automatically download the correct version. If problems persist:

- Make sure Google Chrome is installed and up to date
- Try running the script again (first run may take longer to set up ChromeDriver)

### Fewer Images Than Expected

Google Images may not always have as many results as requested. The script will download as many as it can find.

### Connection Errors

If you get connection errors:

- Check your internet connection
- Google may temporarily block automated requests. Wait a few minutes and try again
- Consider reducing the number of images requested

### Permission Errors

If you get permission errors when saving files:

- Make sure you have write permissions in the output directory
- Try specifying a different output directory with `--output`

## Notes

- This script is for educational and research purposes
- Be respectful of Google's terms of service and rate limits
- Downloaded images may be subject to copyright - use responsibly
- The script runs in headless mode (no browser window visible)

## License

This project is open source and available for educational purposes.

