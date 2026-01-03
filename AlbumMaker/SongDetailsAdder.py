import os
from mutagen.mp4 import MP4, MP4Cover

def addSongDetails(artist, album, genre, year, folderPath, trackList, coverPath=None):
    """
    Update metadata for all .m4a files using MusicBrainz track numbers.
    trackList: [{"number": 1, "title": "Song Name", "filename": "DownloadedFile.m4a"}]
    """
    for idx, track in enumerate(trackList):
        filename = track.get("filename")
        if not filename:
            continue  # skip missing files

        filePath = os.path.join(folderPath, filename)
        if not os.path.exists(filePath):
            print(f"File missing: {filename}")
            continue

        audio = MP4(filePath)

        # Metadata
        audio["\xa9ART"] = artist
        audio["\xa9alb"] = album
        audio["\xa9gen"] = genre
        audio["\xa9day"] = year
        audio["\xa9nam"] = track["title"]  # clean title
        audio["trkn"] = [(track["number"], 0)]  # MusicBrainz track number

        # Embed cover art
        if coverPath and os.path.exists(coverPath):
            with open(coverPath, "rb") as img:
                audio["covr"] = [MP4Cover(img.read(), imageformat=MP4Cover.FORMAT_JPEG)]

        audio.save()
        print(f"Updated metadata: {track['title']} → track {track['number']}")
