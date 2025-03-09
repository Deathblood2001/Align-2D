import bpy
import os
import gettext
import bpy.utils.previews
from bpy.app.handlers import persistent
def _(text):
    return bpy.app.translations.pgettext(text)
custom_icons = None
last_theme_dark = None

def is_dark_theme():
    theme = bpy.context.preferences.themes[0]
    background_color = theme.user_interface.wcol_regular.inner
    brightness = sum(background_color[:3]) / 3
    return brightness < 0.5  

def load_icons(icons_dir):
    global custom_icons
    if custom_icons is not None:
        bpy.utils.previews.remove(custom_icons)
        custom_icons = None
        
    custom_icons = bpy.utils.previews.new()
    
    if os.path.exists(icons_dir):
        for file_name in os.listdir(icons_dir):
            if file_name.lower().endswith(".png"):
                icon_name = os.path.splitext(file_name)[0]  
                file_path = os.path.join(icons_dir, file_name)
                custom_icons.load(icon_name, file_path, 'IMAGE')
    return custom_icons

def get_custom_icons():
    global custom_icons, last_theme_dark
    addon_path = os.path.dirname(__file__)

    current_theme_dark = is_dark_theme()
    
    if custom_icons is None or last_theme_dark != current_theme_dark:
        icons_dir = os.path.join(addon_path, "icons" if current_theme_dark else "icons/black")
        load_icons(icons_dir)
        last_theme_dark = current_theme_dark

    return custom_icons


@persistent
def theme_change_handler(dummy):
    global last_theme_dark
    current_theme_dark = is_dark_theme()
    if last_theme_dark is None or last_theme_dark != current_theme_dark:
        get_custom_icons()  

def register():
    global custom_icons
    bpy.app.handlers.depsgraph_update_post.append(theme_change_handler)
    custom_icons = get_custom_icons()

def unregister():
    global custom_icons
    bpy.app.handlers.depsgraph_update_post.remove(theme_change_handler)
    if custom_icons is not None:
        bpy.utils.previews.remove(custom_icons)
        custom_icons = None