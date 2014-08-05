'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import xbmc
import xbmcaddon
from time import sleep
import json


ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
FOLDER = ADDON.getSetting('autoresume.save.folder').encode('utf-8', 'ignore')
FREQUENCY = int(ADDON.getSetting('autoresume.frequency'))
PATH = os.path.join(FOLDER, 'autoresume.txt')


def json_query(query):
    xbmc_request = json.dumps(query)
    result = xbmc.executeJSONRPC(xbmc_request)
    result = unicode(result, 'utf-8', errors='ignore')
    return json.loads(result)


def get_playlist():
  get_video_playlist_contents = {"jsonrpc":"2.0", "id":1, "method":"Playlist.GetItems","params":{"playlistid":1,"properties":["file"]}}
  res = json_query(get_video_playlist_contents)
  if res.get('result',False):
    if res['result'].get('items',False):
      items = []
      for i in res['result']['items']:
        items.append((i['id'],i['file']))
      items.sort()
      return 'video_-|-_' + '_-|-_'.join([x[1] for x in items])

  get_music_playlist_contents = {"jsonrpc":"2.0", "id":1, "method":"Playlist.GetItems","params":{"playlistid":0,"properties":["file"]}}
  res = json_query(get_music_playlist_contents)
  if res.get('result',False):
    if res['result'].get('items',False):
      items = []
      for i in res['result']['items']:
        items.append((i['id'],i['file']))
      items.sort()
      return 'music_-|-_' + '_-|-_'.join([x[1] for x in items])  

  return ''


def resume():
  for x in range(0,120):
    if os.path.exists(FOLDER):
      if os.path.exists(PATH):
        # Read from autoresume.txt.
        with open(PATH, 'r') as f:
          mediaFile = f.readline().rstrip('\n')
          position = float(f.readline())
          try:
            playlist = f.readline().split('_-|-_')
          except:
            playlist = []

        # load playlist contents
        if playlist:
          add_this = {'jsonrpc': '2.0','id': 1, "method": 'Playlist.Add', "params": {'item' : {'file' : 'placeholder' }, 'playlistid' : 'placeholder'}}

          if playlist[0] == 'music':
            add_this['params']['playlistid'] = 0
          else:
            add_this['params']['playlistid'] = 1
          
          for x in playlist[1:]:
            add_this['params']['item']['file'] = x
            json_query(add_this)

          try:
            playlist_position = playlist.index(mediaFile) - 1
          except:
            playlist_position = 0

          xbmc.Player().play(xbmc.PlayList(add_this['params']['playlistid']), startpos=playlist_position)

        else:
          # Play file.
          xbmc.Player().play(mediaFile)

        while (not xbmc.Player().isPlaying()):
          sleep(0.5)
        sleep(1)
        # Seek to last recorded position.
        xbmc.Player().seekTime(position)
        sleep(1)
        # Make sure it actually got there.
        if abs(position - xbmc.Player().getTime()) > 30:
          xbmc.Player().seekTime(position)
      break
    else:
      # If the folder didn't exist maybe we need to wait longer for the drive to be mounted.
      sleep(5)


def recordPosition():
  if xbmc.Player().isPlaying():
    mediaFile = xbmc.Player().getPlayingFile()
    position = xbmc.Player().getTime()
    playlist = get_playlist()
    # Write info to file
    with open(PATH, 'w') as f:
      f.write(mediaFile)
      f.write('\n')
      f.write(repr(position))
      f.write('\n')
      f.write(playlist)

def log(msg):
  xbmc.log("%s: %s" % (ADDON_ID, msg), xbmc.LOGDEBUG)


if __name__ == "__main__":
  resume()
  while (not xbmc.abortRequested):
    recordPosition()
    sleep(FREQUENCY)

