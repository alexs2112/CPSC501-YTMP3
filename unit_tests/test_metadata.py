from application.song import Song
from datetime import datetime
import pytest, os

class TestMetadata:
    @pytest.fixture(autouse=True)
    def handle_test_file(self):
        os.system("copy lofi-chill.mp3 lofi-chill-copy.mp3")
        yield
        os.remove("lofi-chill-copy.mp3")

    def load_song(self):
        song = Song("lofi-chill-copy.mp3", os.getcwd())
        return song

    def test_artist(self):
        song = self.load_song()
        artist = f"Test{datetime.now()}"
        song.set_tag("artist", artist)
        song.save_tags()
        new_artist = song.get_tag("artist")

        assert artist == new_artist
    
    def test_album(self):
        song = self.load_song()
        album = f"Test{datetime.now()}"
        song.set_tag("album", album)
        song.save_tags()
        new_album = song.get_tag("album")

        assert album == new_album

    def test_title(self):
        song = self.load_song()
        title = f"Test{datetime.now()}"
        song.set_tag("title", title)
        song.save_tags()
        new_title = song.get_tag("title")

        assert title == new_title

    def test_track_num(self):
        song = self.load_song()
        track_num = int(datetime.now().strftime("%Y%m%d%H%M%S"))
        song.set_tag("track_num", track_num)
        song.save_tags()
        new_num = song.get_tag("track_num")

        assert track_num == new_num
