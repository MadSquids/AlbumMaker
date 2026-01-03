import os
import re
import requests
import musicbrainzngs
import SongDetailsAdder
import Downloader
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

musicbrainzngs.set_useragent("AlbumMaker", "1.0", "madsquidsdisease@gmail.com")

# --- MusicBrainz helper functions ---

def searchReleaseByBarcode(barcode):
    """Search MusicBrainz release by barcode (returns first match)."""
    try:
        result = musicbrainzngs.search_releases(barcode=barcode, limit=1)
        releases = result.get("release-list", [])
        if releases:
            return releases[0]
    except Exception as e:
        print("MusicBrainz barcode search failed:", e)
    return None

def searchReleases(artist_name, album_name, limit=5):
    """Search MusicBrainz releases by artist and album name."""
    try:
        result = musicbrainzngs.search_releases(artist=artist_name, release=album_name, limit=limit)
        return result.get("release-list", [])
    except Exception as e:
        print("MusicBrainz search failed:", e)
        return []

def chooseRelease(releases):
    """Prompt user to select the correct release from a list."""
    print("Select the correct release:")
    for idx, release in enumerate(releases, start=1):
        title = release.get("title", "Unknown")
        artist = release["artist-credit"][0]["name"] if release.get("artist-credit") else "Unknown"
        date = release.get("date", "Unknown")
        country = release.get("country", "Unknown")
        status = release.get("status", "Unknown")
        track_count = release.get("track-count", "Unknown")
        medium_count = release.get("medium-count", "Unknown")
        format_ = ", ".join([medium.get("format", "Unknown") for medium in release.get("medium-list", [{}])])
        label = release.get("label-info-list", [{}])[0].get("label", {}).get("name", "Unknown") if release.get("label-info-list") else "Unknown"
        packaging = release.get("packaging", "Unknown")
        barcode = release.get("barcode", "Unknown")
        
        print(f"{idx}: {title} ({status}, {format_}, {track_count} tracks, {medium_count} disc(s), "
              f"{country}, Label: {label}, Packaging: {packaging}, Barcode: {barcode}, Released: {date})")
    
    choice = input(f"Enter number (1-{len(releases)}) or 0 to cancel: ")
    try:
        choice = int(choice)
        if 1 <= choice <= len(releases):
            return releases[choice - 1]
    except:
        pass
    return None

def getTrackList(release_id):
    """Get official track list from MusicBrainz, continuous numbering for multi-disc albums."""
    trackList = []
    try:
        release = musicbrainzngs.get_release_by_id(release_id, includes=["recordings"])
        track_number = 1
        for medium in release["release"]["medium-list"]:
            for track in medium["track-list"]:
                title = track["recording"]["title"]
                trackList.append({"number": track_number, "title": title})
                track_number += 1
    except Exception as e:
        print("Failed to get track list:", e)
    return trackList

def sanitize_title(title):
    """Lowercase, remove non-alphanumerics for matching"""
    return re.sub(r'[^a-z0-9]', '', title.lower())

def renameTracks(folderPath, trackList, artist):
    """
    Rename downloaded files to match MusicBrainz track titles using fuzzy match.
    This ensures track numbers and titles are correctly assigned.
    """
    files = [f for f in os.listdir(folderPath) if f.lower().endswith(".m4a")]
    for file in files:
        original_path = os.path.join(folderPath, file)
        # Remove artist name and extension from filename
        name_part = file.replace(".m4a", "")
        name_part = name_part.replace(artist, "").replace("-", "").strip()
        sanitized_file = sanitize_title(name_part)

        # Find best match in trackList
        best_match = None
        for track in trackList:
            if "filename" in track:
                continue  # already matched
            if sanitize_title(track["title"]) in sanitized_file or sanitized_file in sanitize_title(track["title"]):
                best_match = track
                break

        if not best_match:
            # fallback: assign to first unmatched track
            for track in trackList:
                if "filename" not in track:
                    best_match = track
                    break

        if best_match:
            safe_title = "".join(c for c in best_match["title"] if c not in "\\/:*?\"<>|")
            new_filename = f"{safe_title}.m4a"
            new_path = os.path.join(folderPath, new_filename)
            os.rename(original_path, new_path)
            best_match["filename"] = new_filename

def downloadCoverArt(releaseId, outputDir):
    url = f"https://coverartarchive.org/release/{releaseId}/front"

    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Cover download failed: {e}")
        return None

    coverPath = os.path.join(outputDir, "cover.jpg")
    with open(coverPath, "wb") as f:
        f.write(response.content)

    print(f"Downloaded cover art to {coverPath}")
    return coverPath

def sanitizeFileName(name):
    return re.sub(r'[\\/:*?"<>|]', '', name).strip()

# --- Main script ---

def main():
    path = os.getcwd()

    # --- YouTube download skipped for test ---
    url = input("Enter YouTube playlist/video URL: ")
    Downloader.downloadPlaylist(url, path)

    # --- MusicBrainz lookup ---
    selected = None
    coverPath = None
    trackList = []

    useBarcode = input("Do you have a barcode for the album? (Yes/No): ")
    if useBarcode.lower() == "yes":
        barcode = input("Enter barcode: ")
        selected = searchReleaseByBarcode(barcode)

    if not selected:
        album_input = input("Enter album name for MusicBrainz search: ")
        artist_input = input("Enter artist name for MusicBrainz search: ")
        releases = searchReleases(artist_input, album_input)
        if releases:
            selected = chooseRelease(releases)

    if selected:
        artist = selected["artist-credit"][0]["name"]
        album = selected["title"]
        year = selected.get("date", "")

        # Request genre
        genre = input("Enter genre: ")

        release_id = selected["id"]

        trackList = getTrackList(release_id)
        renameTracks(path, trackList, artist)
        coverPath = downloadCoverArt(release_id, path)
    else:
        # Manual fallback
        artist = input("Enter the artist name: ")
        album = input("Enter the album name: ")
        genre = input("Enter the genre: ")
        year = input("Enter the year: ")
        files = [f for f in os.listdir(path) if f.lower().endswith(".m4a")]
        trackList = [{"number": i+1, "title": os.path.splitext(f)[0], "filename": f} for i, f in enumerate(files)]

    # --- Add metadata ---
    explicitInput = input("Is this album explicit? (Yes/No): ").strip().lower()
    isExplicit = explicitInput == "yes"
    SongDetailsAdder.addSongDetails(artist, album, genre, year, path, trackList=trackList, coverPath=coverPath, isExplicit=isExplicit)

    # --- Move to album folder ---
    safeAlbumName = sanitizeFileName(album)
    albumFolder = os.path.join(path, safeAlbumName)
    os.makedirs(albumFolder, exist_ok=True)
    for track in trackList:
        src = os.path.join(path, track["filename"])
        dst = os.path.join(albumFolder, track["filename"])
        os.rename(src, dst)
    if coverPath:
        os.rename(coverPath, os.path.join(albumFolder, "cover.jpg"))

    print("All done! Album is ready for iTunes.")

if __name__ == "__main__":
    main()
