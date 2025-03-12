# 面板

import bpy
import os
import gettext
import bpy.utils.previews

# def get_icons():
#     from . import icons 
#     return icons.custom_icons
from .icons import get_custom_icons
def _(text):
    return bpy.app.translations.pgettext(text)

class OBJECT_PT_AlignToolsPanel(bpy.types.Panel):
    bl_label = _("Align 2D")
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Align2D"
    
    def draw(self, context):
        custom_icons = get_custom_icons()
        layout = self.layout
        scene = context.scene
        
        row=layout.row(align=True)
        row.alignment="CENTER"
        row.label(text=_("Alignment"),icon_value=custom_icons["Alignment"].icon_id)
        
        box = layout.box()
        row = box.row()
     
        row.label(text=_("Reference:"),icon_value=custom_icons["Gear"].icon_id)
        row = box.row(align=True)
        
        row.prop(context.scene, "align_reference", expand=True)
        
        row = box.row(align=True)
        row.label(text=_("Use screen space:"),icon_value=custom_icons["Screen_2D"].icon_id)
        if scene.align_reference != "OPTION_4":
           
            row = box.row(align=True)
            row.alignment="CENTER"
            row.scale_x = 3
            row.scale_y = 1.2
            op = row.operator("object.align_normal", text="",icon_value=custom_icons["Align_up"].icon_id)  
            op.align_axial = 'Y'
            op.axial_direction = 'POSITIVE'
            op.align_axial_world = 'SCREEN'
            op = row.operator("object.align_normal", text="",icon_value=custom_icons["Align_down"].icon_id)  
            op.align_axial = 'Y'
            op.axial_direction = 'NEGATIVE'
            op.align_axial_world = 'SCREEN'
            op = row.operator("object.align_normal", text="",icon_value=custom_icons["Align_left"].icon_id)  
            op.align_axial = 'X'
            op.axial_direction = 'NEGATIVE'
            op.align_axial_world = 'SCREEN'
            op = row.operator("object.align_normal", text="",icon_value=custom_icons["Align_right"].icon_id)  
            op.align_axial = 'X'
            op.axial_direction = 'POSITIVE'
            op.align_axial_world = 'SCREEN'
            op = row.operator("object.align_normal", text="",icon_value=custom_icons["Horizontally_center"].icon_id)  
            op.align_axial = 'X'
            op.axial_direction = 'CENTER'
            op.align_axial_world = 'SCREEN'
            op = row.operator("object.align_normal", text="",icon_value=custom_icons["Vertical_center"].icon_id)  
            op.align_axial = 'Y'
            op.axial_direction = 'CENTER'
            op.align_axial_world = 'SCREEN'
            split = box.split(factor=0.5)
            left_col = split.column()


            row = left_col.row()
            row.scale_x = 0.6
            row.label(text=_("Use World Axis:"))
            col = left_col.column(align=True)
            row = col.row(align=True)
            row.scale_x = 1.5
            op = row.operator("object.align_normal", text="-X")
            op.align_axial = 'X'
            op.axial_direction = 'NEGATIVE'
            op.align_axial_world = 'WORLD'
            op = row.operator("object.align_normal", text="-X-")
            op.align_axial = 'X'
            op.axial_direction = 'CENTER'
            op.align_axial_world = 'WORLD'
            op = row.operator("object.align_normal", text="+X")
            op.align_axial = 'X'
            op.axial_direction = 'POSITIVE'
            op.align_axial_world = 'WORLD'

            row = col.row(align=True)
            row.scale_x = 1.5
            op = row.operator("object.align_normal", text="-Y")
            op.align_axial = 'Y'
            op.axial_direction = 'NEGATIVE'
            op.align_axial_world = 'WORLD'
            op = row.operator("object.align_normal", text="-Y-")
            op.align_axial = 'Y'
            op.axial_direction = 'CENTER'
            op.align_axial_world = 'WORLD'
            op = row.operator("object.align_normal", text="+Y")
            op.align_axial = 'Y'
            op.axial_direction = 'POSITIVE'
            op.align_axial_world = 'WORLD'

            row = col.row(align=True)
            row.scale_x = 1.5
            op = row.operator("object.align_normal", text="-Z")
            op.align_axial = 'Z'
            op.axial_direction = 'NEGATIVE'
            op.align_axial_world = 'WORLD'
            op = row.operator("object.align_normal", text="-Z-")
            op.align_axial = 'Z'
            op.axial_direction = 'CENTER'
            op.align_axial_world = 'WORLD'
            op = row.operator("object.align_normal", text="+Z")
            op.align_axial = 'Z'
            op.axial_direction = 'POSITIVE'
            op.align_axial_world = 'WORLD'

            right_col = split.column()
            row = right_col.row()
            row.scale_x = 0.6

            row.label(text=_("Copy rotation:"))
            col = right_col.column(align=True)
            row = col.row(align=True)
            op = row.operator("object.align_rotate_scale", text="X")
            op.align_axial = 'X'
            op.mode_LRS = 'XUANZHUAN'
            op = row.operator("object.align_rotate_scale", text="Y")
            op.align_axial = 'Y'
            op.mode_LRS = 'XUANZHUAN'
            op = row.operator("object.align_rotate_scale", text="Z")
            op.align_axial = 'Z'
            op.mode_LRS = 'XUANZHUAN'
            op = row.operator("object.align_rotate_scale", text="XYZ")
            op.align_axial = 'XYZ'
            op.mode_LRS = 'XUANZHUAN'

            row = col.row(align=True)
            row.scale_x = 1.5
            row.label(text=_("Copy scale:"))
            row = col.row(align=True)
            row.alignment="CENTER"
            op = row.operator("object.align_rotate_scale", text="X")
            op.align_axial = 'X'
            op.mode_LRS = 'SUOFANG'
            op = row.operator("object.align_rotate_scale", text="Y")
            op.align_axial = 'Y'
            op.mode_LRS = 'SUOFANG'
            op = row.operator("object.align_rotate_scale", text="Z")
            op.align_axial = 'Z'
            op.mode_LRS = 'SUOFANG'
            op = row.operator("object.align_rotate_scale", text="XYZ")
            op.align_axial = 'XYZ'
            op.mode_LRS = 'SUOFANG'
            row = box.row()
            
        else:
            
            row.prop(context.scene, "use_extreme", text=_("Use mesh boundary"))
            row = box.row(align=True)
            row.alignment="CENTER"
            row.scale_x = 3
            row.scale_y = 1.2
            op = row.operator("object.align_normal", text="",icon_value=custom_icons["Align_curveX2"].icon_id)  
            op.align_axial = 'Y'
            op.axial_direction = 'POSITIVE'
            op.align_axial_world = 'SCREEN'
            op = row.operator("object.align_normal", text="",icon_value=custom_icons["Align_curveX"].icon_id)  
            op.align_axial = 'Y'
            op.axial_direction = 'NEGATIVE'
            op.align_axial_world = 'SCREEN'
            op = row.operator("object.align_normal", text="",icon_value=custom_icons["Align_curveY"].icon_id)  
            op.align_axial = 'X'
            op.axial_direction = 'POSITIVE'
            op.align_axial_world = 'SCREEN'
            op = row.operator("object.align_normal", text="",icon_value=custom_icons["Align_curveY2"].icon_id)  
            op.align_axial = 'X'
            op.axial_direction = 'NEGATIVE'
            op.align_axial_world = 'SCREEN'
            row = box.row()
        row=layout.row()
        row.scale_y = 1.2
        row.operator("object.align_to_view", text=_("Align to View"),icon_value=custom_icons["Align_screen"].icon_id)
        row=layout.row()

