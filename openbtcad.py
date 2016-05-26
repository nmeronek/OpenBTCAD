#Name: OpenBTCAD V0.0.6
#Author: Nathan Meronek
#Date: 2016.02.03
#Blender Version: 2.74
#Description: OpenBTCAD is a addon module for blender that allows creation of objects using scripts.  It doesn't cover all features of blender but many of the basic functions are scripted.

#=================================================
#Imports

import bpy
import math

#=================================================
#DXF File Functions

#Open dxf file.
def dxfOpen(filepath):
    f = open(filepath, 'w')
    f.write('  0\nSECTION\n  2\nBLOCKS\n  0\nENDSEC\n  0\nSECTION\n  2\nENTITIES\n')
    f.close()


#Write dxf line.
def dxfAddLine(filepath, line=(0, 0, 0, 0)):
    f = open(filepath, 'a')
    f.write('  0\nLINE\n  8\n0\n')
    f.write(' 10\n' + str(line[0]) + '\n')
    f.write(' 11\n' + str(line[2]) + '\n')
    f.write(' 20\n' + str(line[1]) + '\n')
    f.write(' 21\n' + str(line[3]) + '\n')
    f.close()


#Close dxf file.
def dxfClose(filepath):
    f = open(filepath, 'a')
    f.write('  0\nENDSEC\n  0\nSECTION\n  2\nOBJECTS\n  0\nDICTIONARY\n  0\nENDSEC\n  0\nEOF\n')
    f.close()


#=================================================
#GCode File Functions

#Open gcode file.
def gcodeOpen(filepath):
    f = open(filepath, 'w')
    f.write('GCodeStart \n')
    f.close()


#Write gcode line.
def gcodeAddPoint(filepath, point=(0, 0)):
    f = open(filepath, 'a')
    f.write('X' + str(line[0]) + ' Y' + str(line[1]) + '\n')
    f.close()


#Write gcode text.
def gcodeAddText(filepath, teststring)
    f = open(filepath, 'a')
    f.write(str(teststring) + '\n')
    f.close()
    

#Close gcode file.
def gcodeClose(filepath):
    f = open(filepath, 'a')
    f.write('GCodeEnd \n')
    f.close()


#=================================================
#OpenBTCAD internal functions.  These functions should only be used by OpenBTCAD itself.

#Returns a pointer to an object based on name.  Some operations need the object pointer.
def objReturnByName(objname1):
    r = None
    obs = bpy.data.objects
    for ob in obs:
        if ob.name == objname1:
            r = ob
    return r
    

#CoDEmanX wrote this from www.elysiun.com.  It changes the pivot point for rotation.
def setPivotPoint(type):
    
    if type not in ('BOUNDING_BOX_CENTER', 'CURSOR', 'INDIVIDUAL_ORIGINS',
                    'MEDIAN_POINT', 'ACTIVE_ELEMENT'):
        return False
    
    for a in bpy.context.screen.areas:
        if a.type == 'VIEW_3D':
            break
    else:
        return False
    
    a.spaces[0].pivot_point = type
    return True
    

#Garret wrote this from blender.stackexchange.com   Does an override on the rotation function.
def get_override(area_type, region_type):
    for area in bpy.context.screen.areas: 
        if area.type == area_type:             
            for region in area.regions:                 
                if region.type == region_type:                    
                    override = {'area': area, 'region': region} 
                    return override
    #error message if the area or region wasn't found
    raise RuntimeError("Wasn't able to find", region_type," in area ", area_type,
                        "\n Make sure it's open while executing script.")


#=================================================
#3D Cursor Functions

#Sets the cursor location to a specific point.
def setCursorLocation(location=(0,0,0)):
    
    for a in bpy.context.screen.areas:
        if a.type == 'VIEW_3D':
            break
    else:
        return False
    
    a.spaces[0].cursor_location[0] = location[0]
    a.spaces[0].cursor_location[1] = location[1]
    a.spaces[0].cursor_location[2] = location[2]
    
    return
 
    
#Gets the cursor location.
def getCursorLocation():
    
    for a in bpy.context.screen.areas:
        if a.type == 'VIEW_3D':
            break
    else:
        return False
    
    return (a.spaces[0].cursor_location[0], a.spaces[0].cursor_location[1], a.spaces[0].cursor_location[2])


#=================================================
#Select and Delete functions.

