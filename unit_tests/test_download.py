import pytest, os
from application.downloader import Downloader, DownloadData

# A logger that doesn't log anything
class Dummy:
    def print(self, _): pass
    def debug(self, _): pass
    def warning(self, _): pass
    def error(self, _): pass

class TestDownload:
    def add_song(self, song):
        return [song]
    
    @pytest.fixture(autouse=True)
    def cleanup_downloads(self):
        self.directory = os.path.join(os.getcwd(), "TestDownload")
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        self.downloader = Downloader(Dummy())

        yield

        for file in os.listdir(self.directory):
            path = os.path.join(self.directory, file)
            os.remove(path)
        os.rmdir(self.directory)

    def test_download(self):
        # More lofi beats
        data = ["https://music.youtube.com/watch?v=MG4vQOtVRMI&si=4vseqt5-SgG4tPbN"]
        download_data = DownloadData(data, self.directory, False)
        self.downloader.download(download_data, self.add_song)

        path = os.path.join(self.directory, "Lofi Chill Beats To Study To.webm")
        assert os.path.exists(path)
    
    def test_playlist(self):
        playlist = "https://music.youtube.com/playlist?list=OLAK5uy_nFcuE_oqLckmXXucm4ZE0bFtFXlDWRWzE&si=iR24ObSkbPiN6Scg"
        songs = self.downloader.get_playlist_songs(playlist)
        expected = \
            ['0hA-Frp2BKY', 
             '9grCvVjUyOw', 
             'pc0asLK383I', 
             'flO0mdO2ods', 
             'Ng-vAaDawXY', 
             'fHRC3Kof1Hk', 
             'zmTRLYEN2GA', 
             'flSF2L8NVlI', 
             'VitG4yx33II', 
             'QjHXEPKv-EE', 
             '_RBgqkwSWMM', 
             'XZNqie7dNvU', 
             'L8rAIk81F6E', 
             '0usdnKRuSFo']
        assert songs == expected

