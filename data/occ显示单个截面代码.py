from __future__ import print_function
from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.TColgp import TColgp_HArray1OfPnt
from OCC.Core.gp import gp_Pnt
from OCC.Display.SimpleGui import init_display
import os
from OCC.Core.gp import gp_Pnt
from OCC.Display.SimpleGui import init_display
from OCC.Extend.DataExchange import read_iges_file, write_step_file
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.TopoDS import TopoDS_Compound
#!/usr/bin/env python
from OCC.Core.AIS import AIS_Shape
##Copyright 2009-2015 Thomas Paviot (tpaviot@gmail.com)
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
from OCC.Core.gp import gp_Pnt, gp_Vec
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.TColgp import TColgp_HArray1OfPnt
from OCC.Core.gp import gp_Pnt
from OCC.Display.SimpleGui import init_display
from OCC.Display.SimpleGui import init_display
# display, start_display, add_menu, add_function_to_menu = init_display()
from OCC.Core.AIS import AIS_Shape
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.gp import gp_Pnt
from OCC.Display.SimpleGui import init_display
import OCC.Core.IGESControl as IGESControl
import OCC.Core.STEPControl as STEPControl
from OCC.Extend.DataExchange import IGESControl_Writer, write_iges_file
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TopoDS import TopoDS_Shape
import OCC.Core.TopoDS as TopoDS

from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TopoDS import TopoDS_Shape
# from OCC.Extend.DataExchange import IGESControl_Writer, IGESControl_Controller
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.TColgp import TColgp_HArray1OfPnt
from OCC.Core.gp import gp_Pnt
from OCC.Display.SimpleGui import init_display
from OCC.Core.StlAPI import StlAPI_Writer
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.IGESControl import IGESControl_Writer
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox  # 用于创建一个盒子作为封闭壳
from OCC.Core.IGESControl import IGESControl_Writer
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


filename = r"./guangshun34.txt"
bspline_curve = generate_bspline_from_file(filename)



display, start_display, _, _ = init_display()
display.DisplayShape(bspline_curve, update=True)
start_display()




# 将生成的 B-spline 曲线封装在一个面上
bspline_edge = BRepBuilderAPI_MakeEdge(bspline_curve).Edge()
face = BRepBuilderAPI_MakeFace(BRepBuilderAPI_MakeWire(bspline_edge).Wire()).Face()

# 导出为 IGES 文件
iges_filename = r"./bspline_curve.iges"

iges_writer = IGESControl_Writer()
iges_writer.AddShape(face)
iges_writer.ComputeModel()
iges_writer.Write(iges_filename)

print(f"B-spline 曲线已成功导出为 IGES 文件：{iges_filename}")

# 导出为 STEP 文件
step_filename = r"./bspline_curve.step"

step_writer = STEPControl_Writer()
step_writer.Transfer(face, STEPControl_AsIs)
status = step_writer.Write(step_filename)

if status == IFSelect_RetDone:
    print(f"B-spline 曲线已成功导出为 STEP 文件：{step_filename}")
else:
    print("导出失败")



