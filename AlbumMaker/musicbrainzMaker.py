import musicbrainzngs # type: ignore
import os
import re
import requests
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