from tkinter import *
from tkinter.ttk import *

import os
import threading
import time
import tkinter.messagebox

import bao
import baoAgent
import boardView 
import chatArea
import historyView
import player
import theme


USERNAME = os.environ.get('USERNAME') or os.environ.get('USER')


class GameWindow(Toplevel):
    class ArbiterProxy(baoAgent.BaoAgent):
        def __init__(self, parent, target):
            '''parent is the GameWindow and target is the field of player
            communicating through this proxy.'''
            super(type(self), self).__init__()
            self.parent = parent
            self.player_fd = target
            self.opponent_fd = bao.Board.rival_field(target)

        def new_game(self, field, **kwargs):
            pass

        def message(self, msg):
            self.parent.players[self.opponent_fd].message(msg, self.opponent_fd)
            self.parent.chat_area.message(msg, self.player_fd)

        def move(self, mv):
            self.parent.move(mv, self.player_fd, self.opponent_fd)

        def forfeit(self):
            self.parent.forfeit(self.player_fd)

        def ack(self, request, status, reason=None):
            if request == baoAgent.RQ_UNDO and self.parent.pending_undo != 0:
                self.parent.pending_undo -= 1
                if status == baoAgent.STS_ACCEPT:
                    self.parent.game.pop_node()
                    board = self.parent.game.get_current_node()[1].get_board()
                    self.parent.board_view.update(board)
            elif request == baoAgent.RQ_MOVE:
                if status == baoAgent.STS_REJECT:
                    self.parent.board.set_notification(
                        'Player rejected move: ' + (reason or ''),
                        boardView.NOTIFICATION_ERROR)
                    
           
    def __init__(self, ab_color='red', AB_color='blue'):
        Toplevel.__init__(self)
        self.styler = Style()

        self.exec_move_thread = None
        self.exec_move_sem = threading.Semaphore()

        self.pending_undo = 0

        self.board_view = boardView.BoardView(self, relief=FLAT)
        self.board_view.grid(row=0, column=0, columnspan=2)

        self.history_view = historyView.HistoryView(self,
                                                    ab_color=ab_color,
                                                    AB_color=AB_color)
        self.history_view.set_event_listener('undo', self.request_undo)
        self.history_view.grid(row=1, column=1, sticky=N+S, padx=5, pady=5)

        self.chat_area = chatArea.ChatArea(self)
        self.chat_area.grid(row=1, column=0, sticky=N+S, padx=5, pady=5)
        self.chat_area.set_color('AB', 'blue')
        self.chat_area.set_color('ab', 'red')
        self.chat_area.set_user('AB')

        self.menu = Menu(self, relief=FLAT)
        self.config(menu=self.menu)

        file_menu = Menu(self.menu, relief=FLAT, tearoff=False)
        file_menu.add_command(
            label='Close',
            accelerator='Ctrl+C',
            command=lambda : self.destroy())
        self.bind('<Control-KeyPress-c>', lambda e: self.destroy())
        self.menu.add_cascade(label='File', menu=file_menu)

        edit_menu = Menu(self.menu, relief=FLAT, tearoff=False)
        theme_menu = Menu(edit_menu, relief=FLAT, tearoff=False)
        for name in self.board_view.get_themes():
            def gen_theme_setter(name):
                # python does not *freeze* variables on lambda closure
                # hence using this
                return (lambda :
                    self.board_view.set_theme(
                        name,
                        self.game.get_current_node()[1].get_board()))
            theme_menu.add_command(label=name, command=gen_theme_setter(name))
        edit_menu.add_cascade(label='Select theme', menu=theme_menu)
        edit_menu.add_command(label='Invert board',
                              accelerator='Ctrl+I',
                              command=self.board_view.invert)
        self.bind('<Control-KeyPress-i>', lambda e: self.board_view.invert())
        self.menu.add_cascade(label='Edit', menu=edit_menu)

    def new_game(self, variant, AB_player, ab_player):
        self.game = bao.new_game(variant=variant)
        self.players = {'AB': AB_player, 'ab': ab_player}
        if AB_player.get_type() == player.PL_MACHINE:
            AB_player.set_arbiter(self.ArbiterProxy(self, 'AB'))
            self.chat_area.set_event_listener('message_AB', AB_player.message)
            self.chat_area.set_id('AB', AB_player.get_id())
        if ab_player.get_type() == player.PL_MACHINE:
            ab_player.set_arbiter(self.ArbiterProxy(self, 'ab'))
            self.chat_area.set_event_listener('message_ab', ab_player.message)
            self.chat_area.set_id('ab', ab_player.get_id())
        
        self.board_view.update(self.game.get_current_node()[1].get_board())

        self.history_view.set_game(self.game);
        self.history_view.set_board_view(self.board_view)

        p = self.players[self.game.get_rules().player_starting]
        if p.get_type() == player.PL_MACHINE:
            self.board_view.set_move_polling(False)
        self.board_view.set_move_listener(self.board_view_move)
        ab_player.message('go')
        AB_player.message('go')

    def main(self):
        self.mainloop()

    def quit(self, exit_sts=0):
        self.destroy()
        exit(exit_sts)

    def move_watcher(self, hole, value):
        self.board_view.clear_all_holes()
        self.board_view.highlight_hole(hole)
        self.board_view.update_hole(hole, value)
        time.sleep(0.25)
        return True

    def board_view_move(self, mv):
        player_fd = self.game.get_player()
        opponent_fd = bao.Board.rival_field(player_fd)
        self.move(mv, player_fd, opponent_fd)
                                         
    def move(self, mv, player_fd, opponent_fd):
        self.exec_move_sem.acquire()
        self.board_view.set_move_polling(False)
        mv_t = self.game.get_closest_move(mv)
        p = self.players[player_fd]
        if self.game.get_player() != player_fd:
            p.ack(baoAgent.RQ_MOVE, baoAgent.STS_REJECT, 'Not your turn yet')
            self.board_view.set_notification(
                'Move rejected, not {}\'s turn'.format(player_fd),
                boardView.NOTIFICATION_ERROR)
            self.exec_move_sem.release()
            if p.get_type() == player.PL_HUMAN:
                self.board_view.set_move_polling(True)
        elif mv_t is None:
            p.ack(baoAgent.RQ_MOVE, baoAgent.STS_REJECT, 'Invalid move')
            self.board_view.set_notification(
                'Invalid move ({}) by {}'.format(mv, p.get_id()),
                boardView.NOTIFICATION_ERROR)
            self.exec_move_sem.release()
            if p.get_type() == player.PL_HUMAN:
                self.board_view.set_move_polling(True)
        else:
            if self.exec_move_thread:
                self.exec_move_thread.join()
            self.exec_move_thread = threading.Thread(
                target=self.exec_move, args=(mv_t,))
            self.exec_move_thread.start()

    def exec_move(self, move):
        self.board_view.set_notification('Executing {}'.format(move))
        player_fd = self.game.get_player()
        opponent_fd = bao.Board.rival_field(player_fd)
        try:
            self.players[opponent_fd].move(move)
            self.game.branch(move, True, move_watcher=self.move_watcher)
            self.board_view.clear_all_holes()
        except bao.InvalidMoveError:
            self.board_view.set_notification(
                'Move {} rejected - Invalid move'.format(move),
                boardView.NOTIFICATION_ERROR)
        except bao.LongMoveError:
            self.board_view.set_notification(
                'Move {} rejected - Long move'.format(move),
                boardView.NOTIFICATION_ERROR)
        finally:
            player_fd = self.game.get_player()
            opponent_fd = bao.Board.rival_field(player_fd)
            if self.game.is_game_over():
                opp = self.players[opponent_fd]
                self.board_view.set_notification(opp.get_id() + ' wins.')
            elif self.players[player_fd].get_type() == player.PL_HUMAN:
                self.board_view.set_move_polling(True)
            self.exec_move_sem.release()

    def forfeit(self, player_fd):
        def report_forfeit(winner_fd, loser_fd):
            loser = self.players[loser_fd]
            winner = self.players[winner_fd]
            self.board_view.set_notification(
                '{} playing as {} wins. {} playing as {} has forfeited.'.format(
                    winner.get_id(), winner_fd, loser.get_id(), loser_fd))
        report_forfeit(bao.Board.rival_field(player_fd), player_fd)

    def request_undo(self):
        return None         # FIX-ME: Add a delete method to HistoryView
        for p in list(self.players.values()):
            if p.get_type() != player.PL_HUMAN:
                p.undo()
            self.pending_undo += 1


