import tkinter, tkinter.filedialog, threading, os
from application.song import Song
from application.downloader import Downloader, DownloadData
from application.logger import Logger

class Application:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title("Youtube to MP3")
        self.window.resizable(False, False)
        self.last_artist = ""
        self.last_album = ""
        self.songs = []
        self.metadata = tkinter.IntVar()
        self.selected_song = tkinter.StringVar()
        self.initialize_colours()
        self.setup()
        self.logger = Logger(self.console)
        self.downloader = Downloader(self.logger)
        self.window.iconbitmap(self.downloader.executable_path("icon.ico"))
        self.reset_directory()
        self.initialize_songs()
        self.downloader.check_for_ffmpeg()

    def setup(self):
        self.top_frame = tkinter.Frame(bg=self.colour_background)
        self.top_frame.grid(row=0, column=0)

        self.input_frame = tkinter.Frame(master=self.top_frame, bg=self.colour_background)
        self.input_frame.grid(row=0, column=0)

        self.input_title = tkinter.Label(master=self.input_frame, text="Youtube URLs:", pady=6, bg=self.colour_background)
        self.input_title.pack()
        self.song_input = tkinter.Text(master=self.input_frame, width=30, height=15, bg=self.colour_foreground, undo=True)
        self.song_input.pack()

        self.input_frame_buttons = tkinter.Frame(master=self.input_frame, bg=self.colour_background)
        self.input_frame_buttons.pack()
        self.dl_button = tkinter.Button(master=self.input_frame_buttons, text="Start Download", padx=10, pady=2)
        self.dl_button.bind("<Button-1>", self.start_download)
        self.dl_button.grid(row=0, column=0)
        self.enable_metadata_button = tkinter.Checkbutton(master=self.input_frame_buttons, text="Fill Metadata", padx=10, pady=2, variable=self.metadata, bg=self.colour_background, activebackground=self.colour_background)
        self.enable_metadata_button.grid(row=0, column=1)

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
        self.song_songname = tkinter.Entry(master=self.entry_frame, width=25, bg=self.colour_foreground, disabledbackground=self.colour_disabled_background)
        self.field_songname.pack()
        self.song_songname.pack()

        self.field_artist = tkinter.Label(master=self.field_frame, text="Artist:", padx=10, bg=self.colour_background)
        self.song_artist = tkinter.Entry(master=self.entry_frame, width=25, bg=self.colour_foreground, disabledbackground=self.colour_disabled_background)
        self.field_artist.pack()
        self.song_artist.pack()

        self.field_album = tkinter.Label(master=self.field_frame, text="Album:", padx=10, bg=self.colour_background)
        self.song_album = tkinter.Entry(master=self.entry_frame, width=25, bg=self.colour_foreground, disabledbackground=self.colour_disabled_background)
        self.field_album.pack()
        self.song_album.pack()

        self.field_track_num = tkinter.Label(master=self.field_frame, text="Track Number:", padx=10, bg=self.colour_background)
        self.song_track_num = tkinter.Entry(master=self.entry_frame, width=25, bg=self.colour_foreground, disabledbackground=self.colour_disabled_background)
        self.song_track_num.bind("<Return>", self.save_and_next_song)
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

        # This console is passed into the Logger object, as it is what prints to it
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
        self.directory = tkinter.Entry(master=self.directory_frame, width=55, bg=self.colour_foreground, disabledbackground=self.colour_disabled_background)
        self.directory.bind("<Return>", self.set_directory)
        self.directory.pack()
        self.directory_button_frame = tkinter.Frame(master=self.directory_frame, bg=self.colour_background)
        self.directory_button_frame.pack()
        self.directory_button = tkinter.Button(master=self.directory_button_frame, text="Choose Folder", padx=10, pady=2)
        self.directory_button.bind("<Button-1>", self.select_directory)
        self.directory_button.grid(row=0, column=0)
        self.open_dir_button = tkinter.Button(master=self.directory_button_frame, text="Open Folder", padx=20, pady=2)
        self.open_dir_button.bind("<Button-1>", self.open_directory)
        self.open_dir_button.grid(row=0, column=1)

    def tab_songname(self, _):
        self.song_artist.focus_set()
        if len(self.song_songname.get()) == 0:
            path = self.song_filename.get()
            self.song_songname.insert(0, path.rsplit(".mp3")[0].rsplit(".webm")[0].rsplit(".m4a")[0])
    
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
            self.logger.error("Download in progress, please wait...")
            return False
        else:
            return True

    def start_download(self, _):
        if self.check_thread():
            self.logger.debug("Initializing download.")
            self.thread = threading.Thread(target=self.download)
            self.thread.daemon = True
            self.thread.start()

            # Don't allow the user to change the directory while a download is running
            self.directory.config(state="disabled")

    def download(self):
        download_data = DownloadData(
            self.song_input.get("1.0", tkinter.END).split('\n'),
            self.directory.get(),
            self.metadata.get())
        self.downloader.download(
            download_data,
            self.add_song)

        # Reallow users to edit the directory
        self.directory.config(state="normal")

    def initialize_songs(self, _=None):
        self.songs = self.downloader.sort_songs(self.directory.get(), self.songs)
        self.logger.debug(f"{len(self.songs)} songs loaded.")
        self.clear_song()
        self.update_songs()

    def update_songs(self, clear=True):
        menu = self.song_options["menu"]
        menu.delete(0, "end")
        for song in self.songs:
            menu.add_command(label=song, 
                             command=lambda value=song: self.selected_song.set(value))
        if clear:
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
            self.logger.error(f"Cannot load {os.path.join(self.directory.get(), self.selected_song.get())}")
            print(e)
            return
        return song

    def song_is_mp3(self, song):
        return song.extension == 'mp3'

    def select_song(self, _=None):
        song = self.get_selected_song()
        if song == None: return
        self.clear_song()
        self.song_filename.insert(0, song.filename)

        if self.song_is_mp3(song):
            self.song_songname.insert(0, song.get_tag('title'))
            self.song_artist.insert(0, song.get_tag('artist'))
            self.song_album.insert(0, song.get_tag('album'))
            self.song_track_num.insert(0, song.get_tag('track_num'))
        else:
            self.song_songname.config(state="disabled")
            self.song_artist.config(state="disabled")
            self.song_album.config(state="disabled")
            self.song_track_num.config(state="disabled")
            self.logger.warning(f"'{song.filename}' is not of mp3 format, setting metadata is disabled.")
        self.song_filename.focus_set()

    def save_and_next_song(self, _):
        self.save_song(_, False)
        if len(self.songs) == 0:
            self.selected_song.set("")
            return
        song = self.get_selected_song()
        if song == None:
            song = self.songs[0]
        else:
            i = self.songs.index(song.filename)
            if (i >= len(self.songs) - 1):
                self.selected_song.set("")
                return
            song = self.songs[i+1]
        self.selected_song.set(song)
        self.select_song()

    def clear_song(self):
        self.song_songname.config(state="normal")
        self.song_artist.config(state="normal")
        self.song_album.config(state="normal")
        self.song_track_num.config(state="normal")
        self.song_filename.delete(0, tkinter.END)
        self.song_songname.delete(0, tkinter.END)
        self.song_artist.delete(0, tkinter.END)
        self.song_album.delete(0, tkinter.END)
        self.song_track_num.delete(0, tkinter.END)

    def save_song(self, _, clear=True):
        song = self.get_selected_song()
        if song == None: return

        if self.song_is_mp3(song):
            song.set_tag("artist", self.song_artist.get())
            song.set_tag("album", self.song_album.get())
            song.set_tag("title", self.song_songname.get())
            self.last_artist = self.song_artist.get()
            self.last_album = self.song_album.get()

            tracknum = self.song_track_num.get()
            if tracknum.isnumeric():
                song.set_tag("track_num", self.song_track_num.get())
            elif tracknum != "":
                self.logger.debug("Only input positive integers for track number.")

            try:
                song.save_tags()
            except Exception as e:
                self.logger.error(e)
                print(e)

        new_fn = self.song_filename.get()
        if new_fn != self.selected_song.get():
            i = self.songs.index(self.selected_song.get())
            if '.mp3' not in new_fn and '.webm' not in new_fn:
                new_fn += '.mp3'
            self.songs[i] = new_fn
            try:
                os.rename(os.path.join(self.directory.get(), self.selected_song.get()), os.path.join(self.directory.get(), new_fn))
                self.selected_song.set(new_fn)
            except Exception as e:
                print(e)
                self.logger.error(f"Failed to rename {self.selected_song.get()}.mp3")
                self.logger.error("Please refresh.")
        self.logger.debug(f"Song updated successfully!")
        self.update_songs(clear)
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

    def open_directory(self, _):
        self.check_directory()
        os.startfile(self.directory.get())

    def check_directory(self):
        if not os.path.exists(self.directory.get()):
            self.reset_directory()
            self.logger.error(f"Could not find directory, resetting to default.")

    def initialize_colours(self):
        # http://cs111.wellesley.edu/archive/cs111_fall14/public_html/labs/lab12/tkintercolor.html
        self.colour_background = "DimGray"
        self.colour_foreground = "Silver"
        self.colour_disabled_background = "Gray"
        self.window.configure(bg=self.colour_background)

def main():
    app = Application()
    app.start()

if __name__ == "__main__":
    main()
