import bpy
import numpy as np
import mathutils
from mathutils import Vector
from bpy_extras import view3d_utils
def _(text):
    return bpy.app.translations.pgettext(text)

# 获取物体的几何极值,会获得两套数据，一套是世界坐标，一套是屏幕坐标
def get_geometry_extremes(obj,flag=True):
    world_verts = []
    view_verts = []

    # 获取 3D 视口的视图矩阵
    region_data = None
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            region_data = area.spaces.active.region_3d
            break
    if region_data:
        view_matrix = region_data.view_matrix
        view_matrix_np = np.array(view_matrix) 
        matrix = obj.matrix_world

        
    if obj.type in {'CURVE','SURFACE','MESH','FONT'}:

        obj_copy = obj.copy()
        obj_copy.data = obj.data.copy() 

        bpy.context.collection.objects.link(obj_copy)
        bpy.context.view_layer.objects.active = obj_copy
        obj_copy.select_set(True)
        # 获取评估对象
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj_copy.evaluated_get(depsgraph)
        # 将顶点数据转换为 NumPy 数组
        mesh = eval_obj.to_mesh()
        if len(mesh.vertices) == 0:
            print("警告：转换后的网格没有顶点。")
            eval_obj.to_mesh_clear()
            return None

        vertices = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get("co", vertices)
        vertices = vertices.reshape(-1, 3)  # 将数组重塑为 Nx3 的形状

        # 将局部顶点转换到世界坐标系
        matrix_world_np = np.array(obj_copy.matrix_world)
        world_verts = np.dot(vertices, matrix_world_np[:3, :3].T) + matrix_world_np[:3, 3]

        world_verts_homogeneous = np.hstack((world_verts, np.ones((world_verts.shape[0], 1))))  
        view_verts = np.dot(world_verts_homogeneous, view_matrix_np.T)  # 矩阵乘法

        view_verts = view_verts[:, :3]  # 去掉齐次坐标的最后一列

        eval_obj.to_mesh_clear()
        bpy.data.objects.remove(obj_copy, do_unlink=True)# 删除复制体

        if flag:
            min_coords = np.min(view_verts, axis=0)
            max_coords = np.max(view_verts, axis=0)
            x_min, x_max = min_coords[0], max_coords[0]
            y_min, y_max = min_coords[1], max_coords[1]
            z_min, z_max = min_coords[2], max_coords[2]
            # view_verts = [view_matrix @ world_vert for world_vert in world_verts]
            # 找到极值点的完整坐标
            x_min_point = view_verts[np.argmin(view_verts[:, 0])]
            x_max_point = view_verts[np.argmax(view_verts[:, 0])]
            y_min_point = view_verts[np.argmin(view_verts[:, 1])]
            y_max_point = view_verts[np.argmax(view_verts[:, 1])]
        else:
            min_coords = np.min(world_verts, axis=0)
            max_coords = np.max(world_verts, axis=0)
            x_min, x_max = min_coords[0], max_coords[0]
            y_min, y_max = min_coords[1], max_coords[1]
            z_min, z_max = min_coords[2], max_coords[2]

            x_min_point = world_verts[np.argmin(world_verts[:, 0])]
            x_max_point = world_verts[np.argmax(world_verts[:, 0])]
            y_min_point = world_verts[np.argmin(world_verts[:, 1])]
            y_max_point = world_verts[np.argmax(world_verts[:, 1])]

    elif obj.type =='GPENCIL' or obj.type =='GREASEPENCIL':
        #版本小于4.3使用老的api
        global blender_version, target_version
        blender_version = bpy.app.version
        target_version = (4, 3, 0)

        matrix_world_np = np.array(obj.matrix_world)
        world_verts = []
        gpencil = obj.data
        if blender_version < target_version:
            for layer in gpencil.layers:
                if not layer.hide:  
                    for frame in layer.frames:
                        for stroke in frame.strokes:
                            for point in stroke.points:
                                local_co = np.array(point.co)
                                local_co_homogeneous = np.append(local_co, 1.0)
                                world_co = np.dot(matrix_world_np, local_co_homogeneous)[:3]
                                world_verts.append(world_co)
            world_verts = np.array(world_verts)
            world_verts_homogeneous = np.hstack((world_verts, np.ones((world_verts.shape[0], 1))))
            view_verts = np.dot(world_verts_homogeneous, view_matrix_np.T)[:, :3]
        else:
             #版本大于4.3使用新的api  
            for layer in gpencil.layers:
                if not layer.hide:  
                    for frame in layer.frames:
                        for stroke in frame.drawing.strokes:
                            for point in stroke.points:
                                local_co = np.array(point.position)
                                local_co_homogeneous = np.append(local_co, 1.0)
                                world_co = np.dot(matrix_world_np, local_co_homogeneous)[:3]
                                world_verts.append(world_co)
            world_verts = np.array(world_verts)
            world_verts_homogeneous = np.hstack((world_verts, np.ones((world_verts.shape[0], 1))))
            view_verts = np.dot(world_verts_homogeneous, view_matrix_np.T)[:, :3]
        if flag:
            min_coords = np.min(view_verts, axis=0)
            max_coords = np.max(view_verts, axis=0)
            x_min, x_max = min_coords[0], max_coords[0]
            y_min, y_max = min_coords[1], max_coords[1]
            z_min, z_max = min_coords[2], max_coords[2]
            x_min_point = view_verts[np.argmin(view_verts[:, 0])]
            x_max_point = view_verts[np.argmax(view_verts[:, 0])]
            y_min_point = view_verts[np.argmin(view_verts[:, 1])]
            y_max_point = view_verts[np.argmax(view_verts[:, 1])]
        else:
            min_coords = np.min(world_verts, axis=0)
            max_coords = np.max(world_verts, axis=0)
            x_min, x_max = min_coords[0], max_coords[0]
            y_min, y_max = min_coords[1], max_coords[1]
            z_min, z_max = min_coords[2], max_coords[2]
            x_min_point = world_verts[np.argmin(world_verts[:, 0])]
            x_max_point = world_verts[np.argmax(world_verts[:, 0])]
            y_min_point = world_verts[np.argmin(world_verts[:, 1])]
            y_max_point = world_verts[np.argmax(world_verts[:, 1])]
    else:
        if flag:
            world_location = obj.location
            location = view_matrix @ world_location
        else:
            world_location = obj.location
            location = world_location
        x_min, x_max = location.x, location.x
        y_min, y_max = location.y, location.y
        z_min, z_max = location.z, location.z

        x_min_point = location
        x_max_point = location
        y_min_point = location
        y_max_point = location

    return {
        'X': (x_min, x_max),
        'Y': (y_min, y_max),
        'Z': (z_min, z_max),
        'x_min_point': x_min_point,
        'x_max_point': x_max_point,
        'y_min_point': y_min_point,
        'y_max_point': y_max_point,
    }