#Return all like named objects.
def objReturnNameList(objname1="badname"):
    objlist = []
    objlist.append(objname1)
    for ob in bpy.data.objects:
        if ob.type == 'MESH' and ob.name.startswith(objname1 + "."):
            objlist.append(ob.name)
            
    return objlist
    

#Selects object with specific name or all objects if none are specified(MESH Only).
def objSelect(objname1=""):
    if objReturnByName(objname1) == None and objname1 != "":
        print("Bad parameter in objSelect:  " + str(objname1))
        print("objname1 does not exist")
        return
        
    for ob in bpy.data.objects:
        if ob.type == 'MESH' and ob.name == objname1:
            ob.select = True
        elif ob.type == 'MESH' and objname1 == "":
            ob.select = True


#UnSelects object with specific name or all objects if none are specified.
def objUnSelect(objname1=""):
    if objReturnByName(objname1) == None and objname1 != "":
        print("Bad parameter in objUnSelect:  " + str(objname1))
        print("objname1 does not exist")
        return
        
    for ob in bpy.data.objects:
        if ob.name == objname1:
            ob.select = False
        elif objname1 == "":
            ob.select = False


#Deletes all selected objects from scene.
def objDeleteSelected():
    bpy.ops.object.delete()


#Delete object with specific name.
def objDelete(objname1=""):
    objUnSelect()
    objSelect(objname1=objname1)
    objDeleteSelected()


#Update all objects with same name.
#def objUpdateAll(objname1="", funct='')
        

#=================================================
#Move and Rotate objects.
    
#Moves an object in a specific direction.
def objMove(objname1, movement=(0,0,0), setlocation=True):
    object1 = objReturnByName(objname1)
    if object1 == None:
        print("Bad parameter in objMove: " + str(objname1) + ", " + str(movement) + ", " + str(setlocation))
        print("objname1 does not exist")
        return
        
    if len(movement) != 3:
        print("Bad parameter in objMove: " + str(objname1) + ", " + str(movement) + ", " + str(setlocation))
        print("movement must contain a 3 number tuple")
        return

    if isinstance(setlocation, int) != True or setlocation not in [0, 1]:
        print("Bad parameter in objMove: " + str(objname1) + ", " + str(movement) + ", " + str(setlocation))
        print("setlocation must be True or False")
        return
        
    if setlocation == True:   
        object1.location[0] = movement[0]
        object1.location[1] = movement[1]
        object1.location[2] = movement[2]
        
    elif setlocation == False:    
        object1.location[0] = object1.location[0] + movement[0]
        object1.location[1] = object1.location[1] + movement[1]
        object1.location[2] = object1.location[2] + movement[2]
    

#Rotates an object with a specific name.
def objRotate(objname1, rotation=(0,0,0), pivot="SELF"):
    if objReturnByName(objname1) == None:
        print("Bad parameter in objRotate: " + str(objname1) + ", " + str(rotation) + ", " + str(pivot))
        print("objname1 does not exist")
        return
        
    if len(rotation) != 3:
        print("Bad parameter in objRotate: " + str(objname1) + ", " + str(rotation) + ", " + str(pivot))
        print("rotation must contain a 3 number tuple in degrees")
        return

    if pivot.upper() not in ["SELF", "CENTER", "CURSOR"]:
        print("Bad parameter in objRotate: " + str(objname1) + ", " + str(rotation) + ", " + str(pivot))
        print("pivot must be self, center, cursor")
        return
    
    objUnSelect()
    objSelect(objname1)
            
    if pivot.upper() == "SELF":
        setPivotPoint('ACTIVE_ELEMENT')
        bpy.ops.transform.rotate(value=(rotation[0] * 0.0174532925), axis=(1,0,0))
        bpy.ops.transform.rotate(value=(rotation[1] * 0.0174532925), axis=(0,1,0))
        bpy.ops.transform.rotate(value=(rotation[2] * 0.0174532925), axis=(0,0,1))

    elif pivot.upper() == "CENTER":
        setPivotPoint('CURSOR')
        setCursorLocation()
        override = get_override('VIEW_3D', 'WINDOW')
        bpy.ops.transform.rotate(override, value=(rotation[0] * 0.0174532925), axis=(1,0,0))
        bpy.ops.transform.rotate(override, value=(rotation[1] * 0.0174532925), axis=(0,1,0))
        bpy.ops.transform.rotate(override, value=(rotation[2] * 0.0174532925), axis=(0,0,1))
        setPivotPoint('ACTIVE_ELEMENT')
        
    elif pivot.upper() == "CURSOR":
        setPivotPoint('CURSOR')
        override = get_override('VIEW_3D', 'WINDOW')
        bpy.ops.transform.rotate(override, value=(rotation[0] * 0.0174532925), axis=(1,0,0))
        bpy.ops.transform.rotate(override, value=(rotation[1] * 0.0174532925), axis=(0,1,0))
        bpy.ops.transform.rotate(override, value=(rotation[2] * 0.0174532925), axis=(0,0,1))
        setPivotPoint('ACTIVE_ELEMENT')


