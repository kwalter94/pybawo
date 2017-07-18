from tkinter import *
from tkinter.ttk import *

class HistoryView(LabelFrame):
    def __init__(self, master, ab_color, AB_color, *args, **kwargs):
        LabelFrame.__init__(self, master, text='History', labelanchor=N,
                            *args, **kwargs)

        self.text = Text(self, takefocus=0, width=20, height=10,
                         background='white', font='sans-serif 10')
        self.text.bind('<FocusIn>', lambda e: self.master.focus_set())
        self.text.grid(row=0, column=0, sticky=E+W, padx=5, pady=5)

        self.scrollbar = Scrollbar(self, command=self.text.yview)
        self.text['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.grid(row=0, column=1, rowspan=2, sticky=N+S, padx=5,
                            pady=5)

        self.text.tag_configure('ab', foreground=ab_color)
        self.text.tag_configure('AB', foreground=AB_color)

        self.on_undo = lambda : None
        self.undo_button = Button(self,
                                  text='undo',
                                  command=lambda: self.on_undo())
        self.undo_button.grid(row=1, column=0, sticky=E+W, padx=5, pady=5)

        self.history = None
        self.board_view = None

    def set_game(self, game):
        self.history = game
        for node in self.history:
            self.on_history_update(node, self.history.branch)
        self.history.add_watcher(self.on_history_update)

    def set_board_view(self, board_view):
        self.board_view = board_view

    def set_event_listener(self, event, listener):
        if event == 'undo':
            if listener:
                self.on_undo = listener
            else:
                self.on_undo = lambda : None
        else:
            raise ValueError('Unknown event: ' + event)
    
    def write(self, hfile):
        hfile.write(self.text.get('1.0', END))

    def on_mouse_enter_item(self, item_no):
        self.text.tag_config(str(item_no), background='Yellow')
        move, state = self.history[item_no]
        self.board_view.update(state.get_board())

    def on_mouse_leave_item(self, item_no):
        self.text.tag_config(str(item_no), background='')
        move, state = self.history.get_current_node()
        self.board_view.update(state.get_board())

    def on_history_update(self, node, func_responsible):
        move, state = node
        if func_responsible == self.history.branch:
            item_no = len(self.history) - 1
            if move is None:
                tags = (str(item_no),)
            elif move[0] in 'ab':
                tags = (str(item_no), 'ab')
            elif move[0] in 'AB':
                tags = (str(item_no), 'AB')
            else:
                raise ValueError('Invalid move')

            text = self.text
            text.insert(END, '{:2}. {}\n'.format(item_no, move), tags)
            text.see(END)
            text.tag_bind(tags[0], '<Enter>',
                          lambda e: self.on_mouse_enter_item(item_no),
                          add='+')
            text.tag_bind(tags[0], '<Leave>',
                          lambda e: self.on_mouse_leave_item(item_no),
                          add='+')
        elif func_responsible == self.history.pop:
            item_no = len(self.history) - 1
            self.text.delete('{}.0'.format(item_no), 'end - 1 chars')
            self.text.see(END)
