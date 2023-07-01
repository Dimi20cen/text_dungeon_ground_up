import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf
from gi.repository import Pango
from game_engine import Game

class FullScreenWidget(Gtk.Overlay):
    def __init__(self):
        super(FullScreenWidget, self).__init__()

        # Loading image and creating pixbuf
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename='background.png', 
                                                         width=Gdk.Screen.width(),
                                                         height=Gdk.Screen.height(), 
                                                         preserve_aspect_ratio=True)
        
        # Creating image and setting pixbuf
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        
        # Creating overlay and packing image
        overlay = Gtk.Overlay()
        overlay.add(img)

        # Create textview and adjust the size30
        textview = Gtk.TextView()
        textview.set_size_request(300, 300)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)
        textview.set_editable(True)

        # Creating textbuffer
        self.textbuffer = textview.get_buffer()
        # game = Game('orig_map.json')
        # game.play()
        # print("lol\n\n\n\n\n")
        text_to_print = "lol"

        self.textbuffer.set_text(text_to_print, -1)

        # Adding the textview to overlay
        overlay.add_overlay(textview)
        overlay.set_overlay_pass_through(textview, False)

        # Set alignment for textview
        textview.set_halign(Gtk.Align.CENTER)
        textview.set_valign(Gtk.Align.CENTER)

        self.add(overlay)
