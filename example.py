import openbtcad as bt


#Global variables used to define stuff.
platethin = 10.5

bolt1 = 8


#example of a simple part
def mysimplepart(objname):
    #Get object locori then delete object.
    locori = bt.getLocOri(objname)
    bt.objDelete(objname)
    bt.objUnSelect()
    
    #Main Block
    bt.objAddCube(objname,(110,50,platethin))

    #Bolt Holes
    bt.objAddCylinder("tempbolt",(bolt1,bolt1,platethin+1))
    bt.objMove("tempbolt", (bt.objMin(objname)[0]+15,0,0))
    bt.objModBool(objname, "tempbolt", 'DIFFERENCE')
    bt.objMove("tempbolt", (bt.objMin(objname)[0]+95,0,0))
    bt.objModBool(objname, "tempbolt", 'DIFFERENCE')
    bt.objDelete("tempbolt")
    
    #Set Material Properties
    bt.objSetMaterial(objname, (.2, .3, .4))

    #Move final object back to original position.
    bt.setLocOri(objname, locori)
    bt.objUnSelect()




#This updates all copies of the part in blender.
objlist = bt.objReturnNameList("mysimplepart")
for itm in objlist:
    mysimplepart(itm)

