import os

def make_theme():
    theme = {
        'board': {
            'image': None,
            'holes': {}
        },
        'field_label': {
            'ab': {
                'x': 620,
                'y': 120 
            },
            'AB': {
                'x': 620,
                'y': 195
            }
        },
        'notification_area': {
            'x': 225,
            'y': 305
        }
    }

    theme_path = 'classic'

    board_image = load_image(os.path.join(theme_path, 'board.png'))
    hole_select_image = load_image(os.path.join(theme_path, 'hole_select.png'))
    hole_deselect_image = load_image(
            os.path.join(theme_path, 'hole_deselect.png'))
    nyumba_select_image = load_image(os.path.join(theme_path, 'nyumba.png'))
    nyumba_deselect_image = hole_deselect_image
    north_store_select_image = load_image(
            os.path.join(theme_path, 'north_store_select.png'))
    north_store_deselect_image = load_image(
            os.path.join(theme_path, 'store_deselect.png'))
    south_store_select_image = load_image(
            os.path.join(theme_path, 'south_store_select.png'))
    south_store_deselect_image = north_store_deselect_image

    theme['board']['image'] = board_image

    y = 34
    for row in ([i + j for j in '12345678'] for i in'baAB'):
        if row[0][0] in 'ab':
            row.reverse()
        x = 48
        for hole in row:
            if hole.lower() == 'a5':
                hole_def = {'x': x, 'y': y,
                            'select_image': nyumba_select_image,
                            'deselect_image': nyumba_deselect_image}
                x += nyumba_select_image.width() + 4
            else:
                hole_def = {'x': x, 'y': y,
                            'select_image': hole_select_image,
                            'deselect_image': hole_deselect_image}
                x += hole_select_image.width() + 4
            theme['board']['holes'][hole] = hole_def

        if row[0][0] == 'a':
            y += hole_select_image.height() + 8
        else:
            y += hole_select_image.height() + 5
    theme['board']['holes']['a9'] = {
        'x': 2, 'y': 36, 'select_image': south_store_select_image,
        'deselect_image': south_store_deselect_image}

    theme['board']['holes']['A9'] = {
        'x': 557, 'y': 36, 'select_image': north_store_select_image,
        'deselect_image': north_store_deselect_image}

    return theme

self = make_theme()

