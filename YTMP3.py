import tkinter, threading
from application.downloader import Downloader, DownloadData
from application.interface import Interface

class Application:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title("Youtube to MP3")
        self.window.resizable(False, False)
        self.songs = []
        self.interface = Interface(self.songs, self.start_download)
        self.logger = self.interface.logger
        self.downloader = Downloader(self.logger)
        self.window.configure(bg=self.interface.colour_background)
        self.window.iconbitmap(self.downloader.executable_path("icon.ico"))
        self.interface.reset_directory()
        self.interface.initialize_songs()
        self.downloader.check_for_ffmpeg()

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
            self.interface.disable_directory()

    def download(self):
        download_data = DownloadData(
            self.interface.get_song_input(),
            self.interface.get_directory(),
            self.interface.get_metadata())
        self.downloader.download(
            download_data,
            self.add_song)

        # Reallow users to edit the directory
        self.interface.enable_directory()

    def add_song(self, song_filename):
        self.songs.append(song_filename)
        self.interface.add_song(song_filename)

def main():
    app = Application()
    app.start()

if __name__ == "__main__":
    main()
