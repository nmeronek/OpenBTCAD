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
    f.write('X' + str(point[0]) + ' Y' + str(point[1]) + '\n')
    f.close()


#Write gcode text.
def gcodeAddText(filepath, teststring):
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
        
        
        
#returns true if point matches
def checkpoint(xval1, yval1, xval2, yval2):
    if checkrange(xval1, xval2) == True and checkrange(yval1, yval2) == True:
        return True
    else:
        return False
        
        



def z0xycoords(pointA,pointB):
	""" Takes two three-dimensional coordinates (x,y,z) in list or tuple form.
	Computes the x and y coordinates of the line at the z=0 plane.
	Returns a list of length 2 with the x and y coords.
	"""
	if (pointA[2] == 0): #Point A is on the z=0 plane already
		return pointA
	elif (pointB[2] == 0 ): #Point B is on the z=0 plane already
		return pointB
	elif (pointA[2]*pointB[2] > 0 ): # Both points fall on the same side of the z=0 plane, so we cannot compute an answer
		return False
	else:
		totaldiff = [(pointA[i]-pointB[i]) for i in range(3)] # The differences between the x,y, and z coordinates of the two points
		xy = [ ( pointA[i] - totaldiff[i]*float(pointA[2])/totaldiff[2]) for i in range(2) ] # in each dimension, endpoint minus (difference times ratio of z)
		return xy 
        
        
        
#Return cross section of object through Z0, return each line as tuple x0,y0,x1,y1
def objLineList(objname):
    
    obj = bpy.data.objects[objname]
    wm = bpy.data.objects[objname].matrix_world
    
    #print("Generate X Section of: " + objname)

    #Get each polygon out of an object.
    finallinelist = []
    for eachpolygon in obj.data.polygons:
        #get each vertex out of each polygon. add to eachvertexlist. vertex list is re-populated for each polygon.
        eachvertexlist = []
        for eachvertex in eachpolygon.vertices:
            #print(wm * obj.data.vertices[eachvertex].co)
            #print("Each Vertex in Each Polygon")
            eachvertexlist.append(wm * obj.data.vertices[eachvertex].co)
        #print("Each Vertex found and added to list")
        
        #create line from each polygon that crosses Z0    
        prev_vertex = None
        polygonline = [] 
        for avertex in eachvertexlist:
            if prev_vertex == None:
                prev_vertex = avertex
                xyvalue = z0xycoords((eachvertexlist[-1][0], eachvertexlist[-1][1], eachvertexlist[-1][2]), (avertex[0], avertex[1], avertex[2]))
                if xyvalue != False:
                    polygonline.append(xyvalue)
                continue
            else:
                xyvalue = z0xycoords((prev_vertex[0], prev_vertex[1], prev_vertex[2]), (avertex[0], avertex[1], avertex[2]))
                if xyvalue != False:
                    polygonline.append(xyvalue)
                prev_vertex = avertex
                
          
        if polygonline != []:
            finallinelist.append((polygonline[0][0], polygonline[0][1], polygonline[1][0], polygonline[1][1]))
    #print("X Section Complete")
    return finallinelist
    
    
    
    
#Sorts line list into toolpath order with section breaks
def SortLineList(linelist):
    finallinelist = []
    newlineset = True
    matchfound = True
    bpy.context.window_manager.progress_begin(0,len(linelist))
    while len(linelist) > 0:
        bpy.context.window_manager.progress_update(len(linelist))
        if newlineset == True:
            newlineset = False
            finallinelist.append("NewLineSet")
            finallinelist.append(linelist[0])
            linelist.remove(linelist[0])
            
        else:
            matchfound = False
            for line in linelist:
                if checkpoint(finallinelist[-1][2], finallinelist[-1][3], line[0], line[1]) == True:
                    finallinelist.append((line[0], line[1], line[2], line[3]))
                    linelist.remove(line)
                    matchfound = True        
                
                elif checkpoint(finallinelist[-1][2], finallinelist[-1][3], line[2], line[3]) == True:
                    finallinelist.append((line[2], line[3], line[0], line[1]))
                    linelist.remove(line)
                    matchfound = True
            
            if matchfound == False:
                newlineset = True
    bpy.context.window_manager.progress_end()
    return finallinelist                
            
            



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


#Change material of object.
def objSetMaterial(objname1, color=(1,1,1), transparency=1):
    object1 = objReturnByName(objname1)
    if object1 == None:
        print("Bad parameter in objSetMaterial: " + str(objname1) + ", " + str(color) + ", " + str(transparency))
        print("objname1 does not exist")
        return
        
    if len(color) != 3:
        print("Bad parameter in objSetMaterial: " + str(objname1) + ", " + str(color) + ", " + str(transparency))
        print("color must contain a 3 number tuple with values between 0 and 1")
        return
    
    #Place holder, not implemented yet.    
    if isinstance(transparency, (int, float)) != True or transparency < 0:
        print("Bad parameter in objSetMaterial: " + str(objname1) + ", " + str(color) + ", " + str(transparency))
        print("transparency must be a number not less than 0")
        return
    
    tempmaterial = "material-" + objname1    
        
    #Create material based on object name if it doesn't exist
    if bpy.data.materials.get(tempmaterial) == None:
        bpy.data.materials.new(tempmaterial)
        
    #Change material properties
    bpy.data.materials[tempmaterial].diffuse_color = color
    
    #Assign material to object
    object1.data.materials.append(bpy.data.materials[tempmaterial])
    
    

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
        linelist = objLineList(objname1)
        linelist2 = SortLineList(linelist)
        
        for itm in linelist2:
            if itm != "NewLineSet":
                dxfAddLine(filepath, (itm[0],itm[1],itm[2],itm[3]))
        
        
        
    dxfOpen(filepath) #Write DXF Header
    
    #Call once for each object.
    if objname1 != "":
        for ob in bpy.data.objects:
            if ob.type == 'MESH' and ob.name == objname1:
                exportdxf(ob.name, filepath, cut)
    else:
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                exportdxf(ob.name, filepath, cut)

    dxfClose(filepath) #Close the DXF file.





#bt.objExportGCODE("Cube", "/home/graydude/testfile.gcode")
#Exports a single object as gcode or all objects if not specified.
def objExportGCODE(objname1="", filepath="", cut=True, roundvalues=5):
    def exportgcode(objnametemp, filepath=filepath, cut=cut, roundvalues=roundvalues):
        
        linelist = objLineList(objnametemp)
        linelist2 = SortLineList(linelist)
        
        newlineset = False
        for itm in linelist2:
            if newlineset == True:
                newlineset = False
                gcodeAddText(filepath, "toolup")
                gcodeAddPoint(filepath, (round(itm[0], roundvalues), round(itm[1], roundvalues)))
                gcodeAddText(filepath, "tooldown")
                
            if itm == "NewLineSet":
                newlineset = True
                continue
            else:
                gcodeAddPoint(filepath, (round(itm[2], roundvalues), round(itm[3], roundvalues)))
                
                    
                    
    gcodeOpen(filepath) #Write GCode Header
    
    #Call once for each object.
    if objname1 != "":
        for ob in bpy.data.objects:
            if ob.type == 'MESH' and ob.name == objname1:
                exportgcode(ob.name, filepath, cut)
    else:
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                exportgcode(ob.name, filepath, cut)
        
        
    gcodeAddText(filepath, "toolup")
    gcodeClose(filepath) #Close the GCode file.
