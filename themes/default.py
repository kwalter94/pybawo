import os
import os.path

theme_path = 'default'
board_image = load_image(os.path.join(theme_path, 'board.png'))
hole_select_image = load_image(os.path.join(theme_path, 'hole_select.png'))
hole_deselect_image = load_image(os.path.join(theme_path, 'hole_deselect.png'))
nyumba_select_image = load_image(os.path.join(theme_path, 'nyumba_select.png'))
nyumba_deselect_image = hole_deselect_image
store_select_image = load_image(os.path.join(theme_path, 'store_select.png'))
store_deselect_image = load_image(os.path.join(theme_path,
                                               'store_deselect.png'))
seed_image = load_image(os.path.join(theme_path, 'seed.png'))

self = {
    'notification_area': {
        'x': 185,
        'y': 340
    },
    'field_label': {
        'ab': {
            'x': 705,
            'y': 70 
        },
        'AB': {
            'x': 705,
            'y': 305
        }
    },
    'board': {
        'image': board_image,
        'seed': {
            'image': seed_image
        },
        'holes': {
            'b8': {
                'x': 60,
                'y': 61,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'b7': {
                'x': 125,
                'y': 61,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'b6': {
                'x': 190,
                'y': 61,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'b5': {
                'x': 252,
                'y': 61,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'b4': {
                'x': 315,
                'y': 61,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'b3': {
                'x': 380,
                'y': 61,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'b2': {
                'x': 442,
                'y': 61,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'b1': {
                'x': 505,
                'y': 61,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'a9': {
                'x': 585,
                'y': 66,
                'select_image': store_select_image,
                'deselect_image': store_deselect_image
            },
            'a8': {
                'x': 60,
                'y': 126,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'a7': {
                'x': 125,
                'y': 126,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'a6': {
                'x': 190,
                'y': 126,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'a5': {
                'x': 250,
                'y': 126,
                'select_image': nyumba_select_image,
                'deselect_image': nyumba_deselect_image
            },
            'a4': {
                'x': 315,
                'y': 126,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'a3': {
                'x': 380,
                'y': 126,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'a2': {
                'x': 442,
                'y': 126,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'a1': {
                'x': 505,
                'y': 126,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'A1': {
                'x': 60,
                'y': 206,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'A2': {
                'x': 125,
                'y': 206,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'A3': {
                'x': 190,
                'y': 206,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'A4': {
                'x': 250,
                'y': 206,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'A5': {
                'x': 315,
                'y': 206,
                'select_image': nyumba_select_image,
                'deselect_image': nyumba_deselect_image
            },
            'A6': {
                'x': 380,
                'y': 206,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'A7': {
                'x': 442,
                'y': 206,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'A8': {
                'x': 505,
                'y': 206,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'A9': {
                'x': 585,
                'y': 211,
                'select_image': store_select_image,
                'deselect_image': store_deselect_image
            },
            'B1': {
                'x': 60,
                'y': 271,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'B2': {
                'x': 125,
                'y': 271,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'B3': {
                'x': 190,
                'y': 271,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'B4': {
                'x': 250,
                'y': 271,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'B5': {
                'x': 315,
                'y': 271,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'B6': {
                'x': 380,
                'y': 271,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'B7': {
                'x': 442,
                'y': 271,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            },
            'B8': {
                'x': 505,
                'y': 271,
                'select_image': hole_select_image,
                'deselect_image': hole_deselect_image
            }
        }
    }
}
 
