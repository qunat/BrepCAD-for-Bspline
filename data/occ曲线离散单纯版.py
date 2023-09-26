from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.TColgp import TColgp_HArray1OfPnt
from OCC.Core.gp import gp_Pnt
from OCC.Display.SimpleGui import init_display
from OCC.Core.TColgp import TColgp_HArray1OfPnt
from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.gp import gp_Pnt
from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Pnt, gp_Pnt2d, gp_OX2d
from OCC.Core.Geom2d import Geom2d_Circle
import numpy as np
#import open3d as o3d
import vtk
from OCC.Core.Geom2dAdaptor import Geom2dAdaptor_Curve
from OCC.Core.GCPnts import GCPnts_UniformAbscissa
#导入用于在适配器曲线上进行等分参数计算的类GCPnts_UniformAbscissa。
from OCC.Display.SimpleGui import init_display
from OCC.Core.Geom2dAdaptor import Geom2dAdaptor_Curve
from OCC.Core.GeomAdaptor import GeomAdaptor_Curve
from OCC.Core.gp import gp_Pnt, gp_Pnt2d, gp_OX2d
from OCC.Core.Geom2d import Geom2d_Circle
from OCC.Core.Geom2dAdaptor import Geom2dAdaptor_Curve
from OCC.Core.GCPnts import GCPnts_UniformAbscissa
#导入用于在适配器曲线上进行等分参数计算的类GCPnts_UniformAbscissa。
from OCC.Display.SimpleGui import init_display
#!/usr/bin/env python
from OCC.Core.gp import gp_Vec, gp_Pnt
import math
import vtk
from OCC.Core.gp import gp_Vec, gp_Pnt
from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.Geom import Geom_BSplineCurve
# from OCC.Core.StdFail import StdFail_NotDone
from OCC.Extend.TopologyUtils import TopologyExplorer
import re
##Copyright 2009-2014 Jelle Feringa (jelleferinga@gmail.com)
##
##This file is part of pythonOCC.
##
##pythonOCC is free software: you can redistribute it and/or modify
##it under the terms of the GNU Lesser General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##pythonOCC is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU Lesser General Public License for more details.
##
##You should have received a copy of the GNU Lesser General Public License
##along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.
#这段代码使用pythonOCC库绘制一个2D圆，并在该圆上进行等分参数计算，然后将参数点显示在图形窗口中。
from OCC.Core.gp import gp_Pnt, gp_Pnt2d, gp_OX2d
from OCC.Core.Geom2d import Geom2d_Circle
from OCC.Core.Geom2dAdaptor import Geom2dAdaptor_Curve
from OCC.Core.GCPnts import GCPnts_UniformAbscissa
#导入用于在适配器曲线上进行等分参数计算的类GCPnts_UniformAbscissa。
from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()
# 假设有一个函数make_c_radius用于计算曲率
# 读取 .txt 文件并存储为 NumPy 数组
def read_txt_file(file_path):
    data = np.loadtxt(file_path) # 假设 .txt 文件中每行包含 x、y、z 坐标
    return data

def generate_bspline_from_file(filename):
    points = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            coordinates = line.strip().split()
            if len(coordinates) == 3:
                x, y, z = float(coordinates[0]), float(coordinates[1]), float(coordinates[2])
                points.append(gp_Pnt(x, y, z))

    num_points = len(points)
    harray = TColgp_HArray1OfPnt(1, num_points)
    for i, point in enumerate(points):
        harray.SetValue(i + 1, point)

    interp = GeomAPI_Interpolate(harray, True, 0.0001)
    interp.Perform()
    return interp.Curve()


filename = r"./test1.txt"
bspline_curve = generate_bspline_from_file(filename)
interpolated_curve = bspline_curve
V_end = bspline_curve.LastParameter()
#这一行代码通过bspline->LastParameter()获取bspline曲线的最后参数值，并将其赋值给名为V_end的变量。
nums=800
#离散的点数
V1, V2 = gp_Vec(), gp_Vec()
P=gp_Pnt()
#一阶导数向量V1，V2，这一行代码声明了三个变量：V1和V2是gp_Vec类型的变量，用于存储曲线上某点处的一阶导数向量；P是gp_Pnt类型的变量，用于存储曲线上的点。
V_dir = 0.0
step = V_end / nums
#V_dir表示当前离散化的参数值，初始化为0；step表示每次增加的步长，即离散化时参数值的增加量，通过将V_end除以nums得到。
print("start")
psum = 0
points_st = []
while V_dir < V_end and psum < nums:
        bspline_curve.D2(V_dir, P, V1, V2)
        points_st.append([P.X(), P.Y(), P.Z()])
        if psum == nums:
            V_dir = V_end
        else:
            V_dir += step
        psum += 1
print(points_st)
print(len(points_st))
display.DisplayShape(interpolated_curve, update=True)

i = 0
for p in points_st:
    i = i + 1
    # pstring = 'P%i : parameter %f' % (i, ua.Parameter(i))
    pnt = gp_Pnt(p[0], p[1], p[2])
    # display points
    display.DisplayShape(pnt, update=True)
    # display.DisplayMessage(pnt, pstring)
start_display()
# 将离散的点保存为.txt文件
output_filename = r"./lisan1.txt"
with open(output_filename, 'w') as file:
    for p in points_st:
        file.write(f"{p[0]} {p[1]} {p[2]}\n")
# display, start_display, _, _ = init_display()
# display.DisplayShape(bspline_curve, update=True)
# start_display()