#Resize an object in a specific direction.
def objResize(objname1, resize=(1,1,1)):
    object1 = objReturnByName(objname1)
    if object1 == None:
        print("Bad parameter in objMove: " + str(objname1) + ", " + str(resize))
        print("objname1 does not exist")
        return
        
    if len(resize) != 3:
        print("Bad parameter in objMove: " + str(objname1) + ", " + str(resize))
        print("resize must contain a 3 number tuple")
        return
        
    if resize[0] >= 0:
        object1.scale[0] = resize[0]
        
    if resize[1] >= 0:
        object1.scale[1] = resize[1]
        
    if resize[2] >= 0:
        object1.scale[2] = resize[2]
    

#=================================================
#Add Objects 

#Add a plane to the scene with name and size.
def objAddPlane(objname1, resize=(1,1,1)):
    if objReturnByName(objname1) != None:
        print("Bad parameter in objAddPlane:  " + str(objname1) + ", " + str(resize))
        print("objname1 already exists")
        return
        
    if len(resize) != 3:
        print("Bad parameter in objAddPlane:  " + str(objname1) + ", " + str(resize))
        print("resize must contain a 3 number tuple")
        return
    
    objUnSelect()
    bpy.ops.mesh.primitive_plane_add(radius=.5, location=(0, 0, 0))
    bpy.ops.transform.resize(value=(resize[0], resize[1], resize[2]))
    for obj in bpy.context.selected_objects:
        obj.name = objname1
        

#Add a cube to the scene with name and size.        
def objAddCube(objname1, resize=(1,1,1)):
    if objReturnByName(objname1) != None:
        print("Bad parameter in objAddCube: " + str(objname1) + ", " + str(resize))
        print("objname1 already exists")
        return
        
    if len(resize) != 3:
        print("Bad parameter in objAddCube: " + str(objname1) + ", " + str(resize))
        print("resize must contain a 3 number tuple")
        return
    
    objUnSelect()
    bpy.ops.mesh.primitive_cube_add(radius=.5, location=(0, 0, 0))
    bpy.ops.transform.resize(value=(resize[0], resize[1], resize[2]))
    for obj in bpy.context.selected_objects:
        obj.name = objname1


#Add a circle to the scene with name and size.
def objAddCircle(objname1, resize=(1,1,1), vertices=32):
    if objReturnByName(objname1) != None:
        print("Bad parameter in objAddCircle: " + str(objname1) + ", " + str(resize) + ", " + str(vertices))
        print("objname1 already exists")
        return
        
    if len(resize) != 3:
        print("Bad parameter in objAddCircle: " + str(objname1) + ", " + str(resize) + ", " + str(vertices))
        print("resize must contain a 3 number tuple")
        return

    if isinstance(vertices, int) != True or vertices < 3:
        print("Bad parameter in objAddCircle: " + str(objname1) + ", " + str(resize) + ", " + str(vertices))
        print("vertices must be an integer greater than 2")
        return
    
    objUnSelect()
    bpy.ops.mesh.primitive_circle_add(radius=.5, vertices=vertices, location=(0, 0, 0))
    bpy.ops.transform.resize(value=(resize[0], resize[1], resize[2]))
    for obj in bpy.context.selected_objects:
        obj.name = objname1


