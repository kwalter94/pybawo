#!/usr/bin/python
from tkinter import *
from tkinter.ttk import *

from theme import load_image

import gameWindow


def main():
    main_window = Tk()
    main_window.title('Bawo')
    main_window.minsize(200, 150)
    # main_window.maxsize(200, 150)

    menu = Menu(main_window, relief=FLAT)
    main_window.config(menu=menu)

    file_menu = Menu(menu, relief=FLAT, tearoff=False)
    file_menu.add_command(
        label='New Game',
        accelerator='Ctrl+N',
        command=lambda : gameWindow.NewGameWindow(main_window))
    main_window.bind('<Control-KeyPress-n>', lambda e: NewGameWindow(self))
    file_menu.add_command(label='Quit', accelerator='Ctrl+Q',
                          command=main_window.destroy)
    main_window.bind('<Control-KeyPress-q>', lambda e: main_window.destroy)
    menu.add_cascade(label='File', menu=file_menu)

    edit_menu = Menu(menu, relief=FLAT, tearoff=False)
    edit_menu.add_command(label='Configure AI engine', accelerator='Ctrl+E')
    main_window.bind('<Control-KeyPress-e>', lambda e: lambda e: None)
    edit_menu.add_command(label='Configure Jabber', accelerator='Ctrl+J')
    main_window.bind('<Control-KeyPress-j>', lambda e: lambda e: None)
    menu.add_cascade(label='Edit', menu=edit_menu)

    logo_image = load_image('art/logo-small.png')
    logo_label = Label(main_window, image=logo_image)
    logo_label.pack(side=TOP, fill=BOTH)

    b1 = Button(main_window,
                text='New Local Game',
                command=lambda : newGameWindow.NewGameWindow(main_window))
    b1.pack(side=TOP, fill=BOTH)

    b2 = Button(main_window, text='New Networked Game', command=lambda : None)
    b2.pack(side=TOP, fill=BOTH)

    b3 = Button(main_window, text='Quit', command=main_window.destroy)
    b3.pack(side=TOP, fill=BOTH)

    main_window.mainloop()

main()
