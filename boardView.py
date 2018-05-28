from tkinter import *
from tkinter.ttk import *

import os
import random

import theme

# Used by board for notifications
NOTIFICATION_NORMAL = 0
NOTIFICATION_ERROR  = 1


class BoardView(Canvas):
    def __init__(self, *args, **kwargs):
        if 'font' in kwargs:
            self.font = kwargs['font']
            del kwargs['font']
        else:
            self.font = 'sans-serif 10'
        Canvas.__init__(self, *args, **kwargs)

        self.hole_name_to_id = {}
        self.hole_id_to_name = {}
        self.hole_id_to_def = {}
        self.hole_id_to_value_id = {}

        self.poll_moves = True
        self.move_pivot_hole = None
        self.move_offset_hole = None
        self.move_listener = lambda m: None

        self.set_theme('default')

    def get_themes(self):
        themes = set()
        for f in os.listdir(theme.THEME_DIR_PATH):
            if f.startswith('.'):
                continue
            themes.add(os.path.splitext(f)[0])
        return iter(themes)

    def set_theme(self, t, board=None):
        self.theme = theme.get_theme(t)
        self.load_theme()
        if board:
            self.update(board)

    def set_move_listener(self, listener):
        if listener is None:
            self.move_listener = lambda m: None
        self.move_listener = listener

    def set_move_polling(self, polling):
        if polling is False:
            self.move_pivot_hole = None
            self.move_offset_hole = None
            self.poll_moves = False
            self.clear_all_holes()
        elif polling is True:
            self.poll_moves = True
        else:
            raise ValueError('Polling must either be True or False')

    def update(self, board):
        for hole in board.holes():
            if hole == 'b9' or hole == 'B9':
                continue
            self.update_hole(hole, board[hole])

    def update_hole(self, hole, value):
        if 'seed' in self.theme['board']:
            s_def = self.theme['board']['seed']
            h_def = self.theme['board']['holes'][hole]
            h_tag = 'seed_' + hole
            self.delete(h_tag)
            for i in range(value):
                x = random.randint(int(0.3 * h_def['select_image'].width()),
                                   int(0.7 * h_def['select_image'].width()))
                y = random.randint(int(0.3 * h_def['select_image'].height()),
                                   int(0.7 * h_def['select_image'].height()))
                self.create_image(h_def['x'] + x,
                                  h_def['y'] + y,
                                  image=s_def['image'],
                                  anchor=NW,
                                  tags=(h_tag,))
                self.tag_lower(h_tag, self.hole_name_to_id[hole])
                
        self.itemconfigure(self.hole_id_to_value_id[self.hole_name_to_id[hole]],
                           text=value)
        

    def highlight_hole(self, hole):
        hole_id = self.hole_name_to_id[hole]
        self.itemconfigure(
            hole_id, image=self.hole_id_to_def[hole_id]['select_image']
        )

    def clear_hole(self, hole):
        hole_id = self.hole_name_to_id[hole]
        self.itemconfigure(
            hole_id, image=self.hole_id_to_def[hole_id]['deselect_image']
        )

    def clear_all_holes(self):
        for hole in self.hole_name_to_id:
            self.clear_hole(hole)

    def set_notification(self, message, ntype=NOTIFICATION_NORMAL):
        if ntype == NOTIFICATION_NORMAL:
            self.itemconfigure('note', text=message, fill='black')
        elif ntype == NOTIFICATION_ERROR:
            self.itemconfigure('note', text=message, fill='red')
        else:
            raise ValueError('Invalid notification type')

    def clear_notification(self):
        self.itemconfigure('note', text='')

    def invert(self):
        hole_name_to_id = {}
        hole_id_to_name = {}
        hole_values = {}
        for hole in self.hole_name_to_id:
            if hole[0].isupper():
                new_hole = hole.lower()
            elif hole[0].islower():
                new_hole = hole.upper()
            else:
                raise RuntimeError('Invalid hole ' + hole)
            hole_id = self.hole_name_to_id[hole]
            hole_name_to_id[new_hole] = hole_id
            hole_id_to_name[hole_id] = new_hole

            hole_values[new_hole] = self.itemcget(
                self.hole_id_to_value_id[hole_id], 'text'
            )

        for hole, value in list(hole_values.items()):
            self.update_hole(hole, value)

        self.hole_name_to_id = hole_name_to_id
        self.hole_id_to_name = hole_id_to_name

        self.field_labels = { 'ab': self.field_labels['AB'],
                              'AB': self.field_labels['ab'] }
        self.itemconfigure(self.field_labels['AB'], text='AB')
        self.itemconfigure(self.field_labels['ab'], text='ab')

    def load_theme(self):
        width = self.theme['board']['image'].width()
        height = self.theme['board']['image'].height()

        self.configure(width=width, height=height)
        self.create_rectangle(0, 0, width, height, fill=self.cget('bg'))
        self.create_image(0,
                          0,
                          image=self.theme['board']['image'],
                          anchor=NW,
                          tags=('board',))
        self.create_text(self.theme['notification_area']['x'],
                         self.theme['notification_area']['y'],
                         anchor=NW,
                         text=None,
                         tags=('note',))
        self.field_labels = {'ab': 'north_label', 'AB': 'south_label'}
        self.create_text(self.theme['field_label']['ab']['x'],
                         self.theme['field_label']['ab']['y'],
                         text='ab',
                         anchor=SW,
                         tags=(self.field_labels['ab'],))
        self.create_text(self.theme['field_label']['AB']['x'],
                         self.theme['field_label']['AB']['y'],
                         text='AB',
                         anchor=NW,
                         tags=(self.field_labels['AB'],))

        for hole, hole_def in list(self.theme['board']['holes'].items()):
            if hole == 'b9' or hole == 'B9':
                continue

            if 'seed' in self.theme['board']:
                value_id_x = (hole_def['x']
                              + int(0.2 * hole_def['select_image'].width()))
                value_id_y = (hole_def['y']
                              + int(0.2 * hole_def['select_image'].height()))
            else:
                value_id_x = (hole_def['x']
                              + hole_def['select_image'].width() / 2)
                value_id_y = (hole_def['y']
                              + hole_def['select_image'].height() / 2)
            value_id = self.create_text(value_id_x,
                                        value_id_y,
                                        text='0',
                                        anchor=CENTER,
                                        font=self.font)

            hole_id = self.create_image(hole_def['x'],
                                        hole_def['y'],
                                        image=hole_def['deselect_image'],
                                        anchor=NW)

            self.set_hole_vars(hole_id, value_id, hole, hole_def)
            self.set_hole_bindings(hole_id)

    def set_hole_vars(self, hole_id, value_id, hole, hole_def):
        self.hole_name_to_id[hole] = hole_id
        self.hole_id_to_name[hole_id] = hole
        self.hole_id_to_def[hole_id] = hole_def
        self.hole_id_to_value_id[hole_id] = value_id

    def set_hole_bindings(self, hole_id):
        # NOTE: hole names change after calling self.invert therefore the names
        # must be determined at the time the callback is called
        self.tag_bind(hole_id,
                      '<Enter>',
                      lambda e:
                        self.on_hole_entered(self.hole_id_to_name[hole_id]))
        self.tag_bind(hole_id,
                      '<Leave>',
                      lambda e:
                        self.on_hole_exited(self.hole_id_to_name[hole_id]),
                      add='+')
        self.tag_bind(hole_id,
                      '<Button-1>',
                      lambda e:
                        self.on_hole_b1clicked(self.hole_id_to_name[hole_id]),
                      add='+')
        self.tag_bind(hole_id,
                      '<Button-3>',
                      lambda e:
                        self.on_hole_b3clicked(self.hole_id_to_name[hole_id]),
                      add='+')


    def on_hole_entered(self, hole):
        if not self.poll_moves:
            return None
        elif self.move_pivot_hole:
            if self.gen_move(self.move_pivot_hole, hole):
                self.move_offset_hole = hole
            else:
                return None
        else:
            self.set_notification('Hole {} selected'.format(hole))
        self.highlight_hole(hole)

    def on_hole_exited(self, hole):
        if not self.poll_moves or hole == self.move_pivot_hole:
            return None
        self.clear_hole(hole)
        if self.move_pivot_hole:
            return None
        self.clear_notification()

    def on_hole_b1clicked(self, hole):
        if self.poll_moves is False or hole[1] == '9':
            return None
        elif self.move_pivot_hole is None:
            self.move_pivot_hole = hole
            self.set_notification('Hole {} pinned for move'.format(hole))
        else:
            move = self.gen_move(self.move_pivot_hole,
                                  self.move_offset_hole)
            if move:
                if (self.move_offset_hole
                        or self.move_pivot_hole == self.move_offset_hole):
                    self.clear_hole(self.move_pivot_hole)
                self.set_notification('{} chosen'.format(move))
                self.set_move_polling(False)
                self.clear_move()
                self.move_listener(move)
            else:
                return None

    def on_hole_b3clicked(self, hole):
        if self.poll_moves:
            self.clear_all_holes()
            self.clear_move()
            self.set_notification('Move cancelled')

    def clear_move(self):
        self.move_pivot_hole = None
        self.move_offset_hole = None

    def gen_move(self, pivot_hole, offset_hole):
        if offset_hole == None or pivot_hole == offset_hole:
            return pivot_hole + '-$'
        else:
            move_dir = self.get_relative_position(pivot_hole, offset_hole)
            if move_dir:
                return pivot_hole + move_dir
            else:
                return None

    def get_relative_position(self, pivot_hole, offset_hole):
        pivot_hole = pivot_hole.lower()
        offset_hole = offset_hole.lower()
        if pivot_hole[0] == offset_hole[0]:
            offset = int(pivot_hole[1]) - int(offset_hole[1])
            if offset == -1:
                return 'R'
            elif offset == 1:
                return 'L'
            else:
                return None
        elif (pivot_hole in ('a8', 'b8') and offset_hole in ('a8', 'b8')):
            return 'R'
        elif (pivot_hole in ('a1', 'b1') and offset_hole in ('a1', 'b1')):
            return 'L'
        else:
            return None
