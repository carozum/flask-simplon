import numpy as np
from PIL import Image, ImageDraw, ImageFont


def generate_digit_image(digit):
    image_size = (28, 28)
    image = Image.new("L", image_size, color=255)  # Create a white image
    draw = ImageDraw.Draw(image)
    # Provide the path to a TTF font file
    font = ImageFont.load_default()
    # font_path = "fonts/MeowScript-Regular.ttf"
    #
    # try:
    #     # Use a truetype font for better results
    #     font = ImageFont.truetype(font_path, size=20)
    # except IOError:
    #     font = ImageFont.load_default()

    draw.text((8, 5), str(digit), fill=0, font=font)  # Draw the digit in black

    return image


# Example: Save a generated digit image
for i in range(10):
    digit_image = generate_digit_image(i)
    digit_image.save(f"digits/digit_{i}.png")
