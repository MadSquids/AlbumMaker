import os
from mutagen.mp4 import MP4, MP4Cover

def addSongDetails(folderPath, artist, album, genre, year, trackList, coverPath):
    for track in trackList:
        filename = track.get("filename")
        if not filename:
            continue

        filePath = os.path.join(folderPath, filename)
        if not os.path.exists(filePath):
            print(f"File missing: {filename}")
            continue

        audio = MP4(filePath)
        audio["\xa9ART"] = artist
        audio["\xa9alb"] = album
        audio["\xa9gen"] = genre
        audio["\xa9day"] = year
        audio["\xa9nam"] = track["title"]
        audio["trkn"] = [(track["number"], 0)]

        if track.get("isExplicit", False):
            audio["rtng"] = [1]  # Explicit
        else:
            audio["rtng"] = [0]  # Not explicit

        if coverPath and os.path.exists(coverPath):
            with open(coverPath, "rb") as img:
                audio["covr"] = [MP4Cover(img.read(), imageformat=MP4Cover.FORMAT_JPEG)]

        audio.save()
        print(f"Updated metadata: {track['title']} → track {track['number']}")