bpy.types.Scene.use_extreme = bpy.props.BoolProperty(
    name="use extreme",
    description=_("Align using extreme values"),
    default=True,
)


def find_nearest_intersection_and_tangent(curve_obj, axis, target_value, obj_location):
    region_data = None
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            region_data = area.spaces.active.region_3d
            break
    if region_data:
        view_matrix = region_data.view_matrix

    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = curve_obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    vertices_world = [curve_obj.matrix_world @ v.co for v in mesh.vertices]
    vertices = [view_matrix @ v for v in vertices_world]
    eval_obj.to_mesh_clear()

    intersections = []
    tangents = []

    for i in range(len(vertices) - 1):
        v1 = vertices[i]
        v2 = vertices[i + 1]

        axis_value1 = getattr(v1, axis)
        axis_value2 = getattr(v2, axis)

        if min(axis_value1, axis_value2) <= target_value <= max(axis_value1, axis_value2):

            t = (target_value - axis_value1) / (axis_value2 - axis_value1)
            intersection = v1.lerp(v2, t)
            intersections.append(intersection)
            #曲线方向计算，保留
            tangent = (v2 - v1).normalized()
            tangents.append(tangent)
    
    if not intersections:
        print("There are no intersections")
        return None, None
    
    nearest_index = min(range(len(intersections)), key=lambda i: (intersections[i] -view_matrix @ obj_location).length)
    
    return intersections[nearest_index], tangents[nearest_index]

def OBJECT_OT_align_Curve(axis,direction):
    scene = bpy.context.scene
    region_data = None
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            region_data = area.spaces.active.region_3d
            break
    if region_data:
        view_matrix = region_data.view_matrix

    curve_obj = bpy.context.active_object
    axis=axis.lower()
    selected_objects = [obj for obj in bpy.context.selected_objects if obj != curve_obj]

