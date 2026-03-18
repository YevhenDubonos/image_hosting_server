ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024


def validate_file_extension(filename):
    if not filename or '.' not in filename:
        return False, "File has no extension"
    extension = filename.lower().split('.')[-1]
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ', '.join(ALLOWED_EXTENSIONS)
        return False, f"Unsupported file format: .{extension}. Allowed: {allowed}"
    return True, "File extension is supported"


def validate_file_size(file_size):
    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        max_mb = MAX_FILE_SIZE / (1024 * 1024)
        return False, f"File too large: {size_mb:.2f} MB (max {max_mb} MB)"
    return True, "File size is acceptable"


def validate_image_file(file, filename):
    is_valid, message = validate_file_extension(filename)
    if not is_valid:
        return False, f"Format error: {message}"

    current_position = file.tell()
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(current_position)

    is_valid, message = validate_file_size(file_size)
    if not is_valid:
        return False, f"Size error: {message}"

    return True, "File passed validation successfully"