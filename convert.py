# Author: Eduardo Osquel Perez Rivero
# Script: Remeshing an STL file without an underlying CAD model

import gmsh
import math
import sys

gmsh.initialize()

def createGeometryAndMesh(stl_file_path, remeshed_path):
    gmsh.clear()

    # Set the file as parameter to execute python convert.py /path/to/the/mesh.stl
    gmsh.merge(stl_file_path)

    angle = gmsh.onelab.getNumber('Parameters/Angle for surface detection')[0]
    forceParametrizablePatches = gmsh.onelab.getNumber('Parameters/Create surfaces guaranteed to be parametrizable')[0]
    includeBoundary = True
    curveAngle = 180

    gmsh.model.mesh.classifySurfaces(angle * math.pi / 180., includeBoundary, forceParametrizablePatches, curveAngle * math.pi / 180.)
    gmsh.model.mesh.createGeometry()

    s = gmsh.model.getEntities(2)
    l = gmsh.model.geo.addSurfaceLoop([e[1] for e in s])
    gmsh.model.geo.addVolume([l])
    gmsh.model.geo.synchronize()

    f = gmsh.model.mesh.field.add("MathEval")
    if gmsh.onelab.getNumber('Parameters/Apply funny mesh size field?')[0]:
        gmsh.model.mesh.field.setString(f, "F", "2*Sin((x+y)/5) + 3")
    else:
        gmsh.model.mesh.field.setString(f, "F", "4")
    gmsh.model.mesh.field.setAsBackgroundMesh(f)

    gmsh.model.mesh.generate(3)
    
    # gmsh.write('remeshed.msh')

    # Write the file name as second parameter string
    gmsh.write(remeshed_path + '.msh')

# Create ONELAB parameters with remeshing options:
gmsh.onelab.set("""[
  {
    "type":"number",
    "name":"Parameters/Angle for surface detection",
    "values":[40],
    "min":20,
    "max":120,
    "step":1
  },
  {
    "type":"number",
    "name":"Parameters/Create surfaces guaranteed to be parametrizable",
    "values":[0],
    "choices":[0, 1]
  },
  {
    "type":"number",
    "name":"Parameters/Apply funny mesh size field?",
    "values":[0],
    "choices":[0, 1]
  }
]""")

# Create the geometry and mesh it:
stl_file_path = sys.argv[1]
remeshed_path = sys.argv[2]
createGeometryAndMesh(stl_file_path, remeshed_path)

# Launch the GUI and handle the "check" event to recreate the geometry and mesh
# with new parameters if necessary:
def checkForEvent():
    action = gmsh.onelab.getString("ONELAB/Action")
    if len(action) and action[0] == "check":
        gmsh.onelab.setString("ONELAB/Action", [""])
        stl_file_path = sys.argv[1]
        remeshed_path = sys.argv[2]
        createGeometryAndMesh(stl_file_path, remeshed_path)
        gmsh.graphics.draw()
    return True

if "-nopopup" not in sys.argv:
    gmsh.fltk.initialize()
    while gmsh.fltk.isAvailable() and checkForEvent():
        gmsh.fltk.wait()

gmsh.finalize()