#极值算法
    for obj in selected_objects:
        obj_extremes = get_geometry_extremes(obj,True)
        if scene.use_extreme:
            if direction=="POSITIVE":
                if axis == 'y':
                    target_value = obj_extremes['x_min_point'][1]
                elif axis == 'x':
                    target_value = obj_extremes['y_min_point'][0]
            else:
                if axis == 'y':
                    target_value = obj_extremes['x_max_point'][1]
                elif axis == 'x':
                    target_value = obj_extremes['y_max_point'][0]
        else:
            target_value = getattr(view_matrix @ obj.location, axis)
        
        intersection, tangent = find_nearest_intersection_and_tangent(curve_obj, axis, target_value, obj.location)
        
        if not intersection or not tangent:
            continue

        # normal = Vector((-tangent.y, tangent.x, 0)).normalized()

        center_view = view_matrix @ obj.location
        if scene.use_extreme:
            if direction=="POSITIVE":
                if axis == 'y':
                    offsetX = obj_extremes['X'][0] - center_view.x
                    offsetY = obj_extremes['x_min_point'][1] - center_view.y
                    intersection[0] -= offsetX
                    intersection[1] -= offsetY
                elif axis == 'x':
                    offsetX = obj_extremes['Y'][0] - center_view.y
                    offsetY = obj_extremes['y_min_point'][0] - center_view.x
                    intersection[1] -= offsetX
                    intersection[0] -= offsetY
            else:
                if axis == 'y':
                    offsetX = obj_extremes['X'][1] - center_view.x
                    offsetY = obj_extremes['x_max_point'][1] - center_view.y
                    intersection[0] -= offsetX
                    intersection[1] -= offsetY
                elif axis == 'x':
                    offsetX = obj_extremes['Y'][1] - center_view.y
                    offsetY = obj_extremes['y_max_point'][0] - center_view.x
                    intersection[1] -= offsetX
                    intersection[0] -= offsetY
            intersection[2] = center_view.z
            obj.location=view_matrix.inverted() @ intersection    
        else:
            
            if axis == 'x':
                    center_view.y=intersection[1]
            elif axis == 'y':
                    center_view.x=intersection[0]
            obj.location=view_matrix.inverted() @ center_view
           
    
            


