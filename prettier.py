import os
import re
import shutil
import fileinput

def get_max_saved_image_idx(path: str) -> int:
    saved_images_indices = [
        int(re.split('[-.]', saved_image_file)[1])
        for saved_image_file in os.listdir(os.path.join(path, 'images'))
        if re.split('[-.]', saved_image_file)[1].isdigit()
    ]
    if saved_images_indices:
        return sorted(saved_images_indices)[-1]
    else:
        # If there are no 'image-{index}.png' files in /images folder set max index to zero
        return 0


def make_prettier(path: str) -> None:
    image_files = [file for file in os.listdir(path) if file.split('.')[-1] == 'png']
    obsidian_image_files = [file for file in image_files if file.startswith('Pasted')]
    vs_code_image_files = [file for file in image_files if not file in obsidian_image_files]

    lecture_files = [file for file in os.listdir(path) if file.split('.')[-1] == 'md']

    vs_code_image_names_mapping: dict[str, str] = {}
    obsidian_image_names_mapping: dict[str, str] = {}
    max_saved_image_idx: int | None = None

    # Create images folder if not present
    if not os.path.exists(os.path.join(path, 'images')):
        os.mkdir(os.path.join(path, 'images'))

    # Handle VS code image files
    for image_file in vs_code_image_files:
        # If there is no image with the same name in /images folder (no rename required), just move the image file
        if not image_file in os.listdir(os.path.join(path, 'images')):
            shutil.move(src=os.path.join(path, image_file), dst=os.path.join(path, 'images', image_file))
        else:
            # Get max index of all images with names 'image-{index}.png' in /images folder
            if max_saved_image_idx is None:
                max_saved_image_idx = get_max_saved_image_idx(path)

            # Prepare new index for the image file
            new_image_idx = max_saved_image_idx + 1
            max_saved_image_idx += 1

            # Move the image file and save its name mapping (for later change in notes part)
            shutil.move(src=os.path.join(path, image_file), dst=os.path.join(path, 'images', f'image-{new_image_idx}.png'))
            vs_code_image_names_mapping.update({
                image_file: f'image-{new_image_idx}.png'
            })

    # Handle obsidian image files
    for image_file in obsidian_image_files:
        # If /images folder is empty
        if not os.listdir(os.path.join(path, 'images')):
            # Use default image file name
            default_image_file = 'image.png'

            # Move the image file and save its name mapping (for later change in notes part)
            shutil.move(src=os.path.join(path, image_file), dst=os.path.join(path, 'images', default_image_file))
            obsidian_image_names_mapping.update({
                image_file: default_image_file
            })
        else:
            # Get max index of all images with names 'image-{index}.png' in /images folder
            if max_saved_image_idx is None:
                max_saved_image_idx = get_max_saved_image_idx(path)

            # Prepare new index for the image file
            new_image_idx = max_saved_image_idx + 1
            max_saved_image_idx += 1

            # Move the image file and save its name mapping (for later change in notes part)
            shutil.move(src=os.path.join(path, image_file), dst=os.path.join(path, 'images', f'image-{new_image_idx}.png'))
            obsidian_image_names_mapping.update({
                image_file: f'image-{new_image_idx}.png'
            })

    # Handle note files
    for lecture_file in lecture_files:
        with fileinput.input(os.path.join(path, lecture_file), inplace=True, encoding="utf8") as file:
            for line in file:
                # Remove newline symbol (because there will be newline anyway when print is used)
                line = line.split('\n')[0]

                if re.match('!\[alt text\]\([^)]*\)', line): # if there is image link in line (VS code)
                    old_image_path = re.split('[()]', line)[-2]
                    new_image_path = old_image_path

                    # Change line only if image file was moved (it must not have 'images' substring in the line)
                    if 'images' not in os.path.split(old_image_path):
                        # If image file name was changed (because of index) and it is saved in mapping, replace it
                        # Otherwise, just leave the previous image file name
                        #
                        # '/'.join instead of os.path.join, because for markdown we must always have '/' separator
                        if old_image_path in vs_code_image_names_mapping:
                            new_image_path = '/'.join(['images', vs_code_image_names_mapping[old_image_path]])
                        else:
                            new_image_path = '/'.join(['images', old_image_path])

                    # Change line in file
                    print(line.replace(old_image_path, new_image_path))

                elif re.match('!\[\[Pasted image [^.]*.png\]\]', line): # if there is image link in line (obsidian)
                    old_image_path = re.split(r'[\[\]]', line)[-3]
                    assert old_image_path in obsidian_image_names_mapping

                    # '/'.join instead of os.path.join, because for markdown we must always have '/' separator
                    new_image_path = '/'.join(['images', obsidian_image_names_mapping[old_image_path]])

                    # Change line in file
                    print(line.replace(f"![[{old_image_path}]]", f"![alt text]({new_image_path})"))

                else:
                    # Print the initial line (it has no image links)
                    print(line)


if __name__ == "__main__":
    make_prettier("./demo")