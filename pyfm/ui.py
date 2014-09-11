import urwid


class ChannelButton(urwid.Button):

    """
    A urwid.Button that can easily change its text 
    """

    def __init__(self, caption):
        super(ChannelButton, self).__init__("")
        self._text = urwid.SelectableIcon([u'\N{BULLET} ', caption], 0)
        self._w = urwid.AttrMap(self._text, None, focus_map='selected')

    @property
    def text(self):
        return self._text.text

    def set_text(self, text):
        self._text.set_text(text)


class ChannelListBox(urwid.ListBox):

    """
    A urwid.ListBox that can control player by emitting signals
    """

    def __init__(self, body):
        super(ChannelListBox, self).__init__(body)
        self._command_map['j'] = 'cursor down'
        self._command_map['k'] = 'cursor up'
        self._command_map['q'] = 'exit'
        self._command_map['Q'] = 'exit'

    def keypress(self, size, key):
        if key in ('up', 'down', 'page up', 'page down', 'enter', 'j', 'k'):
            return super(ChannelListBox, self).keypress(size, key)

        if key in ('q', 'Q'):
            urwid.emit_signal(self, 'exit')

        if key == ('n'):
            urwid.emit_signal(self, 'skip')

        if key == ('l'):
            urwid.emit_signal(self, 'rate')

        if key == ('t'):
            urwid.emit_signal(self, 'trash')