class OBJECT_OT_align_Normal(bpy.types.Operator):
    bl_idname = "object.align_normal"
    bl_label = _("Screen space alignment")
    bl_description = _("Align using extreme coordinates of internal data")
    bl_options = {'REGISTER', 'UNDO'} 
    
    #对齐参考对象设置
    bpy.types.Scene.align_reference = bpy.props.EnumProperty(
        name="AlignReference",
        description=_("Align Reference"),
        items=[
            ('OPTION_1', _("MinMax"), ""),
            ('OPTION_2', "Active", ""),
            ('OPTION_3', "3D Cursor", ""),
            ('OPTION_4', "Curve", ""),
        ],
        default='OPTION_1'
    ) # type: ignore

    align_axial_world:bpy.props.EnumProperty(
        items=[
            ('SCREEN', "axialscreen", ""),
            ('WORLD', "axialworld", ""),
        ],
        default='SCREEN',
        name="AlignAxialWorld"
    ) # type: ignore

    # 对齐轴对象设置
    align_axial:bpy.props.EnumProperty(
        items=[
            ('X', "axialX", ""),
            ('Y', "axialY", ""),
            ('Z', "axialZ", ""),
            ('ZX', "axialZX", ""),
            ('ZY', "axialZY", ""),
        ],
        name="AlignAxial"
    ) # type: ignore
    #对齐轴正反设置
    
    axial_direction:bpy.props.EnumProperty(
        items=[
            ('POSITIVE', "POSITIVE", ""),
            ('CENTER', "CENTER", ""),
            ('NEGATIVE', "NEGATIVE", "")
        ],
        name="AxialDirection"
    ) # type: ignore

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.active_object
        
        if not selected_objects:
            self.report({'WARNING'}, _("No object selected!"))
            return {'CANCELLED'}

        #变量放这里
        selected_reference = context.scene.align_reference
        direction = self.axial_direction
        axis = self.align_axial
        axisworld = self.align_axial_world

        region_data = None
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                region_data = area.spaces.active.region_3d
                break
        if region_data is None:
            self.report({'ERROR'}, _("3D viewport not found!"))
            return None

        view_matrix = region_data.view_matrix
        ################################## MinMax ################################################
        if selected_reference == 'OPTION_1':
            
            if len(selected_objects) < 2:
                self.report({'ERROR'}, _("Select at least 2 objects!"))
                return {'CANCELLED'}
            

            extremes = []
            for obj in selected_objects:
                if axisworld=='SCREEN':
                    obj_extremes = get_geometry_extremes(obj,True)
                else:
                    obj_extremes = get_geometry_extremes(obj,False)
  
                #追加获取到的minmax数据和名称，0为小数据，1为大数据，2为物体名称
                extremes.append((obj_extremes[axis][0], obj_extremes[axis][1], obj))

            if direction == 'POSITIVE':
                active_extreme = max(extremes, key=lambda x: x[1])[1]

            elif direction == 'NEGATIVE':
                active_extreme = min(extremes, key=lambda x: x[0])[0]

            elif direction == 'CENTER':
                min_extreme = min(extremes, key=lambda x: x[0])[0]
                max_extreme = max(extremes, key=lambda x: x[1])[1]
                active_extreme = (min_extreme + max_extreme) / 2

        # ##################################### Active ################################################
        elif selected_reference == 'OPTION_2':
            if not active_object:
                self.report({'WARNING'}, _("No active object!"))
                return {'CANCELLED'}

            #获取活动物体的极值   
            if axisworld=='SCREEN':
                active_extremes = get_geometry_extremes(active_object,True)
            else:
                active_extremes = get_geometry_extremes(active_object,False)
            
            if direction == 'POSITIVE':
                active_extreme = active_extremes[axis][1]
            elif direction == 'NEGATIVE':
                active_extreme = active_extremes[axis][0]
            elif direction == 'CENTER':
                active_extreme = (active_extremes[axis][0] + active_extremes[axis][1]) / 2

        # # ################################### 3D Cursor ###############################################
        elif selected_reference == 'OPTION_3':
            if axisworld=='SCREEN':
                cursor_location = bpy.context.scene.cursor.location
                local_pos =view_matrix @ cursor_location
            else:
                cursor_location = bpy.context.scene.cursor.location
                local_pos =cursor_location
            if axis == 'X':
                active_extreme = local_pos.x
            elif axis == 'Y':
                active_extreme = local_pos.y
            elif axis == 'Z':
                active_extreme = local_pos.z

        # # ################################### Curve ###############################################
        elif selected_reference == 'OPTION_4':#曲线模式

            if active_object and active_object.type in {'CURVE'}:
                no_closest_point=OBJECT_OT_align_Curve(axis,direction)
            else:
                self.report({'ERROR'}, _("Active object must be a Curve!"))
                return {'CANCELLED'}


        #对齐执行代码
        if selected_reference == 'OPTION_4':
            
            if no_closest_point==True:
                self.report({'ERROR'}, _("Increasing the resolutionU of the curve can improve the search accuracy!"))
        else:
            for obj in selected_objects:
                if selected_reference == 'OPTION_2' and obj == bpy.context.active_object:
                    continue
                if axisworld=='SCREEN':
                    obj_extremes = get_geometry_extremes(obj,True)
                else:
                    obj_extremes = get_geometry_extremes(obj,False)
                    
                if obj_extremes:
                    if direction == 'POSITIVE':
                        obj_extreme = obj_extremes[axis][1]  # 正方向
                    elif direction == 'NEGATIVE':
                        obj_extreme = obj_extremes[axis][0]  # 负方向
                    elif direction == 'CENTER':
                        obj_extreme = (obj_extremes[axis][0] + obj_extremes[axis][1]) / 2  # 中间
                else:
                    obj_extreme = obj.location[0 if axis == 'X' else 1 if axis == 'Y' else 2]
                
                offset = active_extreme - obj_extreme
                
                if axisworld=='SCREEN':
                    if axis == 'X':
                        matrix =obj.matrix_world
                        local_pos = view_matrix @ matrix.translation
                        local_pos.x += offset
                        obj.location=view_matrix.inverted() @ local_pos
                    elif axis == 'Y':
                        matrix =obj.matrix_world
                        local_pos = view_matrix @ matrix.translation
                        local_pos.y += offset
                        obj.location=view_matrix.inverted() @ local_pos
                    elif axis == 'Z':
                        matrix =obj.matrix_world
                        local_pos = view_matrix @ matrix.translation
                        local_pos.z += offset
                        obj.location=view_matrix.inverted() @ local_pos
                else:
                    if axis == 'X':
                        obj.location.x += offset
                    elif axis == 'Y':
                        obj.location.y += offset
                    elif axis == 'Z':
                        obj.location.z += offset

        bpy.context.view_layer.objects.active = active_object    

        return {'FINISHED'}
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 1
    
class OBJECT_OT_Align_To_View(bpy.types.Operator):
    bl_idname = "object.align_to_view" 
    bl_label = _("Align to View")  
    bl_description = _("Align selected objects to the current view plane")   
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):
        rv3d = context.region_data
        if rv3d is None:
            self.report({'ERROR'}, "Please make sure to run this operation in the 3D view")
            return {'CANCELLED'}

        view_normal = rv3d.view_rotation @ mathutils.Vector((0, 0, -1))

        selected_objects = context.selected_objects

        for obj in selected_objects:
            obj_location = obj.location
            # 将物体的位置投影到视图平面上
            projected_location = obj_location - (obj_location.dot(view_normal)) * view_normal
            obj.location = projected_location
        context.view_layer.update()
        return {'FINISHED'}
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 1