#Add a cylinder to the scene with name and size.
def objAddCylinder(objname1, resize=(1,1,1), vertices=32, r1=.5, r2=.5):
    if objReturnByName(objname1) != None:
        print("Bad parameter in objAddCylinder: " + str(objname1) + ", " + str(resize) + ", " + str(vertices) + ", " + str(r1) + ", " + str(r2))
        print("objname1 already exists")
        return
        
    if len(resize) != 3:
        print("Bad parameter in objAddCylinder: " + str(objname1) + ", " + str(resize) + ", " + str(vertices) + ", " + str(r1) + ", " + str(r2))
        print("resize must contain a 3 number tuple")
        return

    if isinstance(vertices, int) != True or vertices < 3:
        print("Bad parameter in objAddCylinder: " + str(objname1) + ", " + str(resize) + ", " + str(vertices) + ", " + str(r1) + ", " + str(r2))
        print("vertices must be an integer greater than 2")
        return
        
    if isinstance(r1, (int, float)) != True or r1 < 0:
        print("Bad parameter in objAddCylinder: " + str(objname1) + ", " + str(resize) + ", " + str(vertices) + ", " + str(r1) + ", " + str(r2))
        print("radius1 must be a number not less than 0")
        return
        
    if isinstance(r2, (int, float)) != True or r2 < 0:
        print("Bad parameter in objAddCylinder: " + str(objname1) + ", " + str(resize) + ", " + str(vertices) + ", " + str(r1) + ", " + str(r2))
        print("radius2 must be a number not less than 0")
        return

    objUnSelect()
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=1, vertices=vertices, location=(0, 0, 0))
    bpy.ops.transform.resize(value=(resize[0], resize[1], resize[2]))
    for obj in bpy.context.selected_objects:
        obj.name = objname1


#Add a uv sphere to the scene with name and size.
def objAddSphereUV(objname1, resize=(1,1,1)):
    if objReturnByName(objname1) != None:
        print("Bad parameter in objAddSphereUV: " + str(objname1) + ", " + str(resize))
        print("objname1 already exists")
        return
        
    if len(resize) != 3:
        print("Bad parameter in objAddSphereUV: " + str(objname1) + ", " + str(resize))
        print("resize must contain a 3 number tuple")
        return
    
    objUnSelect()
    bpy.ops.mesh.primitive_uv_sphere_add(size=.5, location=(0, 0, 0))
    bpy.ops.transform.resize(value=(resize[0], resize[1], resize[2]))
    for obj in bpy.context.selected_objects:
        obj.name = objname1


#Add a ico sphere to the scene with name and size.
def objAddSphereICO(objname1, resize=(1,1,1)):
    if objReturnByName(objname1) != None:
        print("Bad parameter in objAddSphereICO: " + str(objname1) + ", " + str(resize))
        print("objname1 already exists")
        return
        
    if len(resize) != 3:
        print("Bad parameter in objAddSphereICO: " + str(objname1) + ", " + str(resize))
        print("resize must contain a 3 number tuple")
        return

    objUnSelect()
    bpy.ops.mesh.primitive_ico_sphere_add(size=.5, location=(0, 0, 0))
    bpy.ops.transform.resize(value=(resize[0], resize[1], resize[2]))
    for obj in bpy.context.selected_objects:
        obj.name = objname1

#=================================================
#Get location of objects.

#Read each vertex of an object and determin Max value.
def objMax(objname1):
    if objReturnByName(objname1) == None:
        print("Bad parameter in objMax: " + str(objname1))
        print("objname1 does not exists")
        return
        
    wm = bpy.data.objects[objname1].matrix_world
    tempvert = wm * bpy.data.objects[objname1].data.vertices[0].co
    maxx = tempvert[0]
    maxy = tempvert[1]
    maxz = tempvert[2]
    
    for vert in bpy.data.objects[objname1].data.vertices:
        tempvert = wm * vert.co
        if tempvert[0] > maxx:
            maxx = tempvert[0]
        if tempvert[1] > maxy:
            maxy = tempvert[1]
        if tempvert[2] > maxz:
            maxz = tempvert[2]
            
    return (maxx, maxy, maxz)
        

#Read each vertex of an object and determin Min value.
def objMin(objname1):
    if objReturnByName(objname1) == None:
        print("Bad parameter in objMin: " + str(objname1))
        print("objname1 does not exists")
        return
        
    wm = bpy.data.objects[objname1].matrix_world
    tempvert = wm * bpy.data.objects[objname1].data.vertices[0].co
    minx = tempvert[0]
    miny = tempvert[1]
    minz = tempvert[2]
    
    for vert in bpy.data.objects[objname1].data.vertices:
        tempvert = wm * vert.co
        if tempvert[0] < minx:
            minx = tempvert[0]
        if tempvert[1] < miny:
            miny = tempvert[1]
        if tempvert[2] < minz:
            minz = tempvert[2]
            
    return (minx, miny, minz)
    
    
#Return mid point of an object based on objMax and objMin.
def objMid(objname1):
    if objReturnByName(objname1) == None:
        print("Bad parameter in objMid: " + str(objname1))
        print("objname1 does not exists")
        return
        
    midx = (objMin(objname1)[0] + objMax(objname1)[0]) / 2
    midy = (objMin(objname1)[1] + objMax(objname1)[1]) / 2
    midz = (objMin(objname1)[2] + objMax(objname1)[2]) / 2
    
    return (midx, midy, midz)    
    

