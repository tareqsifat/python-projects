import os

def is_empty_directory_with_files(directory):
    files = []
    directories = []

    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if os.path.isfile(full_path):
            files.append(entry)
        elif os.path.isdir(full_path):
            directories.append(entry)

    return not (bool(files) or bool(directories))

def delete_empty_directory(directory):

    if is_empty_directory_with_files(directory):
        os.rmdir(directory)

if __name__ == '__main__':
    directory = "/home/sifat/for_delete"
    if(delete_empty_directory(directory)):
        print("successfully deleted directory")
    else:
        print("failed to delete directory")