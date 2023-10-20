try:
    # Only available in Python 3.11
    from hashlib import file_digest
except ImportError:
    from hashlib import md5

    def file_digest(file, *args, **kwargs):
        hash_obj = md5()
        for chunk in iter(lambda: file.read(1024 * 1024), ''):
            hash_obj.update(chunk)
        return hash_obj
