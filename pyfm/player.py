import os
import subprocess


class Player(object):

    def __init__(self):
        self.is_playing = False
        self.current_song = None
        self.player_process = None
        self.return_code = 0
        self.detect_external_players()

    def detect_external_players(self):
        supported_external_players = [
            ["mpv", "--really-quiet"],
            ["mplayer", "-really-quiet"],
            ["mpg123", "-q"],
        ]

        for external_player in supported_external_players:
            proc = subprocess.Popen(
                    ["which", external_player[0]], stdout=subprocess.PIPE)
            env_bin_path = proc.communicate()[0].strip()
            if (env_bin_path and os.path.exists(env_bin_path)):
                self.external_player = external_player
                break

        else:
            print("no supported player found. Exit.")
            raise SystemExit()

    def play(self, song):
        self.current_song = song
        self.player_process = subprocess.Popen(
            self.external_player + [self.current_song.url],
            stdin=subprocess.PIPE)
        self.is_playing = True

    def stop(self):
        if self.player_process is None:
            return
        try:
            self.player_process.terminate()
        except:
            pass
