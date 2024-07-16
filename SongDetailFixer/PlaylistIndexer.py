import os
from mutagen.id3 import ID3, TRCK
from mutagen.mp4 import MP4

def updateTrackNumber(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".mp3") or filename.endswith(".m4a"):
            full_path = os.path.join(directory, filename)

            # Extract the track number from the filename
            track_number, rest = filename.split(" - ", 1)
            track_number = track_number.strip()
            new_filename = rest

            if filename.endswith(".mp3"):
                try:
                    tags = ID3(full_path)
                    tags.add(TRCK(encoding=3, text=track_number))
                    tags.save()
                    #print(f"Track number for {filename} updated to {track_number}.")
                except Exception as e:
                    print(f"Error updating track number for {filename}: {e}")
            elif filename.endswith(".m4a"):
                try:
                    tags = MP4(full_path)
                    tags['trkn'] = [(int(track_number), 0)]  # Track number (tuple of track number and total tracks)
                    tags.save()
                    #print(f"Track number for {filename} updated to {track_number}.")
                except Exception as e:
                    print(f"Error updating track number for {filename}: {e}")

            # Rename the file to remove the "## - " part
            new_full_path = os.path.join(directory, new_filename)
            os.rename(full_path, new_full_path)
            #print(f"Renamed {filename} to {new_filename}.")

if __name__ == "__main__":
    path = os.getcwd()  # Or specify the directory where your music files are located
    updateTrackNumber(path)