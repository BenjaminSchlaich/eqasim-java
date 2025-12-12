import concurrent.futures
import pathlib
import urllib.error
import urllib.request
from typing import Iterable


DOWNLOADS_FILE = pathlib.Path("data/heights/downloads.txt")
OUTPUT_DIR = pathlib.Path("data/heights")
MAX_WORKERS = 5


def load_urls(path: pathlib.Path) -> Iterable[str]:
    """Yield non-empty, non-comment lines from the downloads list."""
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            clean = line.strip()
            if clean and not clean.startswith("#"):
                yield clean


def download_file(url: str, target_dir: pathlib.Path) -> None:
    """Download `url` into `target_dir` unless it already exists."""
    filename = url.rsplit("/", 1)[-1]
    target_path = target_dir / filename

    if target_path.exists():
        return

    try:
        with urllib.request.urlopen(url) as response, target_path.open("wb") as output:
            output.write(response.read())
    except urllib.error.URLError as exc:
        # Surface minimal context without stopping all downloads
        raise RuntimeError(f"Failed to download {url}: {exc}") from exc


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    urls = list(load_urls(DOWNLOADS_FILE))
    if not urls:
        raise SystemExit(f"No URLs found in {DOWNLOADS_FILE}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(download_file, url, OUTPUT_DIR): url for url in urls}
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                future.result()
            except Exception as exc:  # noqa: BLE001 - want to bubble details
                print(exc)
                raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
