from PIL import Image
import requests
from io import BytesIO
from colorthief import ColorThief

def is_black_square(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    color_thief = ColorThief(img)

    # check dominant color
    dominant_color = color_thief.get_color(quality=1)
    black_vals = [c for c in dominant_color if c < 12]
    is_dark = len(black_vals) == len(dominant_color)

    # check palette
    palette = color_thief.get_palette(quality=1)
    black_palette = []

    # to distinguish "dark" images from truly all black images, make sure
    # all the colors in the palette are also dark
    if is_dark:
        for color in palette:
            black_vals = [c for c in color if c < 12]
            is_black_color = len(black_vals) == len(color)
            if is_black_color:
                black_palette.append(color)

    is_black_palette = len(black_palette) == len(palette)
    return is_dark and is_black_palette
