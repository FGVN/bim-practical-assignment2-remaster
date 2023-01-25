"""
Example Script for scalable PythonPart adapted from MacroColumnExample
"""

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import GeometryValidate as GeometryValidate

from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from GeometryExamples.GeometryElements import GeometryElements

from PythonPart import View2D3D, PythonPart


def check_allplan_version(build_ele, version):

    # Delete unused arguments

    del build_ele

    del version
    # Support all versions

    return True

def create_element(build_ele, doc):
    """
    Creation of element

    Args:
        build_ele: the building element.
        doc:       input document
    """
    element = Beam(doc)

    return element.create(build_ele)

def move_handle(build_ele, handle_prop, input_pnt, doc):
    """
    Modify the element geometry by handles

    Args:
        build_ele:  the building element.
        handle_prop handle properties
        input_pnt:  input point
        doc:        input document
    """
    build_ele.change_property(handle_prop, input_pnt)
    return create_element(build_ele, doc)

class Beam():
    """
    Definition of class MacroColumnExample
    """

    def __init__(self, doc):
        """
        Initialisation of class MacroColumnExample

        Args:
            doc: input document
        """
        self.model_ele_list = []
        self.handle_list = []
        self.document = doc
        self._height = 100.
        self._width = 100.
        self._depth = 1000.
        self._wall_thickness = 100.
        self._create_3d_body = True
        self._hash_value = ""
        self._python_file = ""
        
            
    
    def create(self, build_ele):
        """
        Create the elements

        Args:
            build_ele:  the building element.

        Returns:
            tuple  with created elements and handles.
        """
        #------------------ Extract property values
        
        self._depth = build_ele.L.value
        self.height = build_ele.height.value
        
        #bottom part params
        self.bottomh = build_ele.botheight.value
        self.bottomw = build_ele.botwidth.value
        
        self.pol1h = build_ele.pol1height.value
        
        #middle part params
        self.midh=build_ele.midheight.value
        self.midw = build_ele.midwidth.value
        
        #top part bottom params
        self.top1h = 50
        self.top1w = build_ele.top1width.value
        
        #top part top params
        self.top2h = 50
        self.top2w = build_ele.top2width.value
        
        #top polyhedron params
        self.pol2h = build_ele.topheight.value - self.top1h - self.top2h
        
        
        #cylinder params
        self.cyldiametr = 91
        self.cylheight = 10 * self.midw
        self.ls = build_ele.ls.value
        self.hs = build_ele.hs.value
        
        if(build_ele.height.value != 1100):
            self.midh += -1100+build_ele.height.value
        
        
        #rotation params
        self.z_angle = build_ele.zangle.value
        
        
        self._hash_value = build_ele.get_hash()
        self._python_file = build_ele.pyp_file_name

        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        
        com_prop.Pen = 100
        com_prop.Stroke = 1
        com_prop.Color = 3
        
        
        
        #creating all elements by values
        bot = self.create_cuboid(build_ele, self._depth, self.bottomw, self.bottomh, 0)
        #pol stands for polyhedron
        pol1 = self.top_part_addiction_1(build_ele, self._depth, self.bottomh+self.pol1h, self.bottomh, self.bottomw/-2., self.midw/-2, self.midw/2, self.bottomw/2.)
        
        #creating fliped middle part
        mid = self.create_cuboid(build_ele, self._depth,self.midh, self.midw, self.bottomh+self.pol1h)
        
        pol2 = self.top_part_addiction_1(build_ele, self._depth, self.bottomh+self.midh+self.pol2h+self.pol1h, self.bottomh+self.midh+self.pol1h, self.midw/-2, self.top1w/-2, self.top1w/2, self.midw/2)
        top1 = self.create_cuboid(build_ele, self._depth, self.top1w, self.top1h, self.bottomh+self.midh+self.pol2h+self.pol1h)
        top2 = self.create_cuboid(build_ele, self._depth, self.top2w, self.top2h, self.bottomh+self.midh+self.top1h+self.pol2h+self.pol1h)
        
        
        #adding middle part strapping by substracting cylinders from flipped middle part in order to make strpang holes and flipping it back
        
        
        #creating cylinder to make strapping
        cyl =  self.create_cylinder(build_ele)
        #offset for middle part
        off_h = -(self.bottomh+self.pol1h)
        
        
        transvec1 = AllplanGeo.Vector3D(self.ls, self.bottomh+self.pol1h-self.hs+self.midh*0.5, -self.hs)
        cyl = AllplanGeo.Move(cyl, transvec1)
        err, diff = AllplanGeo.MakeSubtraction(mid, cyl)
        print(err)
         
        if err:
           print("invalid substraction one in create")
           
        transvec1 = AllplanGeo.Vector3D(self._depth - 2*self.ls, 0, 0)
        cyl = AllplanGeo.Move(cyl, transvec1)
        
        err, diff = AllplanGeo.MakeSubtraction(diff, cyl)
        print(err)
         
        if err:
           print("invalid substraction two in create")
           
           
        transvec = AllplanGeo.Vector3D(0, -(self.bottomh+self.pol1h+0.5*self.midh), off_h-(0.5*self.midw))
        
        diff = AllplanGeo.Move(diff, transvec)
        self.model_ele_list.append(AllplanBasisElements.ModelElement3D(com_prop, diff))
        AllplanBaseElements.ElementTransform(AllplanGeo.Vector3D(), 270, 0, 0, self.model_ele_list)
        
        
        #adding all another elemnts 
        self.model_ele_list.append(AllplanBasisElements.ModelElement3D(com_prop, bot))
        self.model_ele_list.append(AllplanBasisElements.ModelElement3D(com_prop, pol1))
        self.model_ele_list.append(AllplanBasisElements.ModelElement3D(com_prop, pol2))
        self.model_ele_list.append(AllplanBasisElements.ModelElement3D(com_prop, top1))
        self.model_ele_list.append(AllplanBasisElements.ModelElement3D(com_prop, top2))
        
        AllplanBaseElements.ElementTransform(AllplanGeo.Vector3D(), 0, 0, self.z_angle, self.model_ele_list)
        self.create_handles()
        return (self.model_ele_list, self.handle_list)

    
    def top_part_addiction_1(self, build_ele, length, bottom, top, point0, point1, point2, point3):
        
        #creating polyhedron by it length bottom and top values and 4 points
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(0,
                                   point0,
                                   top)
        base_pol += AllplanGeo.Point3D(0,
                                   point1,
                                   bottom)
        base_pol += AllplanGeo.Point3D(0,
                                   point2,
                                   bottom)
        base_pol += AllplanGeo.Point3D(0,
                                   point3,
                                   top)
        base_pol += AllplanGeo.Point3D(0,
                                   point0,
                                   top)
        
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, 
                                        1000,
                                        1000)
        path += AllplanGeo.Point3D(0, 
                                        1000,
                                        1000)
        
        polyhedron = AllplanGeo.CreatePolyhedron(base_pol, base_pol)
    
        
        area = AllplanGeo.PolygonalArea3D()
        area += base_pol

        solid = AllplanGeo.ExtrudedAreaSolid3D()
        solid.SetDirection(AllplanGeo.Vector3D(length,
                                               0,
                                               0))
        solid.SetRefPoint(AllplanGeo.Point3D(0,
                                             0,
                                             0))
        solid.SetExtrudedArea(area)

        err, polyhedron = AllplanGeo.CreatePolyhedron(solid)

        if not GeometryValidate.polyhedron(err):
            #self.model_ele_list.append(AllplanBasisElements.ModelElement3D(com_prop, base_pol))
            return

        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        com_prop.Pen = 1
        com_prop.Color = 1
        com_prop.Stroke = 2
        com_prop.Stroke = 1

        
        return polyhedron
     
        
    def create_cuboid(self, build_ele, length, width, height, offset_h):
        #creating cuboid by it length width height and adding offset by height
        
        
        com_prop = AllplanBaseElements.CommonProperties()

        com_prop.GetGlobalProperties()
        
        cuboid_middle = AllplanGeo.BRep3D.CreateCuboid(AllplanGeo.AxisPlacement3D(), length, width, height)
        
        transvec1 = AllplanGeo.Vector3D(0, width/-2 , offset_h)
        cuboid_middle = AllplanGeo.Move(cuboid_middle, transvec1)
        cuboid = AllplanBasisElements.ModelElement3D(com_prop, cuboid_middle)
        
        print(type(cuboid))
        return cuboid_middle
    
    def create_cylinder(self, build_ele):
        #creating cylinders to subctract straping holes from middle part
        com_prop = AllplanBaseElements.CommonProperties()

        com_prop.GetGlobalProperties()
        
        cylinder = AllplanGeo.BRep3D.CreateCylinder(AllplanGeo.AxisPlacement3D(), self.cyldiametr/2, self.cylheight)
        
        
        return cylinder
    
    def create_handles(self):
        """
        Create the column handles
        """

        #------------------ Define handles
        origin = AllplanGeo.Point3D(0, 0, 0)
        center = AllplanGeo.Point3D(self._depth, 0, self._height)
        midpart = AllplanGeo.Point3D(0, 0.5*self.midw, self.bottomh+self.pol1h+self.midh*0.5)
        botpoint = AllplanGeo.Point3D(0, 0.5*self.bottomw, self.bottomh*0.5)
        toppoint = AllplanGeo.Point3D(0, 0.5*self.top1w, self.bottomh+self.pol1h+self.midh + self.pol2h + self.top1h*0.5)
        lenpoint = AllplanGeo.Point3D(0, 0, self.height)


        hanglelen = HandleProperties("Length",
                                   center,
                                   origin,
                                   [("L", HandleDirection.x_dir)],
                                   HandleDirection.x_dir,
                                   True)
        self.handle_list.append(hanglelen)
        
        

        hanglehei = HandleProperties("Height",
                                   lenpoint,
                                   origin,
                                   [("height", HandleDirection.z_dir)],
                                   HandleDirection.z_dir,
                                   True)
        self.handle_list.append(hanglehei)
        
        

        hanglemid = HandleProperties("MiddleWidth",
                                   midpart,
                                   origin,
                                   [("midwidth", HandleDirection.y_dir)],
                                   HandleDirection.y_dir,
                                   True)
        self.handle_list.append(hanglemid)

        hanglebot = HandleProperties("BotWidth",
                                   botpoint,
                                   origin,
                                   [("botwidth", HandleDirection.y_dir)],
                                   HandleDirection.y_dir,
                                   True)
        self.handle_list.append(hanglebot)
        
        

        hangletop = HandleProperties("TopWidth",
                                   toppoint,
                                   origin,
                                   [("top1width", HandleDirection.y_dir)],
                                   HandleDirection.y_dir,
                                   True)
        self.handle_list.append(hangletop)

