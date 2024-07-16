import os
from mutagen.id3 import ID3, TALB, TPE1, TPE2, TIT2
from mutagen.mp4 import MP4

def addSongDetails(artist, album, path):
    for filename in os.listdir(path):
        if filename.endswith(".mp3"):
            full_path = os.path.join(path, filename)
            try:
                tags = ID3(full_path)
                tags.add(TALB(encoding=3, text=album))
                tags.add(TPE1(encoding=3, text=artist))
                tags.add(TPE2(encoding=3, text=artist))
                title = os.path.splitext(filename)[0]
                tags.add(TIT2(encoding=3, text=title))
                tags.save()
                #print(f"Tags for {filename} updated.")
            except Exception as e:
                print(f"Error updating tags for {filename}: {e}")
        
        elif filename.endswith(".m4a"):
            full_path = os.path.join(path, filename)
            try:
                tags = MP4(full_path)
                tags['\xa9alb'] = album
                tags['\xa9ART'] = artist
                tags['aART'] = artist
                title = os.path.splitext(filename)[0]
                tags['\xa9nam'] = title
                tags.save()
                #print(f"Tags for {filename} updated.")
            except Exception as e:
                print(f"Error updating tags for {filename}: {e}")

if __name__ == "__main__":
    artist = input("Enter the artist name: ")
    album = input("Enter the album name: ")
    path = os.getcwd()
    addSongDetails(artist, album, path)