#=================================================
#Object Modifiers
    
#Perform difference operation on two objects.
def objModBool(objname1, objname2, operation='DIFFERENCE'):
    object1 = objReturnByName(objname1)
    if object1 == None:
        print("Bad parameter in objModBool: " + str(objname1) + ", " + str(objname2) + ", " + str(operation))
        print("objname1 does not exist")
        return
        
    object2 = objReturnByName(objname2)
    if object2 == None:
        print("Bad parameter in objModBool: " + str(objname1) + ", " + str(objname2) + ", " + str(operation))
        print("objname2 does not exist")
        return
    
    if operation.upper() not in ['DIFFERENCE','UNION','INTERSECT']:
        print("Bad parameter in objModBool: " + str(objname1) + ", " + str(objname2) + ", " + str(operation))
        print("operation does not exist, use DIFFERENCE  UNION  INTERSECT")
        return
    
    objUnSelect()
    tmpmod = object1.modifiers.new('tempmod', 'BOOLEAN')
    tmpmod.object = object2
    tmpmod.operation = operation.upper()
    bpy.context.scene.objects.active = object1
    bpy.ops.object.modifier_apply(modifier="tempmod")
    objUnSelect()


#=================================================
#Get and Set objects location and orientation.  Helps create an object in the same location as another object.

#Gets object location and orientation in world.
def getLocOri(objname1=""):
    object1 = objReturnByName(objname1)
    if object1 == None or objname1 == "":
        print("Bad parameter in getLocOri:  " + str(objname1))
        print("objname1 does not exist")
        return (0,0,0,0,0,0,'XYZ')
    
    else:

        return (object1.location[0],object1.location[1],object1.location[2],object1.rotation_euler[0],object1.rotation_euler[1],object1.rotation_euler[2],object1.rotation_mode)
    

#Sets object location and orientation in world.
def setLocOri(objname1="", locori=(0,0,0,0,0,0,'XYZ')):
    object1 = objReturnByName(objname1)
    if object1 == None or objname1 == "":
        print("Bad parameter in setLocOri:  " + str(objname1))
        print("objname1 does not exist")
        return
        
    else:
        #Set object rotation.
        object1.rotation_mode = locori[6]
        object1.rotation_euler = (locori[3],locori[4],locori[5]) 
        
        #Set object position.
        object1.location[0] = locori[0]
        object1.location[1] = locori[1]
        object1.location[2] = locori[2]
        

    

#=================================================
#Object Export

#bt.objExportSCAD("insideclamp", "/home/greendude/mystuff/projects/pipecnc/PipeCNC125/exp/")
#STL-Export object with specific name or all objects if none are specified(MESH Only).
def objExportSCAD(objname1="", dirpath="", ascii=False, projection=False, cut=False):
    if objReturnByName(objname1) == None and objname1 != "":
        print("Bad parameter in objExportSCAD:  " + str(objname1) + ", " + str(dirpath))
        print("objname1 does not exist")
        return
        
    if dirpath == "":
        print("Bad parameter in objExportSCAD:  " + str(objname1) + ", " + str(dirpath))
        print("dirpath must be added")
        return
        
    objUnSelect()
    f = open((dirpath + "objects.scad"), 'w')
    
    for ob in bpy.data.objects:
        if ob.type == 'MESH' and ob.name == objname1:
            ob.select = True
            if projection == True:
                if cut == True:
                    f.write('projection(cut = true)import("' + ob.name + '.stl", convexity=3);\n')
                else:
                    f.write('projection(cut = false)import("' + ob.name + '.stl", convexity=3);\n')
            else:
                f.write('import("' + ob.name + '.stl", convexity=3);\n')
                
            bpy.ops.export_mesh.stl(filepath=(dirpath + ob.name + ".stl"), check_existing=False, ascii=ascii)
            ob.select = False
            
        elif ob.type == 'MESH' and objname1 == "":
            ob.select = True
            if projection == True:
                if cut == True:
                    f.write('projection(cut = true)import("' + ob.name + '.stl", convexity=3);\n')
                else:
                    f.write('projection(cut = false)import("' + ob.name + '.stl", convexity=3);\n')
            else:
                f.write('import("' + ob.name + '.stl", convexity=3);\n')
            
            bpy.ops.export_mesh.stl(filepath=(dirpath + ob.name + ".stl"), check_existing=False, ascii=ascii)
            ob.select = False
            
    f.close()
    
    