#分布面板
class OBJECT_PT_DISTRIBUTE(bpy.types.Panel):
    bl_label = _("Distribute")
    bl_space_type = 'VIEW_3D'  
    bl_region_type = 'UI'  
    bl_category = "Align2D"
    # bl_parent_id = "OBJECT_PT_AlignToolsPanel"
    def draw(self, context):
        custom_icons = get_custom_icons()
        layout = self.layout
    
        scene = context.scene
        row = layout.row(align=True)
        row.alignment="CENTER"
        row.label(text=_("Linear distribution"),icon_value=custom_icons["Distribution_linear"].icon_id)
        box = layout.box()

        row = box.row()
        col = box.column()
        row.label(text=_("Use screen space:"),icon_value=custom_icons["Screen_2D"].icon_id)
        row = col.row()
        row = col.row(align=True)
        row.scale_x = 3
        row.scale_y = 1.2

        op = row.operator("object.linear_distribution", text=_("Horizontal"),icon_value=custom_icons["Distribute_horizontal"].icon_id)  
        op.distribute_axial = 'HORIZONTAL'
        op = row.operator("object.linear_distribution", text=_("Vertical"),icon_value=custom_icons["Distribute_vertical"].icon_id)  
        op.distribute_axial = 'VERTICAL'


        split = box.split(factor=0.5)

        col_left = split.column(align=True)
        col_left.prop(context.scene, "screen_order_sorting", text=_("Sort Order"))
        if scene.screen_order_sorting:
            row=col_left.row()
            row.prop(context.scene, "distribute_sorting_method", expand=True)

        col_right = split.column(align=True)
        row = col_right.row(align=True)
        row.prop(context.scene, "enable_custom_spacing", text=_("Custom gap"))
        
        if context.scene.enable_custom_spacing:
            row=col_right.row()
            row.prop(context.scene, "custom_spacing", text=_("Gap:"))
        row = box.row()

        ######################环形分布############################
        scene = context.scene
        row = layout.row()
        row = row.row(align=True)
        row.alignment="CENTER"
        row.label(text=_("Circle distribution"),icon_value=custom_icons["Distribution_cycle"].icon_id)
        box = layout.box()
        row = box.row()
        row.scale_y=0.6

        row.label(text=_("Align Axis:"))
        row = box.row(align=True)
        row.prop(scene, "Point_to_center_of_circle", text=_("Point to center of circle"),icon_value=custom_icons["Point_to_center"].icon_id)
        if scene.Point_to_center_of_circle:
            row = box.row(align=True)
            row.prop(scene, "arrange_circle_align_axis", expand=True)
            row.prop(scene, "reverse_alignment_axis", text=_("Reverse"),icon_value=custom_icons["Reverse"].icon_id)


        row = box.row(align=True)
        row.prop(scene, "arrange_circle_radius")
        row.prop(scene, "arrange_circle_angle_range")
        

        if not scene.auto_update_arrangement:
            row = box.row()
            row.scale_y=1.2
            row.operator("object.arrange_in_circle", text=_("Circular Arrange"),icon_value=custom_icons["Distribute_circular"].icon_id)
        else:
            row = box.row()
            row.scale_y=1.2
            row.label(text=_("Button resting"),icon_value=custom_icons["Eye_close"].icon_id)
        row.prop(scene, "auto_update_arrangement", text=_("Auto Update"),icon_value=custom_icons["Auto_run"].icon_id)
        row = box.row()
        row.operator("object.bind_to_empty", text=_("Bind to empty"),icon_value=custom_icons["Set_parent"].icon_id)
   

