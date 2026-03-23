import yt_dlp # type: ignore
import os
import shutil

def downloadPlaylist(url, outputDir):
    """
    Downloads a YouTube playlist or single video to outputDir.
    Converts to M4A, embeds metadata & cover art.
    Fully Windows-safe, no subprocess.
    """

    os.makedirs(outputDir, exist_ok=True)

    useCustom = input("Use custom yt-dlp format? (Y/N): ").strip().lower()

    if useCustom == "y":
        formatString = input("Enter yt-dlp format string (ex: 234 or m4a/bestaudio/best): ").strip()
    else:
        formatString = "m4a/bestaudio/best"  # your default

    ydl_opts = {
        'format': formatString,
        'outtmpl': os.path.join(outputDir, '%(title)s.%(ext)s'),
        'noplaylist': False,  # download full playlist if URL is one
        'ffmpeg_location': shutil.which("ffmpeg"),
        'force_ipv4': True,
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