class NewGameWindow(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.title("New game")

        self.variant_var = StringVar(self)
        self.ab_player_var = IntVar(self)
        self.AB_player_var = IntVar(self)

        vlabel = Label(self, text='Select variant:')
        vlabel.grid(row=0, column=0, sticky=E)

        for i, variant in enumerate(bao.get_variants()):
            radio_button = Radiobutton(self,
                                       text=variant,
                                       value=variant,
                                       variable=self.variant_var)
            radio_button.grid(row=0, column=i + 1, sticky=W)
        else:
            radio_button.invoke()

        AB_label = Label(self, text='AB player:')
        AB_label.grid(row=1, column=0, sticky=E)
        AB_human_button = Radiobutton(self,
                                      text='Human',
                                      value=player.PL_HUMAN,
                                      variable=self.AB_player_var)
        AB_human_button.grid(row=1, column=1, sticky=W)
        AB_mac_button = Radiobutton(self,
                                    text='Machine',
                                    value=player.PL_MACHINE,
                                    variable=self.AB_player_var)
        AB_mac_button.grid(row=1, column=2, sticky=W)
        AB_name_label = Label(self, text='id:')
        AB_name_label.grid(row=2, column=0, sticky=E)
        self.AB_name_entry = Entry(self, width=30)
        self.AB_name_entry.insert(0, USERNAME)
        self.AB_name_entry.grid(row=2, column=1, columnspan=3, sticky=W)
        self.AB_player_var.trace(
            'w', lambda x, y, z: self.toggle_entry(self.AB_name_entry,
                                                   self.AB_player_var))

        ab_label = Label(self, text='ab player:')
        ab_label.grid(row=3, column=0, sticky=E)
        ab_human_button = Radiobutton(self,
                                      text='Human',
                                      value=player.PL_HUMAN,
                                      variable=self.ab_player_var)
        ab_human_button.grid(row=3, column=1, sticky=W)
        ab_mac_button = Radiobutton(self,
                                    text='Machine',
                                    value=player.PL_MACHINE,
                                    variable=self.ab_player_var)
        ab_mac_button.grid(row=3, column=2, sticky=W)
        ab_mac_button.invoke()
        ab_name_label = Label(self, text='id:')
        ab_name_label.grid(row=4, column=0, sticky=E)
        self.ab_name_entry = Entry(self, width=30, state=DISABLED)
        self.ab_name_entry.grid(row=4, column=1, columnspan=3, sticky=W)
        self.ab_player_var.trace(
            'w', lambda x, y, z: self.toggle_entry(self.ab_name_entry,
                                                   self.ab_player_var))

        submit = Button(self, text='Play', command=self.start_game)
        submit.grid(row=5, column=1)
        cancel = Button(self, text='Cancel', command=self.destroy)
        cancel.grid(row=5, column=2)

    def start_game(self):
        variant = self.variant_var.get()
        AB_player_type = self.AB_player_var.get()
        if AB_player_type == player.PL_HUMAN:
            AB_player = player.Player()
            AB_id = self.AB_name_entry.get()
            if not AB_id:
                tkinter.messagebox.showerror('Error',
                                       'Please enter AB player id',
                                       parent=self)
                return None
            AB_player.set_id(AB_id)
        elif AB_player_type == player.PL_MACHINE:
            AB_player = player.Malume()
            AB_player.new_game('AB', variant=variant)

        ab_player_type = self.ab_player_var.get()
        if ab_player_type == player.PL_HUMAN:
            ab_player = player.Player()
            ab_id = self.ab_name_entry.get()
            if not ab_id:
                tkinter.messagebox.showerror('Error',
                                       'Please enter ab player id',
                                       parent=self)
                return None
            ab_player.set_id(ab_id)
        elif ab_player_type == player.PL_MACHINE:
            ab_player = player.Malume()
            ab_player.new_game(field='ab', variant=variant)

        game_window = gameWindow.GameWindow()
        game_window.new_game(variant, AB_player=AB_player, ab_player=ab_player)
        self.destroy()

    def toggle_entry(self, entry, var):
        if var.get() == player.PL_MACHINE:
            entry.config(state=DISABLED)
        else:
            entry.config(state=NORMAL)

