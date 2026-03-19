import uuid
from pathlib import Path

IMAGES_DIR = Path(__file__).parent.parent / 'images'


def generate_unique_filename(original_name):
    ext = original_name.lower().split('.')[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"
    return unique_name


def save_file(file_data, filename):
    IMAGES_DIR.mkdir(exist_ok=True)
    unique_name = generate_unique_filename(filename)
    filepath = IMAGES_DIR / unique_name

    with open(filepath, 'wb') as f:
        f.write(file_data)

    print(f"✅ File saved successfully: {unique_name}")
    return unique_name


def delete_file(filename):
    filepath = IMAGES_DIR / filename
    if filepath.exists():
        filepath.unlink()
        return True
    return False
