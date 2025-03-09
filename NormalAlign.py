import bpy
import bpy_extras
import numpy as np
import mathutils
from mathutils import Vector
def _(text):
    return bpy.app.translations.pgettext(text)


bpy.types.Scene.distance_threshold = bpy.props.FloatProperty(
        name="distance threshold",
        description=_("Threshold for searching for the nearest point"),
        default=0.2,
        min=-0,
        max=10,
)
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

    
    if obj.type in {'CURVE', 'META', 'SURFACE','MESH','FONT'}:

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
        vertices = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get("co", vertices)
        vertices = vertices.reshape(-1, 3)  # 将数组重塑为 Nx3 的形状

        # 将局部顶点转换到世界坐标系
        matrix_world_np = np.array(obj_copy.matrix_world)
        world_verts = np.dot(vertices, matrix_world_np[:3, :3].T) + matrix_world_np[:3, 3]

        world_verts_homogeneous = np.hstack((world_verts, np.ones((world_verts.shape[0], 1))))  # 转换为齐次坐标
        view_verts = np.dot(world_verts_homogeneous, view_matrix_np.T)  # 矩阵乘法
        view_verts = view_verts[:, :3]  # 去掉齐次坐标的最后一列

        
        bpy.data.objects.remove(obj_copy, do_unlink=True)# 删除复制体

        if flag:
            min_coords = np.min(view_verts, axis=0)
            max_coords = np.max(view_verts, axis=0)
            x_min, x_max = min_coords[0], max_coords[0]
            y_min, y_max = min_coords[1], max_coords[1]
            z_min, z_max = min_coords[2], max_coords[2]
            # view_verts = [view_matrix @ world_vert for world_vert in world_verts]
        else:
            min_coords = np.min(world_verts, axis=0)
            max_coords = np.max(world_verts, axis=0)
            x_min, x_max = min_coords[0], max_coords[0]
            y_min, y_max = min_coords[1], max_coords[1]
            z_min, z_max = min_coords[2], max_coords[2]

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
        else:
            min_coords = np.min(world_verts, axis=0)
            max_coords = np.max(world_verts, axis=0)
            x_min, x_max = min_coords[0], max_coords[0]
            y_min, y_max = min_coords[1], max_coords[1]
            z_min, z_max = min_coords[2], max_coords[2]
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

    return {
        'X': (x_min, x_max),'Y': (y_min, y_max),'Z': (z_min, z_max),
    }

bpy.types.Scene.enable_along_curve = bpy.props.BoolProperty(
    name="enable along curve",
    description=_("Enable alignment to the direction of the curve"),
    default=False,
)
bpy.types.Scene.enable_along_curve_XYZ = bpy.props.EnumProperty(
        name="enable along curve XYZ",
        description=_("Which direction should be aligned to the direction of the curve"),
        items=[
            ('X', "X", _("X along the normal direction of the curve")),
            ('Y', "Y", _("Y along the normal direction of the curve")),
            ('Z', "Z", _("Z along the normal direction of the curve")),
        ],
        default='X'
    ) # type: ignore


def find_nearest_intersection_and_tangent(curve_obj, axis, target_value, obj_location):

    # 获取曲线的评估版本（考虑所有修改器）
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = curve_obj.evaluated_get(depsgraph)

    # 将曲线转换为多段线（密集采样）
    mesh = eval_obj.to_mesh()
    vertices = [curve_obj.matrix_world @ v.co for v in mesh.vertices]
    eval_obj.to_mesh_clear()

    intersections = []
    tangents = []

    # 遍历所有线段，寻找交点
    for i in range(len(vertices) - 1):
        v1 = vertices[i]
        v2 = vertices[i + 1]

        # 获取线段在指定轴向上的范围
        axis_value1 = getattr(v1, axis)
        axis_value2 = getattr(v2, axis)
        # 检查目标值是否在线段的范围内
        if min(axis_value1, axis_value2) <= target_value <= max(axis_value1, axis_value2):
            # 计算插值比例
            t = (target_value - axis_value1) / (axis_value2 - axis_value1)
            # 计算交点
            intersection = v1.lerp(v2, t)
            
            # 计算切向向量（线段的方向）
            tangent = (v2 - v1).normalized()
            intersections.append(intersection)
            tangents.append(tangent)
    
    # 如果没有交点，返回 None
    if not intersections:
        print("没有交叉点")
        return None, None
    # 找到与物体最近的那个交点和切向向量
    nearest_index = min(range(len(intersections)), key=lambda i: (intersections[i] - obj_location).length)
    
    return intersections[nearest_index], tangents[nearest_index]

def OBJECT_OT_align_Curve(axis):
    scene = bpy.context.scene
    curve_obj = bpy.context.active_object
    axis=axis.lower()
    axis_tmp="z"
    if axis=="zx":
        axis="y"
        axis_tmp="z"
    elif axis=="zy":
        axis="x"
        axis_tmp="z"
    else:
        axis_tmp="v"

    # 获取选中的物体，并过滤掉活动物体
    selected_objects = [obj for obj in bpy.context.selected_objects if obj != curve_obj]

    # 遍历选中的物体
    for obj in selected_objects:
        # 获取物体在指定轴向上的坐标
        print(obj.location.x)
        target_value= getattr(obj.location, axis)
        # 找到曲线与物体在指定轴向上的最近交点及其切向向量
        intersection, tangent = find_nearest_intersection_and_tangent(curve_obj, axis, target_value, obj.location)

        if not intersection or not tangent:
            continue

        # 计算法向向量（假设法向垂直于切向）
        normal = Vector((-tangent.y, tangent.x, 0)).normalized()

        # 对齐物体的位置
        if axis == 'x':
            if axis_tmp != 'z':
                obj.location.y=intersection[1]
        elif axis == 'y':
            if axis_tmp != 'z':
                obj.location.x=intersection[0]
        if axis_tmp == 'z':
            obj.location.z=intersection[2]
            

        # 对齐物体的旋转
        if scene.enable_along_curve==True:
            if scene.enable_along_curve_XYZ=="X":
                print("转啊")
                rotation_matrix = normal.to_track_quat('Z', 'Y').to_matrix().to_4x4()
                obj.rotation_euler = rotation_matrix.to_euler()
            elif scene.enable_along_curve_XYZ=="Y":
                rotation_matrix = normal.to_track_quat('Y', 'Z').to_matrix().to_4x4()
                obj.rotation_euler = rotation_matrix.to_euler()
            elif scene.enable_along_curve_XYZ=="Z":
                rotation_matrix = normal.to_track_quat('X', 'Y').to_matrix().to_4x4()
                
                obj.rotation_euler = rotation_matrix.to_euler()


class OBJECT_OT_align_Normal(bpy.types.Operator):
    bl_idname = "object.align_normal"
    bl_label = "Extend  Alignment"
    bl_description = _("Align using extreme coordinates of internal data")
    bl_options = {'REGISTER', 'UNDO'} 
    
    #对齐参考对象设置
    bpy.types.Scene.align_reference = bpy.props.EnumProperty(
        name="AlignReference",
        description="Align Reference",
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
                no_closest_point=OBJECT_OT_align_Curve(axis)
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