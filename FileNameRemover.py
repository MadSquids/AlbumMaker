import os

def removeStrings(strings_to_remove, directory):
    for filename in os.listdir(directory):
        new_filename = filename
        for remover in strings_to_remove:
            new_filename = new_filename.replace(remover, '')
        
        # Remove whitespace before the file extension
        name, ext = os.path.splitext(new_filename)
        new_filename = f"{name.rstrip()}{ext}"
    
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
        #print(f"Renamed {filename} to {new_filename}.")

def askStrings():
    toRemove = []

    while True:
        remover = input("Enter what you would like to be removed (or type 'quit' to finish): ")
        if remover.lower() == 'quit':
            break
        toRemove.append(remover)

    return toRemove

if __name__ == "__main__":
    path = os.getcwd()
    strings = askStrings()
    removeStrings(strings, path)
