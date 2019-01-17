import plistlib
import hashlib
from urllib.parse import unquote
from shutil import copyfile
import pathlib
import ntpath
import os.path
from os import listdir
from os.path import isfile, join

FILE_LIBRARY = "<<Path to 'iTunes Library.xml'>>"
DIR_SYNC = "<<Directory to sync>>"
PLAYLIST_NAME = "<<iTunes playlist name>>"

LIBRARY_TRACKS = dict()
SYNC_IDS = []
SYNCED_HASHES = []

def copyFile(original, fileHash):
    fileExt = pathlib.Path(original).suffix
    newFileName = DIR_SYNC + '/' + fileHash + fileExt
    SYNCED_HASHES.append(fileHash + fileExt)
    if (os.path.isfile(newFileName)):
        print("File " + ntpath.basename(newFileName) + " already exists")
    else:
        print("Copy " + ntpath.basename(original) + " to " + ntpath.basename(newFileName))
        copyfile(original, newFileName)

def getFileHash(fileName):
    lim = 5
    blockSize = 65536
    hasher = hashlib.md5()
    with open(fileName, 'rb') as afile:
        buf = afile.read(blockSize)
        while (len(buf) > 0 and lim > 0):
            lim -= 1
            hasher.update(buf)
            buf = afile.read(blockSize)
        return hasher.hexdigest() + hashlib.md5(fileName.encode('utf-8')).hexdigest()

def syncPlaylist():
    i = 0
    for trackId in SYNC_IDS:
        i += 1
        print("[%d/%d] " % (i, len(SYNC_IDS)), end = '')
        k = str(trackId)
        if (k not in LIBRARY_TRACKS):
            print("No file for track id %d" % trackId)
            continue

        trackFileName = LIBRARY_TRACKS[k]
        if (not os.path.isfile(trackFileName)):
            print("File %s does not exist!" % trackFileName)
            continue

        trackFileHash = getFileHash(trackFileName)
        copyFile(trackFileName, trackFileHash)

def deleteUnsynced():
    allFiles = [f for f in listdir(DIR_SYNC) if isfile(join(DIR_SYNC, f))]
    for file in allFiles:
        if(file not in SYNCED_HASHES):
            print("Delete file " + file)
            os.remove(DIR_SYNC + '/' +file)

pList = plistlib.readPlist(FILE_LIBRARY)
tracks = pList['Tracks']
for trackId in tracks:
    trackData = tracks[trackId]
    if ('Location' in trackData):
        LIBRARY_TRACKS[trackId] = unquote(trackData['Location'].replace('file://localhost/', ''))

playlists = pList['Playlists']
for playlist in playlists:
    playlistName = playlist['Name']
    if (playlistName == PLAYLIST_NAME):
        playlistTracks = playlist['Playlist Items']
        for plTrack in playlistTracks:
            plTrackId = plTrack['Track ID']
            if (plTrackId not in SYNC_IDS):
                SYNC_IDS.append(plTrackId)

syncPlaylist()
deleteUnsynced()
