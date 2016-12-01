import os
import sys
from mutagen import flac

class DumpError(Exception):
    """Exception raised when we encounter an error when dumping the tracklist.
    """
    pass

def GetFolderName(path_to_folder):
    """Returns the name of the folder as a string.

    Args:
        path_to_folder: string, the path (absolute or relative) to the folder.
    """
    if path_to_folder[-1] == '/':
        return os.path.basename(path_to_folder[:-1])
    return os.path.basename(path_to_folder)

def GetAlbumInfo(path_to_folder):
    """Returns a tuple of album info.

    Elements of the tuple, in order:
        titles: list of strings
        artists: list of strings
        genre: string
    """
    titles = []
    artists = []
    files = sorted([f for f in os.listdir(path_to_folder)
                    if os.path.splitext(f)[1] == '.flac'])

    if len(files) == 0:
        raise DumpError('Found no files in folder: ' + path_to_folder)

    for f in files:
        tags = flac.FLAC(os.path.join(path_to_folder, f))
        titles.append(tags['title'][0])
        artists.append(tags['artist'][0])

    try:
        genre = flac.FLAC(os.path.join(path_to_folder, files[0]))['genre'][0]
    except:
        genre = ''

    return titles, artists, genre

def IsAlbumVariousArtists(artist_list):
    """Returns true if album has more than one main artist."""
    return not all(artist == artist_list[0] for artist in artist_list)

def WriteTracklist(output_path, titles, artists, genre):
    """Writes the tracklist out to a text file.

    Args:
        output_path: string, the path to where to write the output_file.
        titles: list of strings, the title of each track, in order.
        artists: list of strings, the artist of each track, in order.
        genre: string, the genre of the album
    """
    is_va = IsAlbumVariousArtists(artists)

    with open(output_path, 'w') as out_file:
        out_file.write('[u]Tracklist:[/u]\n')

        for i in range(len(titles)):
            line = '{index}. {title}'.format(index=(i + 1), title=titles[i])
            if is_va:
                line += ' - ' + artists[i]
            out_file.write(line + '\n')

        if is_va:
            out_file.write('\n[u]Artists:[/u]\n')
            out_file.write('\n'.join(artists))

        out_file.write('\nGenre:\n\n' + genre)

def DumpTracklist(path_to_folder):
    """Writes the tracklist to a file for an album folder.

    The tracklist is dumped to <path_to_folder>-tracklist.txt. Also, extra
    useful info is included in the file.
    """
    print('Dumping tracklist for: ' + path_to_folder)

    try:
        titles, artists, genre = GetAlbumInfo(path_to_folder)
    except Exception as e:
        print('ERROR: ' + str(e))
        return

    assert len(titles) == len(artists)
    output_path = ((path_to_folder[:-1] + '-tracklist.txt')
                   if path_to_folder[-1] == '/'
                   else path_to_folder + '-tracklist.txt')
    WriteTracklist(output_path, titles, artists, genre)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Incorrect usage; how to run:')
        print('\t$ python3 dump_tracklist.py <path-folder-to-dump>')
        exit()

    for folder_path in sys.argv[1:]:
        if os.path.isdir(folder_path):
            DumpTracklist(folder_path)