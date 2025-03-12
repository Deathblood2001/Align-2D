import bpy
import os
import gettext
import math
from mathutils import Vector, Matrix
def _(text):
    return bpy.app.translations.pgettext(text)


def update_arrangement(self, context):
    if context.scene.auto_update_arrangement:
        arrange_in_circle(
            context.scene.arrange_circle_radius,
            context.scene.arrange_circle_angle_range,
            context.scene.arrange_circle_align_axis
        )

bpy.types.Scene.arrange_circle_radius = bpy.props.FloatProperty(
    name="Radius",
    default=2.0,
    min=0.01,
    description=_("Radius of the circle"),
    update=update_arrangement  
)

bpy.types.Scene.arrange_circle_angle_range = bpy.props.FloatProperty(
    name=_("Angle Range"),
    default=360.0,
    min=0.0,
    max=360.0,
    description=_("Angle range of the circle"),
    update=update_arrangement  
)

bpy.types.Scene.arrange_circle_align_axis = bpy.props.EnumProperty(
    name="Align Axis",
    items=[
        ('X', "X", _("Align X axis to center")),
        ('Y', "Y", _("Align Y axis to center")),
        ('Z', "Z", _("Align Z axis to center"))
    ],
    default='X',
    description=_("Axis to align towards the center"),
    update=update_arrangement  
)

bpy.types.Scene.auto_update_arrangement = bpy.props.BoolProperty(
    name="Auto Update",
    default=False,
    description=_("Automatically update arrangement when properties change")
)
bpy.types.Scene.Point_to_center_of_circle = bpy.props.BoolProperty(
    name="Auto Update",
    default=False,
    description=_("The object points towards the center of the circle")
)

bpy.types.Scene.reverse_alignment_axis = bpy.props.BoolProperty(
    name="Reverse alignment axis",
    default=False,
    description=_("Reverse alignment axis"),
    update=update_arrangement 
)

def arrange_in_circle(radius, angle_range, align_axis):
    scene = bpy.context.scene
    selected_objects = bpy.context.selected_objects
    
    region_data = None
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            region_data = area.spaces.active.region_3d
            break
    if region_data:
        view_matrix = region_data.view_matrix

    view_rotation = view_matrix.to_3x3().inverted()
    
    cursor_location = bpy.context.scene.cursor.location
    
    num_objects = len(selected_objects)
    angle_step = angle_range / num_objects if num_objects > 1 else 0
    
    for i, obj in enumerate(selected_objects):
        angle = math.radians(-angle_range / 2 + i * angle_step)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = 0
        
        local_position = Vector((x, y, z))
        world_position = view_rotation @ local_position + cursor_location
        obj.location = world_position
        
        direction = cursor_location - obj.location
        direction.normalize()
        
        if scene.reverse_alignment_axis:
            direction = -direction
        if scene.Point_to_center_of_circle:
            view_normal = view_rotation @ Vector((0, 0, 1))
            view_normal.normalize()
            
            if align_axis == 'X':

                y_axis = view_normal.cross(direction).normalized()
                z_axis = direction.cross(y_axis).normalized()
                rotation_matrix = Matrix().to_3x3()
                rotation_matrix.col[0] = direction
                rotation_matrix.col[1] = y_axis
                rotation_matrix.col[2] = z_axis
            elif align_axis == 'Y':

                z_axis = view_normal.cross(direction).normalized()
                x_axis = direction.cross(z_axis).normalized()
                rotation_matrix = Matrix().to_3x3()
                rotation_matrix.col[0] = x_axis
                rotation_matrix.col[1] = direction
                rotation_matrix.col[2] = z_axis
            elif align_axis == 'Z':

                y_axis = view_normal.cross(direction).normalized()
                x_axis = y_axis.cross(direction).normalized()
                rotation_matrix = Matrix().to_3x3()
                rotation_matrix.col[0] = x_axis
                rotation_matrix.col[1] = y_axis
                rotation_matrix.col[2] = direction

            obj.rotation_euler = rotation_matrix.to_euler()

def bind_to_empty():
    scene = bpy.context.scene
    selected_objects = bpy.context.selected_objects
    if not selected_objects:
        return
    
    cursor_location = bpy.context.scene.cursor.location
    
    empty = bpy.data.objects.new("Empty", None)
    empty.location = cursor_location
    bpy.context.collection.objects.link(empty)
    for obj in selected_objects:
        obj.location = obj.location-empty.location
        obj.parent = empty
    scene.auto_update_arrangement=False

class BIND_TO_EMPTY_OT_Operator(bpy.types.Operator):
    bl_idname = "object.bind_to_empty"
    bl_label = _("Bind to Empty")
    bl_description = _("Create an empty object and select the object as a subset of the empty objects")
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        if len(selected_objects) < 2:
            self.report({'ERROR'}, "Select at least 2 objects!")
            return {'CANCELLED'}
        bind_to_empty()
    
        return {'FINISHED'}
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 2
            
class ARRANGE_CIRCLE_OT_Operator(bpy.types.Operator):
    bl_idname = "object.arrange_in_circle"
    bl_label = _("Arrange in Circle")
    bl_description = _("Distribute the selected objects in a circular pattern at the cursor")
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        selected_objects = bpy.context.selected_objects
        if len(selected_objects) < 2:
            self.report({'ERROR'}, _("Select at least 2 objects!"))
            return {'CANCELLED'}
    
        arrange_in_circle(
            scene.arrange_circle_radius,
            scene.arrange_circle_angle_range,
            scene.arrange_circle_align_axis
        )
        return {'FINISHED'}
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 2
