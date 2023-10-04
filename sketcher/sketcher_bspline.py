# -*- coding: utf-8 -*-
from OCC.Core import BRepExtrema
from OCC.Core.BRep import BRep_Tool
from OCC.Core.Geom import Geom_CartesianPoint, Geom_Line
from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.Prs3d import Prs3d_PointAspect
from OCC.Core.Quantity import Quantity_Color
from OCC.Core.TColgp import TColgp_HArray1OfPnt
from OCC.Core.TopoDS import TopoDS_Vertex, TopoDS_Wire
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from GUI.DialogWidget import DialogWidget
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCC.Core.GC import GC_MakeSegment, GC_MakeCircle
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Lin, gp_Ax2,gp_Dir
from OCC.Core.AIS import AIS_Shape, AIS_Point
from sketcher.sketcher_line import sketch_line
from OCC.Core.StdSelect import StdSelect_ShapeTypeFilter
from OCC.Core.TopAbs import TopAbs_VERTEX, TopAbs_EDGE, TopAbs_FACE, TopAbs_SOLID, TopAbs_SHELL, TopAbs_COMPOUND, TopAbs_WIRE
from OCC.Core.Aspect import (Aspect_TOM_POINT,
							 Aspect_TOM_PLUS,
							 Aspect_TOM_STAR,
							 Aspect_TOM_X,
							 Aspect_TOM_O,
							 Aspect_TOM_O_POINT,
							 Aspect_TOM_O_PLUS,
							 Aspect_TOM_O_STAR,
							 Aspect_TOM_O_X,
							 Aspect_TOM_RING1,
							 Aspect_TOM_RING2,
							 Aspect_TOM_RING3,
							 Aspect_TOM_BALL)

