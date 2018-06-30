import os

def getIntMsg(msg):
    return (int)(msg.decode("utf-8").split(':')[1])

def get_all_ext_files_of_path(rootdir, ext):
    filenames = []
    for folder, subs, files in os.walk(rootdir):
        for filename in files:
            if filename.endswith("." + ext):
                filenames.append(os.path.join(folder, filename))
    return sorted(filenames, reverse = True)