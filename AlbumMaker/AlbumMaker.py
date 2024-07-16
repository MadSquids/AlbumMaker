import os
import shutil
import time
import PlaylistIndexer
import FileNameRemover
import SongDetailsAdder

def main():
    # Get current working directory
    path = os.getcwd()
    
    # Run PlaylistIndexer.py
    PlaylistIndexer.updateTrackNumber(path)
    
    # Run FileNameRemover.py
    stringsRemove = FileNameRemover.askStrings()
    FileNameRemover.removeStrings(stringsRemove, path)
    
    # Ask for artist and album name.
    artist = input("Enter the artist name: ")
    album = input("Enter the album name: ")
    genre = input("Enter the genre: ")
    year = input("Enter the year: ")
    
    # Run SongDetailsAdder.py
    SongDetailsAdder.addSongDetails(artist, album, genre, year, path)

    # Creat a new folder named after the album
    albumFolder = os.path.join(path, album)
    if not os.path.exists(albumFolder):
        os.makedirs(albumFolder)
    
    # Move all the songs into the new folder
    for filename in os.listdir(path):
        if filename.endswith(".mp3") or filename.endswith(".m4a"):
            shutil.move(os.path.join(path, filename), os.path.join(albumFolder, filename))
            #print(f"Moved {filename} to {albumFolder}")

    print("DONE!")
    time.sleep(5)

if __name__ == "__main__":
    main()