# bt.objExportDXF("Cube", "/home/greendude/testnlm.dxf")
# bt.objExportDXF("insideclamp", "/home/greendude/testnlm.dxf")
#Exports a single object as a dxf or all objects if not specified.
def objExportDXF(objname1="", filepath="", cut=True):
    
    
    def exportdxf(objname1=objname1, filepath=filepath, cut=cut):
        
        #Function that checks if a line passes Z 0.
        def checkvalues(value1=None, value2=None):
                if value1 <= 0 <= value2 or value2 <= 0 <= value1:
                    return True
                else:
                    return False
                    
        #Function that checks if a number is in range of another number
        def checkrange(value1, value2, valrange=.0001):
            if value1 >= value2 - valrange and value1 <= value2 + valrange:
                return True
            else:
                return False
        
        
        

        obj = bpy.data.objects[objname1]
        
        wm = bpy.data.objects[objname1].matrix_world
        objectlines = [] #List of lines in the object.
        
        #For each polygon on an object.
        for f in obj.data.polygons:
            elements = []
            
            #Add each vertice of the polygon to the elements list.
            for idx in f.vertices:
                elements.append(wm * obj.data.vertices[idx].co)
                
            
            prev = None #Create a previous variable.    
            drawline = []  
              
            #Go through each item in elements.
            for itm in elements:
                if prev == None:
                    prev = itm
                    continue
                else:
                    if checkvalues(prev[2], itm[2]) == True:
                        drawline.append((itm[0],itm[1]))
                    prev = itm
                    
            if checkvalues(elements[0][2], elements[-1][2]) == True:
                drawline.append((elements[0][0],elements[0][1]))
            
            if len(drawline) > 1:
                objectlines.append(((math.ceil(drawline[0][0]*100000)/100000), (math.ceil(drawline[0][1]*100000)/100000), (math.ceil(drawline[1][0]*100000)/100000), (math.ceil(drawline[1][1]*100000)/100000)))
                #dxfAddLine(filepath, line=((math.ceil(drawline[0][0]*100)/100), (math.ceil(drawline[0][1]*100)/100), (math.ceil(drawline[1][0]*100)/100), (math.ceil(drawline[1][1]*100)/100)))

        print(" ")
        print("objectlines")
        for f in objectlines:
            print(f)
        
        finallinelist = []
        newlineset = True
        while len(objectlines) > 0:
            print(" ")
            print("While Loop " + str(len(objectlines)))
            if newlineset == True:
                print("newlineset = true")
                print(objectlines[0])
                finallinelist.append(objectlines[0])
                objectlines.remove(objectlines[0])
                newlineset = False
            
            else:
                print("newlineset = false")
                foundmatch = False
                for itm in objectlines:
                    
                    #if finallinelist[-1][2] == itm[0] and finallinelist[-1][3] == itm[1]:
                    if checkrange(finallinelist[-1][2], itm[0]) and checkrange(finallinelist[-1][3], itm[1]):
                        print("First")
                        print(itm)
                        foundmatch = True
                        finallinelist.append((itm[0],itm[1],itm[2],itm[3]))
                        objectlines.remove(itm)
                        break 
                        
                    #elif finallinelist[-1][2] == itm[2] and finallinelist[-1][3] == itm[3]:
                    elif checkrange(finallinelist[-1][2], itm[2]) and checkrange(finallinelist[-1][3], itm[3]):
                        print("Second")
                        print(itm)
                        print((itm[2],itm[3],itm[0],itm[1]))
                        foundmatch = True
                        finallinelist.append((itm[2],itm[3],itm[0],itm[1]))
                        objectlines.remove(itm)
                        break
                
                if foundmatch == False:        
                    newlineset = True
                    
        print("Final List")            
        for itm in finallinelist: 
            print(itm)
            dxfAddLine(filepath, (itm[0],itm[1],itm[2],itm[3]))
            
            #export gcode file with toolup and tooldown labels
            
            
    dxfOpen(filepath) #Write DXF Header
    
    #Call once for each object.
    for ob in bpy.data.objects:
        if ob.type == 'MESH' and ob.name == objname1:
            exportdxf(ob.name, filepath, cut)
        elif ob.type == 'MESH' and objname1 == "":
            exportdxf(ob.name, filepath, cut)

    dxfClose(filepath) #Close the DXF file.
        