from PyQt5 import QtCore 
from PyQt5.QtWidgets import QFileDialog
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_BLACK
class sketch_bspline(object):
	def __init__(self,parent=None,gp_Dir=None):
		super(sketch_bspline, self).__init__()
		self.parent = parent
		self.gp_Dir=gp_Dir
		self.dragStartPosX = 0
		self.dragStartPosY = 0
		self.aisline = None
		self.point_count = []
		self.line_dict = {}
		self.point_dict = {}
		self.show_circel_dict = {}
		self.point_count = []
		self.circel_id = 0
		self.draw_circel_connect=None
		self.ais_point=None
		self.ais_point_dict={}
		self.perious_ais_point_ID=None
		self.mousePress_select_point_ID=None
		self.bspline_curve=None
		self.bspline_curve_dict=None
		self.dialogWidget=None
		self.Distance=0
		self.dynamics_point_move_point_shield=False
		self.import_bspline_point()
		self.parent.Displayshape_core.canva.mouse_move_Signal.trigger.connect(self.dynamics_point_highlight)
		self.parent.Displayshape_core.canva.mousePressEvent_Signal.trigger.connect(self.mousepress)
		

	
	def generate_bspline_from_file(self,filename):
		solidFilter=StdSelect_ShapeTypeFilter(TopAbs_EDGE)#选择过滤器
		self.parent.Displayshape_core.canva._display.Context.AddFilter(solidFilter)#设置过滤器
		points = []
		with open(filename, 'r') as file:
			lines = file.readlines()
			n=1
			for line in lines:
				coordinates = line.strip().split()
				if len(coordinates) == 3:
					x, y, z = float(coordinates[0])*10, float(coordinates[1])*10, float(coordinates[2])
					self.draw_point(x,y,0,0,n)
					
					points.append(gp_Pnt(x, y, 0))
					self.point_dict[n]=gp_Pnt(x, y, 0)
					n+=1
		
		num_points = len(points)
		self.harray = TColgp_HArray1OfPnt(1, num_points)
		for i, point in enumerate(points):
			self.harray.SetValue(i + 1, point)
		
		interp = GeomAPI_Interpolate(self.harray, True, 0.0001)
		interp.Perform()
		return interp.Curve()

	def generate_bspline(self,n,pnt):
		self.harray.SetValue(n,pnt)
		self.point_dict[n]=pnt
		interp = GeomAPI_Interpolate(self.harray, True, 0.0001)
		interp.Perform()
		return interp.Curve()

	def generate_bspline_setvalue(self,n,pnt):
		self.harray.SetValue(n,pnt)
		self.point_dict[n]=pnt
		interp = GeomAPI_Interpolate(self.harray, True, 0.0001)
		interp.Perform()
	def test(self):
		if self.dynamics_point_move_point_shield==False:
			
			self.parent.Displayshape_core.canva._display.Context.Remove(self.ais_point_dict[self.mousePress_select_point_ID],False)
			print(self.mousePress_select_point_ID,"已经移除")
			x=self.dialogWidget.qdoubleSpinBox_x.value()
			y=self.dialogWidget.qdoubleSpinBox_y.value()
			z=self.dialogWidget.qdoubleSpinBox_z.value()
			print("TEST ID",self.mousePress_select_point_ID)
			self.ais_point_dict[self.perious_ais_point_ID]=self.draw_point(x,y,0,1)
			self.parent.Displayshape_core.canva._display.Context.Display(self.ais_point_dict[self.mousePress_select_point_ID],False)
			self.parent.Displayshape_core.canva._display.Context.UpdateCurrentViewer()

			bspline_curve=self.generate_bspline(self.mousePress_select_point_ID,gp_Pnt(x,y,z))
			edge = BRepBuilderAPI_MakeEdge(bspline_curve).Edge()
			self.bspline_curve.SetShape(edge)
			self.parent.Displayshape_core.canva._display.Context.Redisplay(self.bspline_curve,True,False)  # 重新计算更新已经显示的物
			self.parent.Displayshape_core.canva._display.Repaint()
			self.parent.Displayshape_core.canva._display.Context.UpdateCurrentViewer()
			print(123)
	def import_bspline_point(self):
		try:
			filename = r"./data/guangshun19.txt"
			self.chose_document = QFileDialog.getOpenFileName(self.parent, '打开文件', './'," TXT files(*.TXT , *.TEXT);;(*.DAT);;(*.INI)")  # 选择转换的文价夹
			filename = self.chose_document[0]  # 获取打开文件夹路径
			bspline_curve = self.generate_bspline_from_file(filename)
			edge = BRepBuilderAPI_MakeEdge(bspline_curve).Edge()
			self.bspline_curve=AIS_Shape(edge)
			self.bspline_curve.SetColor(Quantity_Color(Quantity_NOC_BLACK))
			self.bspline_curve.SetWidth(2)
			self.parent.Displayshape_core.canva._display.Context.Display(self.bspline_curve,
																				 False)  # 重新计算更新已经显示的物
	
		except Exception as e:
			print(e)

	def mousepress(self):
		if self.parent.Displayshape_core.canva.mousepresstype==QtCore.Qt.LeftButton:
			try:
				self.parent.Displayshape_core.canva._display.Context.Remove(self.ais_point,False)
				self.ais_point=None
				
			except Exception as e:
				print(11111,e)
				pass
				
			self.mousePress_select_point_ID=self.perious_ais_point_ID
			self.parent.Displayshape_core.canva.mouse_move_Signal.trigger.disconnect(self.dynamics_point_highlight)
			self.parent.Displayshape_core.canva.mouse_move_Signal.trigger.connect(self.dynamics_point_move_point)
			self.parent.Displayshape_core.canva.mouseReleaseEvent_Signal.trigger.connect(self.mouserelease)

			if self.dialogWidget==None:
				self.dialogWidget=DialogWidget(parent=self.parent)
				self.dialogWidget.Show()
				self.dialogWidget.qdoubleSpinBox_x.valueChanged.connect(self.test)
				#self.dialogWidget.qdoubleSpinBox_x.ok.clicked.connect()
			if self.dialogWidget!=None:
				(x, y, z, vx, vy, vz) = self.parent.Displayshape_core.ProjReferenceAxe()
				self.dialogWidget.qdoubleSpinBox_x.setValue(x)
				self.dialogWidget.qdoubleSpinBox_y.setValue(y)
				self.dialogWidget.qdoubleSpinBox_z.setValue(z)
		
			
	def mouserelease(self):
		try:
			self.parent.Displayshape_core.canva.mouse_move_Signal.trigger.disconnect(self.dynamics_point_move_point)
			self.parent.Displayshape_core.canva.mouse_move_Signal.trigger.connect(self.dynamics_point_highlight)
		except:
			pass

	def dynamics_point_highlight(self):
		shape_id = 0
		Distance = 0
		_dragStartPosY = self.parent.Displayshape_core.canva.dragStartPosY
		_dragStartPosX = self.parent.Displayshape_core.canva.dragStartPosX
		(x, y, z, vx, vy, vz) = self.parent.Displayshape_core.ProjReferenceAxe()
		direction = gp_Dir(vx, vy, vz)
		#line = gp_Lin(gp_Pnt(x, y, z), direction)
		#edge_builder = BRepBuilderAPI_MakeEdge(line)
		#edge = edge_builder.Edge()
		nearest_point1=gp_Pnt(x,y,0)
		if self.ais_point==None:
			for ID in self.point_dict.keys():
				try:
					nearest_point2 = self.point_dict[ID]
					if Distance > nearest_point1.Distance(nearest_point2) or Distance == 0:
						Distance = nearest_point1.Distance(nearest_point2)
						x, y, z = (nearest_point2.X()), (nearest_point2.Y()), (nearest_point2.Z())
						self.perious_ais_point_ID=ID
						#print(" ID",self.perious_ais_point_ID)

				except Exception as e:
					print(e)
					pass
			
			if Distance<20*(1/self.parent.Displayshape_core.canva.scaling_ratio):
				self.draw_point(x,y,0,0,None,9,[0,0,255])
				self.Distance=Distance

			elif Distance>20*(1/self.parent.Displayshape_core.canva.scaling_ratio) and self.ais_point!=None:
				self.perious_ais_point_ID=None
				#self.parent.Displayshape_core.canva._display.Context.Remove(self.ais_point,False)
				#self.ais_point=None
				pass

		else:
			try:
				_dragStartPosY = self.parent.Displayshape_core.canva.dragStartPosY
				_dragStartPosX = self.parent.Displayshape_core.canva.dragStartPosX
				(x, y, z, vx, vy, vz) = self.parent.Displayshape_core.ProjReferenceAxe()
				direction = gp_Dir(vx, vy, vz)
				nearest_point1=gp_Pnt(x,y,0)
				Distance=self.point_dict[self.perious_ais_point_ID].Distance(nearest_point1)
				if Distance>20*(1/self.parent.Displayshape_core.canva.scaling_ratio):
					self.parent.Displayshape_core.canva._display.Context.Remove(self.ais_point,False)
					self.ais_point=None
					self.perious_ais_point_ID=None
					print("yes")
			except Exception as e:
				print(e)
				pass
		print(66,self.perious_ais_point_ID)
	def dynamics_point_move_point(self):
		if self.perious_ais_point_ID!=None:
			self.dynamics_point_move_point_shield=True
			self.parent.Displayshape_core.canva._display.Context.Remove(self.ais_point_dict[self.perious_ais_point_ID],False)
			(x, y, z, vx, vy, vz) = self.parent.Displayshape_core.ProjReferenceAxe()
			#------------------------------------
			self.dialogWidget.qdoubleSpinBox_x.setValue(x)
			self.dialogWidget.qdoubleSpinBox_y.setValue(y)
			self.dialogWidget.qdoubleSpinBox_z.setValue(z)
			
			self.ais_point_dict[self.perious_ais_point_ID]=self.draw_point(x,y,0,1)
			self.parent.Displayshape_core.canva._display.Context.Display(self.ais_point_dict[self.perious_ais_point_ID],False)
			self.parent.Displayshape_core.canva._display.Context.UpdateCurrentViewer()
			bspline_curve=self.generate_bspline(self.perious_ais_point_ID,gp_Pnt(x,y,z))
			edge = BRepBuilderAPI_MakeEdge(bspline_curve).Edge()
			self.bspline_curve.SetShape(edge)
			print(self.bspline_curve)
			self.parent.Displayshape_core.canva._display.Context.Redisplay(self.bspline_curve,True,False)  # 重新计算更新已经显示的物
			self.parent.Displayshape_core.canva._display.Repaint()
			self.parent.Displayshape_core.canva._display.Context.UpdateCurrentViewer()
			self.dynamics_point_move_point_shield=False

		

	def draw_point(self,x,y,z,mode=0,id=None,point_type=0,color=None):
		ALL_ASPECTS = [Aspect_TOM_POINT,
					   Aspect_TOM_PLUS,
					   Aspect_TOM_STAR,
					   Aspect_TOM_X,
					   Aspect_TOM_O,
					   Aspect_TOM_O_POINT,
					   Aspect_TOM_O_PLUS,
					   Aspect_TOM_O_STAR,
					   Aspect_TOM_O_X,
					   Aspect_TOM_RING1,
					   Aspect_TOM_RING2,
					   Aspect_TOM_RING3,
					   Aspect_TOM_BALL]
		if mode==0:
			if point_type!=None:
				point_type = ALL_ASPECTS[point_type]
				p = Geom_CartesianPoint(gp_Pnt(x, y, z))
				if color!=None:
					color = Quantity_Color(color[0]/255, color[1]/255, color[2]/255, Quantity_TOC_RGB)

				else:
					color = Quantity_Color(0, 0, 0, Quantity_TOC_RGB)

				if id==None:
						self.ais_point = AIS_Point(p)
						drawer = self.ais_point.Attributes()
						asp = Prs3d_PointAspect(ALL_ASPECTS[point_type], color, 3)
						drawer.SetPointAspect(asp)
						self.ais_point.SetAttributes(drawer)
						self.parent.Displayshape_core.canva._display.Context.Display(self.ais_point,
																					 False)  # 重新计算更新已经显示的物

				else:
					self.ais_point_dict[id]=AIS_Point(p)
					drawer = self.ais_point_dict[id].Attributes()
					asp = Prs3d_PointAspect(ALL_ASPECTS[point_type], color, 3)
					drawer.SetPointAspect(asp)
					self.ais_point_dict[id].SetAttributes(drawer)

					self.parent.Displayshape_core.canva._display.Context.Display(self.ais_point_dict[id],
																					 False)  # 重新计算更新已经显示的物
			
		
		elif mode==1:
			if point_type!=None:
				point_type = ALL_ASPECTS[point_type]
				p = Geom_CartesianPoint(gp_Pnt(x, y, z))
				if color!=None:
					color = Quantity_Color(color[0]/255, color[1]/255, color[2]/255, Quantity_TOC_RGB)

				else:
					color = Quantity_Color(0, 0, 0, Quantity_TOC_RGB)

				ais_point = AIS_Point(p)
				drawer = ais_point.Attributes()
				asp = Prs3d_PointAspect(ALL_ASPECTS[point_type], color, 3)
				drawer.SetPointAspect(asp)
				ais_point.SetAttributes(drawer)

				return ais_point
			
			
			
			
	
			

			
	