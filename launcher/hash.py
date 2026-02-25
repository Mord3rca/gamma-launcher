from hashlib import md5
from pathlib import Path
from tqdm import tqdm


def check_hash(file: Path, checksum: str, desc: str = None) -> bool:
    """Compute MD5 hash of a file and display progress with `tqdm`

    Argument(s):
    * file -- File path as Path or str to check
    * checksum -- Known checksum of the file

    Keyword argument(s):
    * desc -- Custom description for `tqdm`

    Return True if computed checksum and checksum match
    """
    hash = md5()
    with open(file, 'rb') as f, tqdm(
        desc=desc or f"Calculating hash of {file.name}",
        unit="iB", unit_scale=True, unit_divisor=1024,
        total=file.stat().st_size, ascii=True
    ) as progress:
        while True:
            s = f.read(1024*1024)
            if not s:
                break
            hash.update(s)
            progress.update(len(s))

    return hash.hexdigest() == checksum
