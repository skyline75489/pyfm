import subprocess
from multiprocessing import Process

class Player:
    def __init__(self):
        self.is_playing = False
        self.current_song = None
        self.player_process = None
        self.return_code = 0
        
    def play(self, song):
        self.current_song = song
        
        print("Now playing: ")
        print("Artist: "+ str(self.current_song.artist))
        print("Title: " + str(self.current_song.title))
        print("Album: " + str(self.current_song.album_title))
        
        # using mpg123 to play the track
        # -q(quiet) remove the output to stdout
        # -C(control) enables the keyboard control
        self.player_process = subprocess.Popen(["mpg123", "-q", "-C", self.current_song.url])
        self.player_process.wait()
        self.return_code = self.player_process.returncode
        self.is_playing = True
        
    def stop(self):
        if self.player_process is None:
            return
        try:
            self.player_process.terminate()
        except:
            pass
