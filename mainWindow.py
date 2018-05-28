from tkinter import *
from tkinter.ttk import *

import logging

import sleekxmpp

from theme import load_image
from config import config


LOGGER = logging.getLogger(__name__)

TYPE_FOREIGN = 'FOREIGN'     # For XMPP based buddies.
TYPE_LOCAL = 'LOCAL'         # For local buddies eg Bao engines

STATUS_OFFLINE = 'OFFLINE'     # Flags buddies that are currently off-line
STATUS_ONLINE = 'ONLINE'       # Flags buddies that are currently on-line


class MainWindow(Tk):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.title('PyBawo')
        self.minsize(200, 150)

        self.menubar = Menu(self, relief=FLAT)
        self.init_menubar()

        # logo_label = Label(self, image=load_image('art/logo-small.png'))
        # logo_label.pack(side=TOP, fill=BOTH)

        self.buddy_view = BuddyView(self)
        self.buddy_view.pack(side=TOP, fill=BOTH)
        self.init_buddies()

        self.xmpp_client = None
        self.init_xmpp_client()

    def init_menubar(self):
        self.config(menu=self.menubar)
        self.init_file_menu()
        self.init_edit_menu()
        self.init_help_menu()

    def init_file_menu(self):
        self.file_menu = Menu(self.menubar, relief=FLAT, tearoff=False)
        self.menubar.add_cascade(label='File', menu=self.file_menu)

        self.file_menu.add_command(label='New local game', accelerator='Ctrl+N',
                                   command=self.new_local_game)
        self.bind('<Control-KeyPress-n>', lambda e: self.new_local_game())

        self.file_menu.add_command(label='Add buddy', accelerator='Ctrl+A',
                                   command=self.add_buddy)
        self.bind('<Control-KeyPress-a>', lambda e: self.add_buddy())

        self.file_menu.add_command(label='Quit', accelerator='Ctrl+Q',
                                   command=self.quit)
        self.bind('<Control-KeyPress-q>', lambda e: self.quit())

    def init_edit_menu(self):
        self.edit_menu = Menu(self.menubar, relief=FLAT, tearoff=False)
        self.menubar.add_cascade(label='Edit', menu=self.edit_menu)

        self.edit_menu.add_command(label='Configure', accelerator='Ctrl+E',
                                   command=self.configure)
        self.bind('<Control-KeyPress-e>', lambda e: self.configure())

    def init_help_menu(self):
        self.help_menu = Menu(self.menubar, relief=FLAT, tearoff=False)
        self.menubar.add_cascade(label='Help', menu=self.help_menu)

        self.help_menu.add_command(label='About PyBawo', command=self.about)

    def init_buddies(self):
        self.buddy_view.add_buddy('PyBawo', TYPE_LOCAL, STATUS_ONLINE,
                                  self.new_local_game)

    def init_xmpp_client(self):
        if not config['xmpp']['jid']:
            LOGGER.warning('XMPP not configured')
            return
        self.xmpp_client = sleekxmpp.ClientXMPP(jid=config['xmpp']['jid'],
                                                password=config['xmpp']['password'])
        self.xmpp_client.add_event_handler('session_start', self.xmpp_connected)
        self.xmpp_client.add_event_handler('message', self.xmpp_message_received)
        self.xmpp_client.connect()

    def add_buddy(self):
        pass

    def new_local_game(self, engine='PyBawo'):
        LOGGER.debug('Local game with %s requested', engine)
        pass

    def configure(self):
        pass

    def about(self):
        pass

    def quit(self):
        # TODO: Stop Jabber client, any running games, etc
        self.destroy()

    def xmpp_connected(self, event):
        self.xmpp_client.send_presence()
        self.get_roster()

    def xmpp_message_received(self, message):
        pass


class BuddyView(Treeview):
    def __init__(self, *args, **kwargs):
        kwargs['columns'] = ['type']
        super(BuddyView, self).__init__(*args, **kwargs)
        self.insert('', END, STATUS_ONLINE, text=STATUS_ONLINE.capitalize(),
                    open=True)
        self.insert('', END, STATUS_OFFLINE, text=STATUS_OFFLINE.capitalize())
        self.heading('#0', text='Buddy', anchor=W)
        self.heading('0', text='Type', anchor=W)

    def add_buddy(self, username, type_, status, on_click_callback):
        '''Add buddy identified by username.

        Parameters:

            -> username          - The display name of the buddy.

            -> type_             - Type of buddy. Can be be one of:

                * TYPE_LOCAL   - Local buddies/players (like a local game engine).
                * TYPE_FOREIGN - Non local buddies found on the XMPP network

            -> status            - One of the following constants:

                * STATUS_ONLINE  - Buddy is on-line
                * STATUS_OFFLINE - Buddy is off-line
            
            -> on_click_callback - Callback called when buddy is clicked.
        '''
        self.insert(status, END, iid=username, text=username, tags=[username],
                    values=[type_.capitalize()])
        self.tag_bind(username, '<1>', lambda e: on_click_callback(username))

    def remove_buddy(self, username):
        self.delete(username)


if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()
