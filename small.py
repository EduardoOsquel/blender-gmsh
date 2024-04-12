# Author: Eduardo Osquel Perez Rivero
# Script: Remeshing an STL file without an underlying CAD model

import gmsh
import math
import sys

gmsh.initialize()

def createGeometryAndMesh(stl_file_path, remeshed_path, elements_size):
    gmsh.clear()

    # Set the file as parameter to execute python convert.py /path/to/the/mesh.stl
    gmsh.merge(stl_file_path)

    # First we clean the STL default triangles
    # Iterate over all surfaces in the model
    for surf_tag in gmsh.model.getEntities(2):
        # Apply the setRecombine constraint to each surface
        gmsh.model.geo.mesh.setRecombine(2, surf_tag[1])

    angle = gmsh.onelab.getNumber('Parameters/Angle for surface detection')[0]
    forceParametrizablePatches = gmsh.onelab.getNumber('Parameters/Create parametrizable surfaces')[0]
    includeBoundary = True
    curveAngle = 180

    gmsh.model.mesh.classifySurfaces(angle * math.pi / 180., includeBoundary, forceParametrizablePatches, curveAngle * math.pi / 180.)
    gmsh.model.mesh.createGeometry()

    s = gmsh.model.getEntities(2)
    l = gmsh.model.geo.addSurfaceLoop([e[1] for e in s])
    gmsh.model.geo.addVolume([l])
    gmsh.model.geo.synchronize()

    gmsh.model.mesh.setSize(gmsh.model.getEntities(0), float(elements_size))

    gmsh.model.mesh.generate(3)
    
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
    "name":"Parameters/Create parametrizable surfaces",
    "values":[0],
    "choices":[0, 1]
  }
]""")

# Create the geometry and mesh it:
stl_file_path = sys.argv[1]
remeshed_path = sys.argv[2]
elements_size = sys.argv[3]
createGeometryAndMesh(stl_file_path, remeshed_path, elements_size)

# Launch the GUI and handle the "check" event to recreate the geometry and mesh
# with new parameters if necessary:
def checkForEvent():
    action = gmsh.onelab.getString("ONELAB/Action")
    if len(action) and action[0] == "check":
        gmsh.onelab.setString("ONELAB/Action", [""])
        stl_file_path = sys.argv[1]
        remeshed_path = sys.argv[2]
        elements_size = sys.argv[3]
        createGeometryAndMesh(stl_file_path, remeshed_path, elements_size)
        gmsh.graphics.draw()
    return True

if "-nopopup" not in sys.argv:
    gmsh.fltk.initialize()
    while gmsh.fltk.isAvailable() and checkForEvent():
        gmsh.fltk.wait()

gmsh.finalize()
