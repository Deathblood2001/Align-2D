import bpy
import numpy as np
import mathutils
from . import NormalAlign
from mathutils import Vector
def _(text):
    return bpy.app.translations.pgettext(text)
bpy.types.Scene.custom_spacing = bpy.props.FloatProperty(
        name="spacing",
        description=_("The gap between objects"),
        default=1.0,
        min=-100.0,
        max=100.0,
)
bpy.types.Scene.enable_custom_spacing = bpy.props.BoolProperty(
    name="Enable custom Spacing",
    description=_("Enable or disable custom gap for distribution"),
    default=False,
)
bpy.types.Scene.screen_order_sorting = bpy.props.BoolProperty(
    name="Screen Order Sorting",
    description=_("Calculate based on the left and up order on the screen"),
    default=False,
)
#添加坐标系切换
bpy.types.Scene.distribute_sorting_method = bpy.props.EnumProperty(
        name="Sorting method",
        description="Sort objects in chronological order",
        items=[
            ('LeftToRight', "→", _("Left To Right")),
            ('RightToLeft', "←", _("Right To Left")),
            ('TopToBottom', "↓", _("Top To Bottom")),
            ('BottomToTop', "↑", _("Bottom To Top")),
        ],
        default='LeftToRight',
    ) # type: ignore

class OBJECT_OT_LinearDistribution(bpy.types.Operator):
    bl_idname = "object.linear_distribution"
    bl_label = "Linear Distribution"
    bl_description = _("Distribution using extreme coordinates of objects")
    bl_options = {'REGISTER', 'UNDO'}
    
    # 对齐轴对象设置
    distribute_axial:bpy.props.EnumProperty(
        items=[
            ('HORIZONTAL', _("HORIZONTAL"), ""),
            ('VERTICAL', _("VERTICAL"), ""),
        ],
        name="AlignAxial"
    )  # type: ignore

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.active_object
        if len(selected_objects) < 3:
            self.report({'ERROR'}, _("Please select at least 3 objects!"))
            return {'CANCELLED'}
        
        axis = self.distribute_axial

        if axis == "HORIZONTAL":
            distribute_objects('HORIZONTAL',True)#True为屏幕坐标False为世界坐标
        elif axis == "VERTICAL":
            distribute_objects('VERTICAL',True)

        bpy.context.view_layer.objects.active = active_object    


        return {'FINISHED'}
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 2



