import tkinter, tkinter.filedialog, os, threading
from application.song import Song
from application.logger import Logger

class Interface:
    METADATA = ["Filename", "Song Name", "Artist", "Album", "Track Number"]

    def __init__(self, songs, start_download_method):
        self.songs = songs
        self.last_artist = ""
        self.last_album = ""
        self.metadata = tkinter.IntVar()
        self.selected_song = tkinter.StringVar()
        self.initialize_colours()
        self.setup(start_download_method)
        self.logger = Logger(self.console)
    
    def initialize_colours(self):
        # http://cs111.wellesley.edu/archive/cs111_fall14/public_html/labs/lab12/tkintercolor.html
        self.colour_background = "DimGray"
        self.colour_foreground = "Silver"
        self.colour_disabled_background = "Gray"

    def setup(self, start_download_method):
        top_frame = tkinter.Frame(bg=self.colour_background)
        top_frame.grid(row=0, column=0)
        self.get_console_frame()

        input_frame = self.get_input_frame(top_frame)
        input_frame_buttons = self.get_input_frame_buttons(input_frame, start_download_method)
        input_frame_buttons.pack()
        input_frame.grid(row=0, column=0)

        right_frame = self.get_right_frame(top_frame)
        song_frame = self.get_song_frame(right_frame)
        self.get_song_frame_buttons(song_frame)
        self.bind_tab_functionality()
        self.get_directory_frame(right_frame)
        right_frame.grid(row=0, column=1)
    
    def get_input_frame(self, top_frame):
        input_frame = self.new_frame(top_frame)

        input_title = tkinter.Label(master=input_frame, text="Youtube URLs:", pady=6, bg=self.colour_background)
        input_title.pack()
        self.song_input = tkinter.Text(master=input_frame, width=30, height=15, bg=self.colour_foreground, undo=True)
        self.song_input.pack()

        return input_frame
    
    def get_input_frame_buttons(self, input_frame, start_download_method):
        input_frame_buttons = self.new_frame(input_frame)
        
        dl_button = tkinter.Button(master=input_frame_buttons, text="Start Download", padx=10, pady=2)
        dl_button.bind("<Button-1>", start_download_method)
        dl_button.grid(row=0, column=0)
        
        enable_metadata_button = tkinter.Checkbutton(master=input_frame_buttons, text="Fill Metadata", padx=10, pady=2, variable=self.metadata, bg=self.colour_background, activebackground=self.colour_background)
        enable_metadata_button.grid(row=0, column=1)
        
        return input_frame_buttons

    def get_right_frame(self, top_frame):
        right_frame = self.new_frame(top_frame)
        return right_frame
    
    def get_song_frame(self, right_frame):
        song_frame = self.new_frame(right_frame)
        song_frame.grid(row=0, column=0, pady=20, sticky="W")

        # SELECT SONG
        select_song_frame = self.new_frame(song_frame)
        select_song_frame.grid(row=0, column=1)
        self.song_options = tkinter.OptionMenu(select_song_frame, self.selected_song, None, [])
        self.song_options.bind("<Configure>", self.select_song)
        self.song_options.pack()

        # SET SONG DETAILS
        field_frame = self.new_frame(song_frame)
        field_frame.grid(row=1, column=0)
        entry_frame = self.new_frame(song_frame)
        entry_frame.grid(row=1, column=1)
        self.get_song_metadata_frames(field_frame, entry_frame)
        self.song_data["Track Number"].bind("<Return>", self.save_and_next_song)

        return song_frame

    def get_song_metadata_frames(self, field_frame, entry_frame):
        self.song_data = {}
        for metadata in Interface.METADATA:
            field = tkinter.Label(master=field_frame, text=f"{metadata}:", padx=10, bg=self.colour_background)
            entry = tkinter.Entry(master=entry_frame, width=25, bg=self.colour_foreground, disabledbackground=self.colour_disabled_background)
            field.pack()
            entry.pack()
            self.song_data[metadata] = entry

    def get_song_frame_buttons(self, song_frame):
        save_song_frame = self.new_frame(song_frame)
        save_song_frame.grid(row=2, column=1)
        save_song_button = tkinter.Button(master=save_song_frame, text="Save Song", padx=20, pady=2)
        save_song_button.bind("<Button-1>", self.save_song)
        save_song_button.pack()

        refresh_songs_frame = self.new_frame(song_frame)
        refresh_songs_frame.grid(row=3, column=1)
        refresh_songs_button = tkinter.Button(master=refresh_songs_frame, text="Refresh Songs", padx=10, pady=2)
        refresh_songs_button.bind("<Button-1>", self.initialize_songs)
        refresh_songs_button.pack()
    
    def bind_tab_functionality(self):
        self.song_data["Filename"].bind("<Return>", lambda _: self.song_data["Song Name"].focus_set())
        self.song_data["Song Name"].bind("<Return>", self.tab_songname)
        self.song_data["Song Name"].bind("<Tab>", self.tab_songname)
        self.song_data["Artist"].bind("<Return>", self.tab_artist)
        self.song_data["Artist"].bind("<Tab>", self.tab_artist)
        self.song_data["Album"].bind("<Return>", self.tab_album)
        self.song_data["Album"].bind("<Tab>", self.tab_album)
    
    def get_console_frame(self):
        bot_frame = tkinter.Frame(bg=self.colour_background)
        bot_frame.grid(row=1, column=0)

        # This console is passed into the Logger object, as it is what prints to it
        self.console = tkinter.Text(master=bot_frame, height=20, bg=self.colour_foreground)
        self.console.pack(fill=tkinter.BOTH, expand=True)
    
    def get_directory_frame(self, right_frame):
        directory_frame = self.new_frame(right_frame)
        directory_frame.grid(row=1, column=0, padx=5)
        directory_text = tkinter.Label(master=directory_frame, text="Directory:", padx=10, bg=self.colour_background)
        directory_text.pack()

        self.directory = tkinter.Entry(master=directory_frame, width=55, bg=self.colour_foreground, disabledbackground=self.colour_disabled_background)
        self.directory.bind("<Return>", self.set_directory)
        self.directory.pack()

        directory_button_frame = tkinter.Frame(master=directory_frame, bg=self.colour_background)
        directory_button_frame.pack()
        directory_button = tkinter.Button(master=directory_button_frame, text="Choose Folder", padx=10, pady=2)
        directory_button.bind("<Button-1>", self.select_directory)
        directory_button.grid(row=0, column=0)
        open_dir_button = tkinter.Button(master=directory_button_frame, text="Open Folder", padx=20, pady=2)
        open_dir_button.bind("<Button-1>", self.open_directory)
        open_dir_button.grid(row=0, column=1)

    def new_frame(self, master):
        return tkinter.Frame(master=master, bg=self.colour_background)

    def tab_songname(self, _):
        self.song_data["Artist"].focus_set()
        if len(self.song_data["Song Name"].get()) == 0:
            path = self.song_data["Filename"].get()
            self.song_data["Song Name"].insert(0, path.rsplit(".mp3")[0].rsplit(".webm")[0].rsplit(".m4a")[0])

    def tab_artist(self, _):
        self.song_data["Album"].focus_set()
        if len(self.song_data["Artist"].get()) == 0 and self.last_artist:
            self.song_data["Artist"].insert(0, self.last_artist)

    def tab_album(self, _):
        self.song_data["Track Number"].focus_set()
        if len(self.song_data["Album"].get()) == 0 and self.last_album:
            self.song_data["Album"].insert(0, self.last_album)
    
    def disable_directory(self):
        self.directory.config(state="disabled")

    def enable_directory(self):
        self.directory.config(state="normal")

    def get_song_input(self):
        return self.song_input.get("1.0", tkinter.END).split('\n')
    
    def get_directory(self):
        return self.directory.get()
    
    def get_metadata(self):
        return self.metadata.get()
    
    def update_songs(self, clear=True):
        menu = self.song_options["menu"]
        menu.delete(0, "end")
        for song in self.songs:
            menu.add_command(label=song, 
                             command=lambda value=song: self.selected_song.set(value))
        if clear:
            self.selected_song.set("")
    
    def add_song(self, song_filename):
        self.song_options["menu"].add_command(label=song_filename, 
                             command=lambda value=song_filename: self.selected_song.set(value))

    def get_selected_song(self):
        if self.selected_song.get() == "":
            return
        try:
            song = Song(self.selected_song.get(), self.get_directory())
        except Exception as e:
            self.logger.error(f"Cannot load {os.path.join(self.get_directory(), self.selected_song.get())}")
            print(e)
            return
        return song
    
    def song_is_mp3(self, song):
        return song.extension == 'mp3'

    def select_song(self, _=None):
        song = self.get_selected_song()
        if song == None: return
        self.clear_song()
        self.song_data["Filename"].insert(0, song.filename)

        if self.song_is_mp3(song):
            self.song_data["Song Name"].insert(0, song.get_tag('title'))
            self.song_data["Artist"].insert(0, song.get_tag('artist'))
            self.song_data["Album"].insert(0, song.get_tag('album'))
            self.song_data["Track Number"].insert(0, song.get_tag('track_num'))
        else:
            for field in Interface.METADATA[1:]:
                self.song_data[field].config(state="disabled")
            self.logger.warning(f"'{song.filename}' is not of mp3 format, setting metadata is disabled.")
        self.song_data["Filename"].focus_set()
    
    def clear_song(self):
        for field in Interface.METADATA:
            self.song_data[field].config(state="normal")
            self.song_data[field].delete(0, tkinter.END)
    
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
    
    def save_song(self, _, clear=True):
        song = self.get_selected_song()
        if song == None: return

        if self.song_is_mp3(song):
            song.set_tag("artist", self.song_data["Artist"].get())
            song.set_tag("album", self.song_data["Album"].get())
            song.set_tag("title", self.song_data["Song Name"].get())
            self.last_artist = self.song_data["Artist"].get()
            self.last_album = self.song_data["Album"].get()

            tracknum = self.song_data["Track Number"].get()
            if tracknum.isnumeric():
                song.set_tag("track_num", tracknum)
            elif tracknum != "":
                self.logger.debug("Only input positive integers for track number.")

            try:
                song.save_tags()
            except Exception as e:
                self.logger.error(e)
                print(e)

        new_fn = self.song_data["Filename"].get()
        if new_fn != self.selected_song.get():
            i = self.songs.index(self.selected_song.get())
            if '.mp3' not in new_fn and '.webm' not in new_fn:
                new_fn += '.mp3'
            self.songs[i] = new_fn
            try:
                os.rename(os.path.join(self.get_directory(), self.selected_song.get()), os.path.join(self.get_directory(), new_fn))
                self.selected_song.set(new_fn)
            except Exception as e:
                print(e)
                self.logger.error(f"Failed to rename {self.selected_song.get()}.mp3")
                self.logger.error("Please refresh.")
        self.logger.debug(f"Song updated successfully!")
        self.update_songs(clear)
        self.clear_song()
    
    def sort_songs(self):
        files = os.listdir(self.get_directory())
        new_songs = []
        for f in files:
            n = f.rsplit('.', 1)
            if len(n) > 1 and (n[1] == "mp3" or n[1] == "webm"):
                new_songs.append(f)

        # If the song loaded is already in songs, leave it there
        all_songs = []
        for song in self.songs:
            if song in new_songs:
                all_songs.append(song)
                new_songs.remove(song)

        # If the song loaded isn't already in songs, append it
        for song in new_songs:
            all_songs.append(song)

        # Sort loaded songs by Artist + Album + Track Number
        all_songs.sort(key=lambda s: Song(s, self.get_directory()).sort_attributes())
        self.songs = all_songs
    
    def initialize_songs(self, _=None):
        self.sort_songs()
        self.logger.debug(f"{len(self.songs)} songs loaded.")
        self.clear_song()
        self.update_songs()
    
    def reset_directory(self):
        self.directory.delete(0, tkinter.END)
        self.directory.insert(0, os.getcwd().replace("\\", "/"))

    def set_directory(self, _):
        self.check_directory()
        self.initialize_songs()

    def select_directory(self, _):
        if threading.active_count() == 1:
            directory = tkinter.filedialog.askdirectory(initialdir=os.getcwd())
            if len(directory) == 0:
                return
            self.directory.delete(0, tkinter.END)
            self.directory.insert(0, directory)
            self.check_directory()
            self.initialize_songs()

    def open_directory(self, _):
        self.check_directory()
        os.startfile(self.get_directory())

    def check_directory(self):
        if not os.path.exists(self.get_directory()):
            self.reset_directory()
            self.logger.error(f"Could not find directory, resetting to default.")
