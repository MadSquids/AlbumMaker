# AlbumMaker
 
A Python-based program to quickly and easily edit the metadata, and clean up filenames for mp3 and m4a files.\
Designed to be used on albums.
## Features include:
 - Adding playlist track number. 

 - Mass removal of filename bloat.

 - Adding Album, Artist, and Title metadata to the files.

 - Packing all the .mp3 and .m4a files into a new folder named after the album.

## Usage:
Place the AlbumMaker.exe file in the same folder as the songs you want to add the metadata to.\
Launch the .exe and follow the instructions in the command prompt.

### Playlist Track Number
To add playlist track numbers please have your files named in the following format.\
(filename format required "[tracknumber] - [rest of filename]") Example 01 - Killer Queen.m4a\
Will auto-remove the track number from the filename upon adding it to the metadata.

### Remove Filename Bloat
The program will ask what bloat you want to remove. Type quit to signify all bloat has been given to the program.\
For example, if your files have (Official Audio) you can add that as a bloat word and it will remove that from all the files.\
As well as removing leading and trailing spaces in the filename.

## Compatibility:
The .exe file will only work on Windows. The source code is included if you want to compile it for Mac or Linux. AlbumMaker.py is the main file that calls the other 3.
Additionally, you can use the other 3 Python files individually allowing for more specific use cases.
	