def distribute_objects(axis,method):
    region_data = None
    scene = bpy.context.scene
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            region_data = area.spaces.active.region_3d
            break
    view_matrix = region_data.view_matrix
    if axis=='HORIZONTAL':
        axis="X"

    elif axis=='VERTICAL':
        axis="Y"

    
    selected_objects = bpy.context.selected_objects
    active_object = bpy.context.active_object
    extremes = []
    #获取所有物体的轴向上的极值
    for obj in selected_objects:
        obj_extremes = NormalAlign.get_geometry_extremes(obj,method)
        extremes.append((obj_extremes[axis][0], obj_extremes[axis][1], obj))

    # 找到最小和最大极值对应的物体，提取该元素中的物体本身 (obj)，并将其赋值给obj
    min_obj = min(extremes, key=lambda x: x[0])[2]
    max_obj = max(extremes, key=lambda x: x[1])[2]

    if scene.enable_custom_spacing:
        middle_objects = [obj for obj in selected_objects if obj != min_obj]    #如果用了自定义间距，那么最大物体可以不用过滤掉
    else:
        middle_objects = [obj for obj in selected_objects if obj != min_obj and obj != max_obj]

    total_middle_length = 0

    for obj in middle_objects:
        obj_extremes = NormalAlign.get_geometry_extremes(obj,method)
        #获取可移动物体的整体长度
        total_middle_length += obj_extremes[axis][1] - obj_extremes[axis][0]

    #输出最大最小物体的数据(min_value, max_value, obj)
    min_obj_extremes = next((item for item in extremes if item[2] == min_obj), None)
    max_obj_extremes = next((item for item in extremes if item[2] == max_obj), None)
  
    total_gap = max_obj_extremes[0] - min_obj_extremes[1]  #中间总空隙

    if scene.enable_custom_spacing:
        spacing =scene.custom_spacing
    else:
        spacing = (total_gap - total_middle_length) / (len(middle_objects) + 1)

    # 获取最小物体的位置保存为第一个起点
    current_position = min_obj_extremes[1]

    """ 如果自动排序打开 """
    if scene.screen_order_sorting: 
        
        sorted_objects=None
        view_coords_data = []
        
        #把选择物体的坐标换成视图坐标
        for obj in selected_objects:
                world_coords = obj.matrix_world.translation
                view_coords = view_matrix @ world_coords
                view_coords_data.append((view_coords.x,view_coords.y, obj))

        np_view_coords = np.array(view_coords_data)
  

        obj_orderX = np.argsort(np_view_coords[:, 0]) # 获取 X 方向的物体顺序（按 X 坐标值从小到大排序）
        obj_orderY = np.argsort(np_view_coords[:, 1]) # 获取 Y 方向的物体顺序
        # 获取排序后的物体列表
        sorted_objects_temporaryX =[selected_objects[i] for i in obj_orderX]   
        sorted_objects_temporaryY =[selected_objects[i] for i in obj_orderY]   

        if scene.enable_custom_spacing:
            sorted_objects_removeX = sorted_objects_temporaryX[1:]#去掉第一个
            sorted_objects_removeY = sorted_objects_temporaryY[1:]
        else:
            sorted_objects_removeX = sorted_objects_temporaryX[1:-1]#去掉头尾
            sorted_objects_removeY = sorted_objects_temporaryY[1:-1]

        if scene.distribute_sorting_method=="LeftToRight":
            sorted_objects = sorted_objects_removeX
        elif scene.distribute_sorting_method=="RightToLeft":
            sorted_objects = sorted_objects_removeX[::-1]
        elif scene.distribute_sorting_method=="TopToBottom":
            sorted_objects = sorted_objects_removeY
        elif scene.distribute_sorting_method=="BottomToTop":
            sorted_objects = sorted_objects_removeY[::-1]
         
    else:
        extremes = []
        for obj in middle_objects:
            obj_extremes = NormalAlign.get_geometry_extremes(obj, method)
            min_value = obj_extremes[axis][0]  # 获取指定轴向上的最小值
            extremes.append((min_value, obj))  # 存储最小值和物体

        sorted_objects = [obj for _, obj in sorted(extremes, key=lambda x: x[0])]


##########################################走位开始###############################################
    for obj in sorted_objects:
        obj_extremes = NormalAlign.get_geometry_extremes(obj,method)
        obj_length = obj_extremes[axis][1] - obj_extremes[axis][0] #获取物体的长度
        obj_center = (obj_extremes[axis][0] + obj_extremes[axis][1]) / 2 #获取物体中心位置的坐标
        if method:
            if axis == 'X':
                matrix =obj.matrix_world
                local_pos = view_matrix @ matrix.translation
                local_pos.x += (current_position + spacing + obj_length / 2) - obj_center
                obj.location=view_matrix.inverted() @ local_pos
            elif axis == 'Y':
                matrix =obj.matrix_world
                local_pos = view_matrix @ matrix.translation
                local_pos.y += (current_position + spacing + obj_length / 2) - obj_center
                obj.location=view_matrix.inverted() @ local_pos
        else:
            if axis == 'X':
                obj.location.x += (current_position + spacing + obj_length / 2) - obj_center
            elif axis == 'Y':
                obj.location.y += (current_position + spacing + obj_length / 2) - obj_center
            elif axis == 'Z':
                obj.location.z += (current_position + spacing + obj_length / 2) - obj_center

        # 更新当前位置递进
        current_position += spacing + obj_length
    bpy.context.view_layer.objects.active = active_object
    return {'FINISHED'}
