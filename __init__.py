bl_info = {
    "name": "Align2D-BLCN",
    "author": "BlenderCN-DB",
    "version": (0, 0, 4),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Edit Tab / Edit Mode Context Menu",
    "description": "Alignment based on screen coordinate system",
    "doc_url": "https://www.blendercn.org/",
    "category": "Mesh",
}

import os
import bpy
import gettext
import bpy.utils.previews
from .Translation import translations_dict
from bpy.app.handlers import persistent
from bpy.types import (
        Operator,
        Panel,
        AddonPreferences,
        )
from bpy.props import (
        StringProperty,
        )


from . import icons
from .NormalAlign import OBJECT_OT_align_Normal,OBJECT_OT_Align_To_View
from .RotateScaleAlign import OBJECT_OT_AlignRotateScale
from .Distribution import OBJECT_OT_LinearDistribution
from .CircularDistribution import ARRANGE_CIRCLE_OT_Operator,BIND_TO_EMPTY_OT_Operator
from .Panels import OBJECT_PT_AlignToolsPanel, OBJECT_PT_DISTRIBUTE


def _(text):
    return bpy.app.translations.pgettext(text)


panels = [OBJECT_PT_AlignToolsPanel,OBJECT_PT_DISTRIBUTE]

def update_panel(self, context):
    message = _("Updating Panel locations has failed")
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        for panel in panels:
            panel.bl_category = context.preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass

class AlignAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    category: StringProperty(
        name=_("Tab Category"),
        description=_("Choose a name for the category of the panel"),
        default="Align2D",
        update=update_panel
    )# type: ignore

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column()

        col.label(text=_("Custom Tab Category:"))
        col.prop(self, "category", text="")


classes = (
    
    OBJECT_PT_DISTRIBUTE,
    OBJECT_OT_align_Normal,
    OBJECT_OT_Align_To_View,
    OBJECT_OT_AlignRotateScale,
    OBJECT_OT_LinearDistribution,
    ARRANGE_CIRCLE_OT_Operator,
    BIND_TO_EMPTY_OT_Operator,
    AlignAddonPreferences,
    OBJECT_PT_AlignToolsPanel,
)



def register():

    icons.register()

    for cls in classes:
        bpy.utils.register_class(cls)

    update_panel(None, bpy.context)

    bpy.app.translations.register(__name__,  translations_dict)

    
    

def unregister():
    # 清理图标
    # if icons.custom_icons is not None:
    #     bpy.utils.previews.remove(icons.custom_icons)
    #     icons.custom_icons = None
    icons.unregister()
    bpy.app.translations.unregister(__name__)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


    

if __name__ == "__main__":
    register()