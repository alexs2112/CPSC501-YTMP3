import tkinter, tkinter.filedialog, threading, os, sys, eyed3
from youtube_dl import YoutubeDL

class Song:
    def __init__(self, file, path):
        self.filename = file
        self.file = eyed3.load(os.path.join(path, file))

        self.last_artist = ""
        self.last_album = ""

    def set_tag(self, tag, value):
        if tag == "artist": self.file.tag.artist = value
        elif tag == "album": self.file.tag.album = value
        elif tag == "title": self.file.tag.title = value
        elif tag == "track_num": self.file.tag.track_num = value
        else: raise Exception(f"Unknown song file tag: <{tag}>.")

    def get_tag(self, tag):
        if tag == "artist": v = self.file.tag.artist
        elif tag == "album": v = self.file.tag.album
        elif tag == "title": v = self.file.tag.title
        elif tag == "track_num": v = self.file.tag.track_num[0]
        else: raise Exception(f"Unknown song file tag: <{tag}>.")
        
        if v == None: return ""
        return v

    def save_tags(self):
        self.file.tag.save()

class Application:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title("Youtube to MP3")
        self.window.resizable(False, False)
        self.window.iconbitmap(self.icon_path("icon.ico"))
        self.last_log = None
        self.last_artist = ""
        self.last_album = ""
        self.songs = []
        self.selected_song = tkinter.StringVar()
        self.initialize_colours()
        self.setup()
        self.reset_directory()
        self.initialize_songs()

    def setup(self):
        self.top_frame = tkinter.Frame(bg=self.colour_background)
        self.top_frame.grid(row=0, column=0)

        self.input_frame = tkinter.Frame(master=self.top_frame, bg=self.colour_background)
        self.input_frame.grid(row=0, column=0)

        self.input_title = tkinter.Label(master=self.input_frame, text="Youtube URLs:", pady=6, bg=self.colour_background)
        self.input_title.grid(row=0, column=0)
        self.song_input = tkinter.Text(master=self.input_frame, width=30, height=15, bg=self.colour_foreground, undo=True)
        self.song_input.grid(row=1, column=0)

        self.dl_button = tkinter.Button(master=self.input_frame, text="Start Download...", padx=10, pady=2)
        self.dl_button.bind("<Button-1>", self.start_download)
        self.dl_button.grid(row=2, column=0)

        self.right_frame = tkinter.Frame(master=self.top_frame, bg=self.colour_background)
        self.right_frame.grid(row=0, column=1)
        self.song_frame = tkinter.Frame(master=self.right_frame, bg=self.colour_background)
        self.song_frame.grid(row=0, column=0, pady=20, sticky="W")

        # SELECT SONG
        self.select_song_frame = tkinter.Frame(master=self.song_frame, bg=self.colour_background)
        self.select_song_frame.grid(row=0, column=1)
        self.song_options = tkinter.OptionMenu(self.select_song_frame, self.selected_song, None, [])
        self.song_options.bind("<Configure>", self.select_song)
        self.song_options.pack()

        # SET SONG DETAILS
        self.field_frame = tkinter.Frame(master=self.song_frame, bg=self.colour_background)
        self.field_frame.grid(row=1, column=0)

        self.entry_frame = tkinter.Frame(master=self.song_frame, bg=self.colour_background)
        self.entry_frame.grid(row=1, column=1)

        self.field_filename = tkinter.Label(master=self.field_frame, text="Filename:", padx=10, bg=self.colour_background)
        self.song_filename = tkinter.Entry(master=self.entry_frame, width=25, bg=self.colour_foreground)
        self.field_filename.pack()
        self.song_filename.pack()

        self.field_songname = tkinter.Label(master=self.field_frame, text="Song Name:", padx=10, bg=self.colour_background)
        self.song_songname = tkinter.Entry(master=self.entry_frame, width=25, bg=self.colour_foreground)
        self.field_songname.pack()
        self.song_songname.pack()

        self.field_artist = tkinter.Label(master=self.field_frame, text="Artist:", padx=10, bg=self.colour_background)
        self.song_artist = tkinter.Entry(master=self.entry_frame, width=25, bg=self.colour_foreground)
        self.field_artist.pack()
        self.song_artist.pack()

        self.field_album = tkinter.Label(master=self.field_frame, text="Album:", padx=10, bg=self.colour_background)
        self.song_album = tkinter.Entry(master=self.entry_frame, width=25, bg=self.colour_foreground)
        self.field_album.pack()
        self.song_album.pack()

        self.field_track_num = tkinter.Label(master=self.field_frame, text="Track Number:", padx=10, bg=self.colour_background)
        self.song_track_num = tkinter.Entry(master=self.entry_frame, width=25, bg=self.colour_foreground)
        self.song_track_num.bind("<Return>", self.save_song)
        self.field_track_num.pack()
        self.song_track_num.pack()

        self.save_song_frame = tkinter.Frame(master=self.song_frame, bg=self.colour_background)
        self.save_song_frame.grid(row=2, column=1)
        self.save_song_button = tkinter.Button(master=self.save_song_frame, text="Save Song", padx=20, pady=2)
        self.save_song_button.bind("<Button-1>", self.save_song)
        self.save_song_button.pack()

        self.refresh_songs_frame = tkinter.Frame(master=self.song_frame, bg=self.colour_background)
        self.refresh_songs_frame.grid(row=3, column=1)
        self.refresh_songs_button = tkinter.Button(master=self.refresh_songs_frame, text="Refresh Songs", padx=10, pady=2)
        self.refresh_songs_button.bind("<Button-1>", self.initialize_songs)
        self.refresh_songs_button.pack()

        self.bot_frame = tkinter.Frame(bg=self.colour_background)
        self.bot_frame.grid(row=1, column=0)
        self.console = tkinter.Text(master=self.bot_frame, height=20, bg=self.colour_foreground)
        self.console.pack(fill=tkinter.BOTH, expand=True)

        # Pressing ENTER on the entry fields go to the next field and auto populate if needed
        self.song_filename.bind("<Return>", lambda _: self.song_songname.focus_set())
        self.song_songname.bind("<Return>", self.tab_songname)
        self.song_songname.bind("<Tab>", self.tab_songname)
        self.song_artist.bind("<Return>", self.tab_artist)
        self.song_artist.bind("<Tab>", self.tab_artist)
        self.song_album.bind("<Return>", self.tab_album)
        self.song_album.bind("<Tab>", self.tab_album)

        # SET DIRECTORY
        self.directory_frame = tkinter.Frame(master=self.right_frame, bg=self.colour_background)
        self.directory_frame.grid(row=1, column=0, padx=5)
        self.directory_text = tkinter.Label(master=self.directory_frame, text="Directory:", padx=10, bg=self.colour_background)
        self.directory_text.pack()
        self.directory = tkinter.Entry(master=self.directory_frame, width=55, bg=self.colour_foreground)
        self.directory.bind("<Return>", self.set_directory)
        self.directory.pack()
        self.directory_button = tkinter.Button(master=self.directory_frame, text="Choose Folder", padx=10, pady=2)
        self.directory_button.bind("<Button-1>", self.select_directory)
        self.directory_button.pack()

    def tab_songname(self, _):
        self.song_artist.focus_set()
        if len(self.song_songname.get()) == 0:
            path = self.song_filename.get()
            self.song_songname.insert(0, path.rsplit(".mp3")[0])
    
    def tab_artist(self, _):
        self.song_album.focus_set()
        if len(self.song_artist.get()) == 0 and self.last_artist:
            self.song_artist.insert(0, self.last_artist)
    
    def tab_album(self, _):
        self.song_track_num.focus_set()
        if len(self.song_album.get()) == 0 and self.last_album:
            self.song_album.insert(0, self.last_album)

    def start(self):
        self.window.mainloop()
    
    def check_thread(self):
        if threading.active_count() > 1:
            self.error("Download in progress, please wait...")
            return False
        else:
            return True

    def start_download(self, _):
        if self.check_thread():
            self.debug("Initializing download.")
            self.thread = threading.Thread(target=self.download)
            self.thread.daemon = True
            self.thread.start()

            # Don't allow the user to change the directory while a download is running
            self.directory.config(state="disabled")

    def download(self):
        data = self.song_input.get("1.0", tkinter.END).split('\n')
        songs = []
        for link in data:
            if "youtu.be" in link:
                songs.append(link)
            elif "playlist" in link:
                ids = self.get_playlist_songs(link)
                for id in ids:
                    songs.append(f"https://youtu.be/{id}")
            elif "www.youtube.com" in link:
                video_code = link.split("?v=")
                if len(video_code) == 2:
                    code = video_code[1].split("&")[0]
                    songs.append(f"https://youtu.be/{code}")
                else:
                    self.error(f"Could not split {link} by '?v='")

        if (len(songs) == 0):
            self.error("No songs to download")
            return

        audio = YoutubeDL({
            "format": "bestaudio",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "outtmpl": f"{self.directory.get()}\\%(title)s.%(ext)s",
            "logger": self
        })

        failed = []
        for i in range(len(songs)):
            url = songs[i]
            try:
                data = audio.extract_info(url)
                title = f"{data['title']}.mp3"  # data['ext'] returns m4a
                self.add_song(title)
            except Exception as e:
                print(e)
                failed.append(i)
                continue

        if len(failed) > 0:
            self.error(f"\n{str(len(failed))} Failures Detected")    
            for i in failed:
                self.print(songs[i])

        self.print(f"\nDownload Complete!\nFiles located at {self.directory.get()}\n")

        # Reallow users to edit the directory
        self.directory.config(state="normal")

    def get_playlist_songs(self, url):
        out = []
        download = YoutubeDL({"simulate": True, "quiet": True})
        self.debug("Downloading playlist data.")
        try:
            with download:
                data = download.extract_info(url, download=False)
                if 'entries' in data:
                    video = data['entries']
                    for i, _ in enumerate(video):
                        out.append(data['entries'][i]['id'])
        except Exception as e:
            self.error("Could not retrieve playlist data.")
            print(e)
        self.debug(f"Found {str(len(out))} songs.")
        return out

    def initialize_songs(self, _=None):
        files = os.listdir(self.directory.get())
        new_songs = []
        for f in files:
            n = f.rsplit('.', 1)
            if len(n) > 1 and n[1] == "mp3":
                new_songs.append(f)

        # If the song loaded is already in songs, leave it there
        new_new_songs = []
        for song in self.songs:
            if song in new_songs:
                new_new_songs.append(song)
                new_songs.remove(song)

        # If the song loaded isn't already in songs, append it
        for song in new_songs:
            new_new_songs.append(song)
        self.songs = new_new_songs

        self.debug(f"{len(self.songs)} songs loaded.")
        self.clear_song()
        self.update_songs()

    def update_songs(self):
        menu = self.song_options["menu"]
        menu.delete(0, "end")
        for song in self.songs:
            menu.add_command(label=song, 
                             command=lambda value=song: self.selected_song.set(value))
        self.selected_song.set("")

    def add_song(self, song_filename):
        self.songs.append(song_filename)
        self.song_options["menu"].add_command(label=song_filename, 
                             command=lambda value=song_filename: self.selected_song.set(value))

    def get_selected_song(self):
        if self.selected_song.get() == "":
            return
        try:
            song = Song(self.selected_song.get(), self.directory.get())
        except Exception as e:
            self.error(f"Cannot load {os.path.join(self.directory.get(), self.selected_song.get())}")
            print(e)
            return
        return song

    def select_song(self, _):
        song = self.get_selected_song()
        if song == None: return
        self.clear_song()
        self.song_filename.insert(0, song.filename)
        self.song_songname.insert(0, song.get_tag('title'))
        self.song_artist.insert(0, song.get_tag('artist'))
        self.song_album.insert(0, song.get_tag('album'))
        self.song_track_num.insert(0, song.get_tag('track_num'))
        self.song_filename.focus_set()

    def clear_song(self):
        self.song_filename.delete(0, tkinter.END)
        self.song_songname.delete(0, tkinter.END)
        self.song_artist.delete(0, tkinter.END)
        self.song_album.delete(0, tkinter.END)
        self.song_track_num.delete(0, tkinter.END)

    def save_song(self, _):
        song = self.get_selected_song()
        if song == None: return

        song.set_tag("artist", self.song_artist.get())
        song.set_tag("album", self.song_album.get())
        song.set_tag("title", self.song_songname.get())
        self.last_artist = self.song_artist.get()
        self.last_album = self.song_album.get()

        tracknum = self.song_track_num.get()
        if tracknum.isnumeric():
            song.set_tag("track_num", self.song_track_num.get())
        elif tracknum != "":
            self.debug("Only input positive integers for track number.")

        try:
            song.save_tags()
        except Exception as e:
            self.error(e)
            print(e)
            return

        new_fn = self.song_filename.get()
        if new_fn != self.selected_song.get():
            i = self.songs.index(self.selected_song.get())
            if '.mp3' not in new_fn:
                new_fn += '.mp3'
            self.songs[i] = new_fn
            try:
                os.rename(os.path.join(self.directory.get(), self.selected_song.get()), os.path.join(self.directory.get(), new_fn))
            except Exception as e:
                print(e)
                self.error(f"Failed to rename {self.selected_song.get()}.mp3")
                self.error("Please refresh.")
        self.debug(f"Song updated successfully!")
        self.update_songs()
        self.clear_song()
    
    def reset_directory(self):
        self.directory.delete(0, tkinter.END)
        self.directory.insert(0, os.getcwd().replace("\\", "/"))

    def set_directory(self, _):
        self.check_directory()
        self.initialize_songs()

    def select_directory(self, _):
        if self.check_thread():
            directory = tkinter.filedialog.askdirectory(initialdir=os.getcwd())
            if len(directory) == 0:
                return
            self.directory.delete(0, tkinter.END)
            self.directory.insert(0, directory)
            self.check_directory()
            self.initialize_songs()

    def check_directory(self):
        if not os.path.exists(self.directory.get()):
            self.reset_directory()
            self.error(f"Could not find directory, resetting to default.")

    def icon_path(self, path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath("resources/")

        return os.path.join(base_path, path)

    def initialize_colours(self):
        self.colour_background = "DimGray"
        self.colour_foreground = "Silver"
        self.window.configure(bg=self.colour_background)

    # Some logging methods
    def print(self, msg):
        if self.last_log != None:
            msg = "\n" + msg
        self.console.insert(tkinter.END, msg)
        self.console.see(tkinter.END)
        self.last_log = msg
    def debug(self, msg):
        msg.strip()

        # Extra handling to pretty up the output and stop downloads from flooding the console
        if "[download]" in msg and "[download]" in self.last_log and "Destination" not in self.last_log:
            last = self.console.index("end-1c linestart")
            self.console.delete(last, tkinter.END)

        self.print(msg if "[" in msg else f"[debug]: {msg}")
    def warning(self, msg):
        self.print(f"[warning]: {msg}")
    def error(self, msg):
        self.print(f"[error]: {msg}")

def main():
    app = Application()
    app.start()

if __name__ == "__main__":
    main()
