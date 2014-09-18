import os
import subprocess

from multiprocessing import Process


class Player(object):

    def __init__(self):
        self.is_playing = False
        self.current_song = None
        self.player_process = None
        self.return_code = 0

        proc = subprocess.Popen(
                ["which", "mpg123"], stdout=subprocess.PIPE)
        env_bin_path = proc.communicate()[0].strip()
        if not (env_bin_path and os.path.exists(env_bin_path)):
            print("mpg123 not found. Exit.")
            raise SystemExit()

    def play(self, song):
        self.current_song = song
        # using mpg123 to play the track
        # -q(quiet) remove the output to stdout
        self.player_process = subprocess.Popen(
            ["mpg123", "-q", self.current_song.url])
        self.is_playing = True

    def stop(self):
        if self.player_process is None:
            return
        try:
            self.player_process.terminate()
        except:
            pass
