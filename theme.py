from tkinter import *
from tkinter.ttk import *

import os
import os.path

THEME_PATH = 'themes'


def load_image(path):
    import PIL.ImageTk as imageTk

    image = imageTk.Image.open(path)
    return imageTk.PhotoImage(image)

def get_theme(theme_name='classic'):
    sym_tab =  { 'load_image':
                    lambda p: load_image(os.path.join(THEME_PATH, p)),
                 'self': None }
    exec(compile(open(os.path.join(THEME_PATH, theme_name + '.py')).read(), os.path.join(THEME_PATH, theme_name + '.py'), 'exec'), sym_tab)

    return sym_tab['self']
