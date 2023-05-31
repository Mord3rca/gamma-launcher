try:
    # Only available in Python 3.11
    from hashlib import file_digest
except ImportError:
    from hashlib import md5

    def file_digest(file, *args, **kwargs) -> md5:
        hash = md5()
        while True:
            r = file.read(1024*1024)
            if not r:
                break
            hash.update(r)
        return hash
