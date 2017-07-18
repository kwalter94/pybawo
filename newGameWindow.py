from tkinter import *
from tkinter.ttk import *

import os

import tkinter.messagebox
import bao
import player
import gameWindow
import theme

USERNAME = os.environ.get('USERNAME') or os.environ.get('USER')


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
