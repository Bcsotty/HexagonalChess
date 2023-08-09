from PIL import Image
import os


def create_collage(input_folder, output_file, row_count, column_count):
    png_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.png')]

    if len(png_files) == 0:
        print("No PNG files found in input folder.")
        return

    png_files.sort()

    first_image = Image.open(os.path.join(input_folder, png_files[0]))
    image_width, image_height = first_image.size

    collage_width = image_width * column_count
    collage_height = image_height * row_count

    collage = Image.new('RGBA', (collage_width, collage_height), (0, 0, 0, 0))

    for i, png_file in enumerate(png_files):
        row = i // column_count
        col = i % column_count
        x_offset = col * image_width
        y_offset = row * image_height
        image = Image.open(os.path.join(input_folder, png_file))
        collage.paste(image, (x_offset, y_offset))

    collage.save(output_file, 'PNG')
    print(f"Collage saved as {output_file}")


input_folder = "images/seperate"

output_file = "images/pieces.png"

row_count = 2
column_count = 6

create_collage(input_folder, output_file, row_count, column_count)