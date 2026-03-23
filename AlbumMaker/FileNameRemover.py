import os
import re

AUDIO_EXTS = (".m4a", ".mp3", ".flac", ".wav", ".aac", ".ogg")

COMMON_JUNK = [
    "[Official Video]",
    "(Official Video)",
    "[Official Audio]",
    "(Official Audio)",
    "[Lyrics]",
    "(Lyrics)",
    "[HD]",
    "(HD)",
    "[4K]",
    "(4K)",
    "Official Video",
    "Official Audio",
    "Lyrics Video",
    "(Official Lyric Video)",
    "(Lyric Visualiser)",
    "(Official Visualiser)",
    "[Official Visualiser]",
]

def clean_filename(filename, strings_to_remove):
    new_filename = filename

    # Remove unwanted strings
    for remover in strings_to_remove:
        new_filename = new_filename.replace(remover, "")

    name, ext = os.path.splitext(new_filename)

    # --- NEW CLEANING LOGIC ---

    # Collapse multiple spaces into one
    name = re.sub(r'\s+', ' ', name)

    # Remove leading/trailing dashes, underscores, spaces
    name = name.strip(" -_")

    # Final safety strip
    name = name.strip()

    if not name:
        name = "Unknown Track"

    new_filename = f"{name}{ext}"

    return new_filename


def interactiveClean(directory):
    print("\n--- Live Filename Cleaner ---")
    print("Type text to remove from filenames.")
    print("Type 'common' to remove common junk.")
    print("Type 'quit' to finish.\n")

    while True:
        remover = input("Remove string: ").strip()

        if remover.lower() == "quit":
            break

        if remover.lower() == "common":
            strings_to_remove = COMMON_JUNK
            print("\nUsing common junk removal list...\n")
        elif remover:
            strings_to_remove = [remover]
        else:
            continue

        preview_changes = []

        # --- PREVIEW ---
        for filename in os.listdir(directory):
            if not filename.lower().endswith(AUDIO_EXTS):
                continue

            new_filename = clean_filename(filename, strings_to_remove)

            if filename != new_filename:
                preview_changes.append((filename, new_filename))

        if not preview_changes:
            print("No changes would be made.\n")
            continue

        print("\n--- Preview ---")
        for old, new in preview_changes:
            print(f"{old}  →  {new}")

        confirm = input("\nApply these changes? (Y/N): ").strip().lower()
        if confirm != "y":
            print("Skipped.\n")
            continue

        # --- APPLY ---
        for old, new in preview_changes:
            src = os.path.join(directory, old)
            dst = os.path.join(directory, new)

            if os.path.exists(dst):
                print(f"Skipping (exists): {new}")
                continue

            os.rename(src, dst)

        print("\n--- Changes applied ---\n")


if __name__ == "__main__":
    path = os.getcwd()
    interactiveClean(path)