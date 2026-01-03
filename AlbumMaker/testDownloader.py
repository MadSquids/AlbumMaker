import os
import Downloader

testDir = os.path.join(os.getcwd(), "testDownload")
os.makedirs(testDir, exist_ok=True)

testUrl = "https://www.youtube.com/watch?v=QJJYpsA5tv8"
Downloader.downloadPlaylist(testUrl, testDir)
