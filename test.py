import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")

        self.box = Gtk.Box(spacing=10)
        self.add(self.box)

        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textbuffer = self.textview.get_buffer()
        self.textview.connect("key-press-event", self.on_key_press)
        self.box.pack_start(self.textview, True, True, 0)

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_KP_Enter:
            start_iter = self.textbuffer.get_start_iter()
            end_iter = self.textbuffer.get_end_iter()
            text = self.textbuffer.get_text(start_iter, end_iter, True)

            # clear the buffer
            self.textbuffer.set_text('')

            if text.strip() == 'lol':
                self.textbuffer.insert_at_cursor('pog\n')
            elif text.strip() == 'lol1':
                self.textbuffer.insert_at_cursor('pog1\n')

            return True  # stop the event propagation

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
