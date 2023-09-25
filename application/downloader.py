import os, sys
from application.song import Song
from yt_dlp import YoutubeDL

class Downloader:
    def executable_path(self, path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath("resources/")

        return os.path.join(base_path, path)
    
    def check_for_ffmpeg(self, application):
        ffmpeg = self.executable_path("ffmpeg.exe")
        if (os.path.exists(ffmpeg)):
            return True
        else:
            application.warning("ffmpeg not found, files will not be converted to mp3 format.")
            return False
    
    def sort_songs(self, directory, songs):
        files = os.listdir(directory)
        new_songs = []
        for f in files:
            n = f.rsplit('.', 1)
            if len(n) > 1 and (n[1] == "mp3" or n[1] == "webm"):
                new_songs.append(f)

        # If the song loaded is already in songs, leave it there
        all_songs = []
        for song in songs:
            if song in new_songs:
                all_songs.append(song)
                new_songs.remove(song)

        # If the song loaded isn't already in songs, append it
        for song in new_songs:
            all_songs.append(song)

        # Sort loaded songs by Artist + Album + Track Number
        all_songs.sort(key=lambda s: Song(s, directory).sort_attributes())
        return all_songs
    
    def get_playlist_songs(self, application, url):
        out = []
        download = YoutubeDL({"simulate": True, "quiet": True})
        application.debug("Downloading playlist data.")
        try:
            with download:
                data = download.extract_info(url, download=False)
                if 'entries' in data:
                    video = data['entries']
                    for i, _ in enumerate(video):
                        out.append(data['entries'][i]['id'])
        except Exception as e:
            application.error("Could not retrieve playlist data.")
            print(e)
        application.debug(f"Found {str(len(out))} songs.")
        return out

    def get_downloader(self, application, directory, embed_metadata):
        # Convert to mp3 if ffmpeg is available, otherwise leave as is
        if (self.check_for_ffmpeg(application)):
            postprocessors = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
            if embed_metadata: postprocessors.append({
                "key": "FFmpegMetadata",
                "add_metadata": True
            })
            audio = YoutubeDL({
                "format": "bestaudio",
                "postprocessors": postprocessors,
                "ffmpeg_location": self.executable_path("ffmpeg.exe"),
                "outtmpl": f"{directory}\\%(title)s.%(ext)s",
                "logger": application
            })
        else:
            audio = YoutubeDL({
                "format": "bestaudio",
                "outtmpl": f"{directory}\\%(title)s.%(ext)s",
                "logger": application
            })
        return audio

    def download(self, application, data, directory, add_metadata):
        songs = []
        for link in data:
            if "youtu.be" in link:
                songs.append(link)
            elif "playlist" in link:
                ids = self.get_playlist_songs(application, link)
                for id in ids:
                    songs.append(f"https://youtu.be/{id}")
            elif "music.youtube" in link:
                songs.append(link)
            elif "www.youtube.com" in link:
                video_code = link.split("?v=")
                if len(video_code) == 2:
                    code = video_code[1].split("&")[0]
                    songs.append(f"https://youtu.be/{code}")
                else:
                    application.error(f"Could not split {link} by '?v='")
            elif len(link.strip()) > 0:
                application.error(f"Could not read {link}, skipping.")

        if (len(songs) == 0):
            application.error("No songs to download")
            return

        audio = self.get_downloader(application, directory, add_metadata)
        failed = []
        for i in range(len(songs)):
            url = songs[i]
            try:
                data = audio.extract_info(url)
                try:
                    filepath = data['requested_downloads'][0]['filepath']
                    title = os.path.basename(filepath)
                except Exception as e:
                    # The video title is not accurate to the filename, this may break
                    # yt-dlp replaces certain punctuation marks to make them windows safe
                    title = f"{data['title']}.mp3"  # data['ext'] returns m4a

                application.add_song(title)
            except Exception as e:
                print(e)
                failed.append(i)
                continue

        if len(failed) > 0:
            application.error(f"\n{str(len(failed))} Failures Detected")    
            for i in failed:
                application.print(songs[i])

        application.print(f"\nDownload Complete!\nFiles located at {directory}\n")
