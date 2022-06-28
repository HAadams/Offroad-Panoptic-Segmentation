import os
import re
import shutil
from multiprocessing import Pool
from pathlib import Path

import parallelbar
from PIL import Image
from sklearn.model_selection import train_test_split
from tqdm import tqdm


def _split_name(filename):
    parts = re.split(r"\.|/|\\", str(filename))
    return (parts[-2], parts[-1])


def _consolidate_files(dataset_dir, new_dir, file_ext):
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
        files = list(Path(dataset_dir).glob(f"**/*.{file_ext}"))
        print(f"{len(files)} files with extension .{file_ext} found")
        for f in tqdm(files):
            file_name = ".".join(_split_name(f))
            shutil.move(f, os.path.join(new_dir, file_name))
    else:
        print(f"Directory already exists at path: {new_dir}")


def _remove_unpaired_images(image_dir, label_dir):
    if not os.path.exists(image_dir) or not os.path.exists(label_dir):
        return
    
    image_set = set(_split_name(image)[0] for image in Path(image_dir).glob("*"))
    label_set = set(_split_name(label)[0] for label in Path(label_dir).glob("*"))
    unpaired_images = image_set.difference(label_set)
    print(f"Deleting {len(unpaired_images)} unpaired images")

    for im in unpaired_images:
        image_path = os.path.join(image_dir, f"{im}.jpg")
        if os.path.exists(image_path):
            os.remove(image_path)


def _get_data_splits(image_dir, test_size, random_state=123):
    files = [_split_name(filename)[0] for filename in Path(image_dir).glob("*")]
    train, test = train_test_split(files, test_size=test_size, random_state=random_state)
    print(len(train), len(test))
    return train, test


def _make_data_dirs(image_dir, label_dir, split_names):
    for dir_name in [image_dir, label_dir]:
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        for split_name in split_names:
            split_dir = os.path.join(dir_name, split_name)
            if not os.path.exists(split_dir):
                os.mkdir(split_dir)


def _move_files(image_dir, label_dir, splits):
    _make_data_dirs(image_dir, label_dir, [name for name, _ in splits])

    for dir_name, data_split in splits:
        for filename in tqdm(data_split, desc=dir_name):
            image_name = f"{filename}.jpg"
            label_name = f"{filename}.png"

            shutil.move(
                os.path.join(image_dir, image_name),
                os.path.join(image_dir, dir_name, image_name)
            )
            shutil.move(
                os.path.join(label_dir, label_name),
                os.path.join(label_dir, dir_name, label_name)
            )


def generate_split_datasets(dataset_path, images_extract_path, labels_extract_path, test_size=0.2):
    processed_images_path = os.path.join(dataset_path, "images")
    processed_labels_path = os.path.join(dataset_path, "labels")

    # Consolidate the extracted files to their new directories
    _consolidate_files(images_extract_path, processed_images_path, "jpg")
    _consolidate_files(labels_extract_path, processed_labels_path, "png")

    # Remove any images without a paired label file
    _remove_unpaired_images(processed_images_path, processed_labels_path)

    # Split into training and testing
    train_split, test_split = _get_data_splits(processed_images_path, test_size)
    _move_files(
        processed_images_path,
        processed_labels_path,
        [("train", train_split), ("test", test_split)]
    )

    return processed_images_path, processed_labels_path


def _change_image_ext(args):
    filename, from_ext, to_ext = args
    image = Image.open(filename)
    image.save(str(filename).replace(from_ext, to_ext))


def change_file_extensions(images_dir, from_ext, to_ext, n_proc=1):
    image_files = list(Path(images_dir).glob(f"**/*{from_ext}"))

    with Pool():
        parallelbar.progress_imap(
            func=_change_image_ext,
            tasks=[(image_filename, from_ext, to_ext) for image_filename in image_files],
            n_cpu=n_proc,
            chunk_size=10,
        )


