#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Gtk

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.graphics.radiotoolbutton import RadioToolButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.activity.widgets import StopButton
from gettext import gettext as _
import main


class TextdungeonActivity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        self.max_participants = 1
        self.sound = True

        self.build_toolbar()

        # Create your fullscreen window instance
        self.full_screen_widget = main.FullScreenWidget()

        # Set the activity root window to your fullscreen window
        self.set_canvas(self.full_screen_widget)

        # Show all elements in the activity
        self.full_screen_widget.show_all()

    def build_toolbar(self):

        toolbar_box = ToolbarBox()
        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, -1)
        activity_button.show()

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(False)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        self._levels_buttons = []

        def add_level_button(icon_name, tooltip, numeric_level):
            if self._levels_buttons:
                button = RadioToolButton(icon_name=icon_name,
                                         group=self._levels_buttons[0])
            else:
                button = RadioToolButton(icon_name=icon_name)
            self._levels_buttons.append(button)

            def callback(source):
                if source.get_active():
                    self.game.set_level(numeric_level)
                    self.game.run()

            button.connect('clicked', callback)
            button.set_tooltip(tooltip)

        add_level_button('male-7', _("Hard"), 3)
        add_level_button('male-4', _("Medium"), 2)
        add_level_button('male-1', _("Easy"), 1)

        for button in self._levels_buttons[::-1]:
            toolbar_box.toolbar.insert(button, -1)

        separator2 = Gtk.SeparatorToolItem()
        separator2.props.draw = True
        separator2.set_expand(False)
        toolbar_box.toolbar.insert(separator2, -1)
        separator2.show()

        button = ToolButton('speaker-muted-100')
        button.set_tooltip(_('Sound'))
        button.connect('clicked', self.sound_control)
        toolbar_box.toolbar.insert(button, -1)

        separator3 = Gtk.SeparatorToolItem()
        separator3.props.draw = False
        separator3.set_expand(True)
        toolbar_box.toolbar.insert(separator3, -1)
        separator3.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()
        self.show_all()

    def sound_control(self, button):
        self.sound = not self.sound
        self.game.sound = self.sound
        if not self.sound:
            button.set_icon_name('speaker-muted-000')
            button.set_tooltip(_('No sound'))
        else:
            button.set_icon_name('speaker-muted-100')
            button.set_tooltip(_('Sound'))
