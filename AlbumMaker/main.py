import os
import re
import SongDetailsAdder
import Downloader
import musicbrainzMaker as mbMaker
import FileNameRemover as fileNameRemover

def sanitizeFileName(name):
    return re.sub(r'[\\/:*?"<>|]', '', name).strip()

def musicBrainz(path):
    # --- MusicBrainz lookup ---
    artist = album = genre = year = selected = coverPath = None
    trackList = []

    useBarcode = input("Do you have a barcode for the album? (Yes/No): ")
    if useBarcode.lower() == "yes":
        barcode = input("Enter barcode: ")
        selected = mbMaker.searchReleaseByBarcode(barcode)

    if not selected:
        album_input = input("Enter album name for MusicBrainz search: ")
        artist_input = input("Enter artist name for MusicBrainz search: ")
        releases = mbMaker.searchReleases(artist_input, album_input)
        if releases:
            selected = mbMaker.chooseRelease(releases)

    if selected:
        artist = selected["artist-credit"][0]["name"]
        album = selected["title"]
        year = selected.get("date", "")

        # Request genre
        genre = input("Enter genre: ")

        release_id = selected["id"]

        trackList = mbMaker.getTrackList(release_id)
        mbMaker.renameTracks(path, trackList, artist)
        coverPath = mbMaker.downloadCoverArt(release_id, path)
    
    if not selected:
        print("No release selected. Falling back to manual mode.")
        return manual(path)

    return artist, album, genre, year, trackList, coverPath

def manualCoverPath(path):
    coverPath = None
    valid_exts = (".jpg", ".jpeg", ".png")
    for file in os.listdir(path):
        if file.lower().endswith(valid_exts):
            coverPath = os.path.join(path, file)
            print(f"Using cover art: {coverPath}")
            return coverPath
    print("No cover art found in folder.")
    return None

def askExplicitTracks(trackList):
    print("\nTrack List:")
    for t in trackList:
        print(f"{t['number']:02d} - {t['title']}")

    explicit_tracks = input(
        "\nEnter track numbers that are explicit (comma-separated, e.g., 1,3,5), or leave empty if none: "
    )
    explicit_set = set()
    if explicit_tracks.strip():
        for x in explicit_tracks.split(","):
            try:
                num = int(x.strip())
                explicit_set.add(num)
            except ValueError:
                pass  # ignore invalid entries
    return explicit_set

def manualTrackList(path):
    while True:
        files = sorted([f for f in os.listdir(path) if f.lower().endswith(".m4a")])
        useNumbers = input("Do filenames already have track numbers? (Yes/No): ").strip().lower()
        trackList = []

        for i, f in enumerate(files, start=1):
            full_path = os.path.join(path, f)
            name, ext = os.path.splitext(f)

            # Strip leading track number (digits + optional dash/space)
            match = re.match(r'^(\d+)\s*[-.]?\s*(.*)', name)
            if match:
                number = int(match.group(1))
                title = match.group(2).strip()
            else:
                number = 0
                title = name.strip()

            # Clean up multiple spaces and leading/trailing hyphens
            title_clean = re.sub(r'\s+', ' ', title).strip('- ').strip()

            # Rename the file
            new_filename = f"{title_clean}{ext}"
            new_full_path = os.path.join(path, new_filename)
            if full_path != new_full_path:
                os.rename(full_path, new_full_path)

            trackList.append({
                "number": number if useNumbers == "yes" else 0,
                "title": title_clean,
                "filename": os.path.basename(new_full_path)
            })

        if useNumbers == "yes":
            trackList.sort(key=lambda x: x["number"] if x["number"] > 0 else float('inf'))
            for i, track in enumerate(trackList, start=1):
                if track["number"] == 0:
                    track["number"] = i

        print("\nTrack List Preview:")
        for t in trackList:
            num_display = f"{t['number']:02d} - " if t["number"] > 0 else ""
            print(f"{num_display}{t['title']}")

        confirm = input("Is this correct? (Yes/No): ").strip().lower()
        if confirm == "yes":
            return trackList
        print("Let's try again.\n")

def manual(path):
    cleanFileNames = input("Do you want to mass clean the file names? (Yes/No): ").strip().lower()
    if cleanFileNames == "yes":
        fileNameRemover.interactiveClean(path)

    artist = input("Enter the artist name: ")
    album = input("Enter the album name: ")
    genre = input("Enter the genre: ")
    year = input("Enter the year: ")
    coverPath = manualCoverPath(path)
    trackList = manualTrackList(path)

    return artist, album, genre, year, trackList, coverPath

# --- Main script ---

def main():
    path = os.getcwd()

    hasFiles = input("Do you already have the music files? (Yes/No): ")
    if hasFiles.lower() == "no":
        # --- YouTube download skipped for test ---
        url = input("Enter YouTube playlist/video URL: ")
        Downloader.downloadPlaylist(url, path)

    mode = input("Do you want to use musicBrainz to assist in tagging? (Yes/No): ")
    if mode.lower() == "yes":
        tags = musicBrainz(path)
    else:
        tags = manual(path)

    artist = tags[0]
    album = tags[1]
    genre = tags[2]
    year = tags[3]
    trackList = tags[4]
    coverPath = tags[5]

    explicitSet = askExplicitTracks(trackList)

    for track in trackList:
        track["isExplicit"] = track["number"] in explicitSet

    # --- Add metadata ---
    SongDetailsAdder.addSongDetails(path, artist, album, genre, year, trackList, coverPath)

    # --- Move to album folder ---
    safeAlbumName = sanitizeFileName(album)
    albumFolder = os.path.join(path, safeAlbumName)
    os.makedirs(albumFolder, exist_ok=True)
    for track in trackList:
        src = os.path.join(path, track["filename"])
        dst = os.path.join(albumFolder, track["filename"])
        if os.path.exists(dst):
            os.remove(dst)
        os.rename(src, dst)
    if coverPath:
        os.rename(coverPath, os.path.join(albumFolder, "cover.jpg"))

    print("All done! Album is ready for iTunes.")

if __name__ == "__main__":
    main()
