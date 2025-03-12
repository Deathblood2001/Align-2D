import bpy
import gettext
def _(text):
    return bpy.app.translations.pgettext(text)
current_axis = 'X'

class OBJECT_OT_AlignRotateScale(bpy.types.Operator):
    bl_idname = "object.align_rotate_scale"
    bl_label = _("Rotate and Scale Alignment")
    bl_description = _("Align using data from active objects")
    bl_options = {'REGISTER', 'UNDO'} 

    align_axial:bpy.props.EnumProperty(
        items=[
            ('X', "axialX", ""),
            ('Y', "axialY", ""),
            ('Z', "axialZ", ""),
            ('XYZ', "axialXYZ", "")
        ],
        name="AlignAxial"
    ) # type: ignore

    mode_LRS: bpy.props.EnumProperty(
        name="modeLRS",
        items=[
            ('YIDONG', "location", ""),
            ('XUANZHUAN', "rotation", ""),
            ('SUOFANG', "scale", ""),
        ],
    )# type: ignore


    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        active_object = context.active_object

        if len(selected_objects) < 2:
            self.report({'ERROR'}, "Please select at least two objects!")
            return {'CANCELLED'}
        if not active_object or active_object not in selected_objects:
            self.report({'ERROR'}, "An active object must be selected!")
            return {'CANCELLED'}
        
        axis=self.align_axial
        LorRorS=self.mode_LRS

        global current_axis

        if LorRorS=='XUANZHUAN':
            if axis == 'XYZ':        
                for obj in context.selected_objects:
                    if obj != active_object:
                        obj.rotation_euler=active_object.rotation_euler
            else:
                active_axis_value = getattr(active_object.rotation_euler, axis.lower())
                for obj in context.selected_objects:
                    if obj != active_object:
                        setattr(obj.rotation_euler, axis.lower(), active_axis_value)

        elif LorRorS=='SUOFANG':
            if axis == 'XYZ':        
                for obj in context.selected_objects:
                    if obj != active_object:
                        obj.scale=active_object.scale
            else:
                active_axis_value = getattr(active_object.scale, axis.lower())
                for obj in context.selected_objects:
                    if obj != active_object:
                        setattr(obj.scale, axis.lower(), active_axis_value)
        return {'FINISHED'} 
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 1