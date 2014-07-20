import subprocess
from multiprocessing import Process

class Player:
    def __init__(self):
        self.is_playing = False
        self.current_song = None
        self.return_code = None
        
    def play(self, song):
        self.current_song = song
        # using mpg123 to play music, -q(quiet) to remove the output in stdout
        print("Now playing: " + str(self.current_song.artist) + " - " + str(self.current_song.title))
        self.return_code = subprocess.call(["mpg123", "-q", "-C", self.current_song.url])
        self.is_playing = True
        
    def stop(self):
        if self.player_process is None:
            return
            
        try:
            self.player_process.terminate()
        except:
            pass
