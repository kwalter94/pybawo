import os
import os.path

THEME_DIR_PATH = 'themes'


def load_image(path):
    import PIL.ImageTk as imageTk

    image = imageTk.Image.open(path)
    return imageTk.PhotoImage(image)

def get_theme(theme_name='classic'):
    image_loader = lambda p: load_image(os.path.join(THEME_DIR_PATH, p))
    sym_tab =  {'load_image': image_loader, 'self': None}
                
    full_theme_path = os.path.join(THEME_DIR_PATH, theme_name + '.py')
    theme_script = open(full_theme_path).read()

    exec(compile(theme_script, full_theme_path, 'exec'), sym_tab)

    return sym_tab['self']
