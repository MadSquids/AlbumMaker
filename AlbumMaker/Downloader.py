import yt_dlp
import os

def downloadPlaylist(url, outputDir):
    """
    Downloads a YouTube playlist or single video to outputDir.
    Converts to M4A, embeds metadata & cover art.
    Fully Windows-safe, no subprocess.
    """

    os.makedirs(outputDir, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(outputDir, '%(title)s.%(ext)s'),
        'noplaylist': False,  # download full playlist if URL is one
        'postprocessors': [
            {   # Extract audio
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                'preferredquality': '0',
            },
            {   # Embed metadata
                'key': 'FFmpegMetadata',
            },
            {   # Embed thumbnail
                'key': 'EmbedThumbnail',
            }
        ],
        'quiet': False,
        'no_warnings': False,
    }

    print(f"Downloading to {outputDir} ...\n")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print("yt-dlp ERROR:", e)
        raise

    print("\nDownload complete!\n")
