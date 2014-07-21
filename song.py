class Song:
    def __init__(self, song_json):
        self.artist = song_json['artist']
        self.title = song_json['title']
        self.album_title = song_json['albumtitle']
        self.length_in_sec = song_json['length']
        # Process the length of the song
        self.length_minute = divmod(self.length_in_sec, 60)[0]
        self.length_sec = divmod(self.length_in_sec, 60)[1]
        self.length_in_str = str(self.length_minute) + ":" + str(self.length_sec)
        
        self.like = True and song_json['like'] == 1 or False
        self.url = song_json['url']
        self.ssid = song_json['ssid']
        self.sid = song_json['sid']
        self.aid = song_json['aid']        
    
        
