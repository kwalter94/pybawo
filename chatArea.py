from tkinter import *
from tkinter.ttk import *

import threading
import bao


class ChatArea(LabelFrame):
    def __init__(self, master, **kwargs):
        LabelFrame.__init__(self, master, text='Chat', labelanchor=N, **kwargs)

        self.msg_view = Text(self, background='white',
                              height=10, width=70, font='sans-serif 10',
                              wrap=WORD, state=DISABLED)
        self.msg_view.grid(row=0, column=0, sticky=E+W, pady=5, padx=5)

        mv_scrollbar = Scrollbar(self, command=self.msg_view.yview)
        mv_scrollbar.grid(row=0, column=1, rowspan=2, sticky=N+S, padx=5,
                          pady=5)
        self.msg_view['yscrollcommand'] = mv_scrollbar.set
        self.msg_view_lock = threading.Semaphore()

        self.msg_entry = Entry(self, background='white')
        self.msg_entry.grid(row=1, column=0, sticky=E+W, padx=5, pady=5)
        self.msg_entry.bind('<Return>', lambda e: self.send_message())
        self.msg_entry.focus_set()

        self.player_id = {'ab': 'ab', 'AB': 'AB'}
        self.user = 'AB'

        self.event_listeners = {
            'message_ab': (lambda m: None),
            'message_AB': (lambda m: None)
        }

        self.message_queue = list()
        self.message_queue_sem = threading.Semaphore()
        self.poll_messages()

    def set_id(self, player, sid):
        if player not in self.player_id:
            raise ValueError('Invalid id')
        self.player_id[player] = sid

    def set_color(self, player, color):
        if player not in self.player_id:
            raise ValueError('Invalid id')
        self.msg_view.tag_configure(player, foreground=color)

    def set_user(self, player):
        if player not in self.player_id:
            raise ValueError('Invalid player')
        self.user = player

    def set_event_listener(self, event, listener):
        if event not in self.event_listeners:
            raise ValueError('Invalid event')
        self.event_listeners[event] = listener

    def message(self, msg, from_):
        dest = bao.Board.rival_field(from_)
        self.queue_message((msg, self.player_id[from_], from_))
        self.event_listeners['message_' + dest](msg)

    def queue_message(self, args):
        self.message_queue_sem.acquire()
        self.message_queue.append(args)
        self.message_queue_sem.release()

    def poll_messages(self):
        if self.message_queue:
            self.message_queue_sem.acquire()
            args = self.message_queue.pop(0)
            self.message_queue_sem.release()
            self.display_message(*args)
        self.master.after(100, self.poll_messages)
        
    def display_message(self, msg, author_str, tag):
        self.msg_view['state'] = NORMAL
        self.msg_view.insert(END, author_str + ':\n', tag)
        self.msg_view.insert(END, self.process_message(msg) + '\n', tag)
        self.msg_view.see(END)
        self.msg_view['state'] = DISABLED

    def send_message(self):
        if self.user is None:
            return None
        msg = self.msg_entry.get()
        self.msg_entry.delete('0', END)
        user_id = self.player_id[self.user]
        self.queue_message((msg, 'You ({}) say:'.format(user_id), self.user))
        dest = bao.Board.rival_field(self.user)
        self.event_listeners['message_' + dest](msg)

    def process_message(self, msg):
        left_margin = ' ' * 4
        return left_margin + msg.rstrip().replace('\n', '\n' + left_margin)
