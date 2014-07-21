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
        # using mpg123 to play music
        # -q(quiet) remove the output in stdout
        # -C(control) enables the keyboard control
        print("Now playing: " + str(self.current_song.artist) + " - " + str(self.current_song.title))
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
