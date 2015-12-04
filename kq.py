# Make a 3D model of the Klein Quartic

''' Copyright 2015 Tim Hutton <tim.hutton@gmail.com>

    This file is part of klein-quartic.

    klein-quartic is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    klein-quartic is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with klein-quartic. If not, see <http://www.gnu.org/licenses/>.
'''
    
try:
    import vtk
except ImportError:
    print "\nThis script uses VTK, which you don't seem to have installed.\n"
    print "On Ubuntu: sudo apt-get install python-vtk, and then run with 'python kq.py'\n"
    print "On Windows: download python installer from http://vtk.org, install, add the bin folder to your PATH\n"
    print "(eg. 'C:\Program Files\VTK-6.3.0\bin') and then run with 'vtkpython kq.py'"
    exit(1)
    
import itertools
import math
from math_functions import *
import random

# first make a tetrahedron
r6 = math.sqrt(6)
r3 = math.sqrt(3)
tet_verts = [ (0,0,-r6/2), (-r3/3,1,r6/6), (2*r3/3,0,r6/6), (-r3/3,-1,r6/6) ]
tet_edges = list( itertools.combinations(range(4),2) )

# and a nested one
inner_tet_verts = [ mul(p,0.6) for p in tet_verts ]

# then make a staggered ring of 8 vertices halfway along each edge of the tetrahedron
tet_centers = [ av( tet_verts[i], inner_tet_verts[i] ) for i in range(4) ]
arm_centers = [ av( tet_centers[a], tet_centers[b] ) for a,b in tet_edges ]
arm_edges = [ av( tet_verts[a], tet_verts[b] ) for a,b in tet_edges ]
twist = [ 1.5, 2.5+1-0.5, 3.5-0.5, 4.5+0.5, 5.5-1+0.5, 6.5, 7.5-1, 8.5+1 ]
stagger = [ 0.1, -0.1, 0.25, -0.25, 0.1, -0.1, 0.3, -0.3 ]
radius = [ 0.7, 1, 1, 1, 1, 0.7, 1, 1 ]
arm_sides = [ add( add( add( arm_centers[i], \
                             mul( cross( sub( arm_edges[i], arm_centers[i] ), sub( tet_verts[a], arm_centers[i] ) ), radius[j] * math.sin(twist[j]*2*math.pi/8) ) ), \
                             mul( sub( arm_edges[i], arm_centers[i] ), radius[j] * math.cos(twist[j]*2*math.pi/8) ) ), \
                             mul( sub( tet_verts[a], arm_centers[i] ), stagger[j] ) ) \
              for i,(a,b) in enumerate(tet_edges) for j in range(8) ]

# then join the vertices together to make 12 outer heptagons and 12 inner ones
outer_faces = [ (0,8,9,10,30,31,24),   (0,24,25,26,22,23,16), (0,16,17,18,14,15,8),
                (1,13,12,11,38,39,32), (1,32,33,34,46,47,40), (1,40,41,42,15,14,13),
                (2,21,20,19,54,55,48), (2,48,49,50,39,38,37), (2,37,36,35,23,22,21),
                (3,29,28,27,47,46,45), (3,45,44,43,55,54,53), (3,53,52,51,31,30,29) ]
inner_faces = [ (4,12,13,14,18,19,20), (4,20,21,22,26,27,28), (4,28,29,30,10,11,12),
                (5,9,8,15,42,43,44),   (5,44,45,46,34,35,36), (5,36,37,38,11,10,9), 
                (6,17,16,23,35,34,33), (6,33,32,39,50,51,52), (6,52,53,54,19,18,17),
                (7,25,24,31,51,50,49), (7,49,48,55,43,42,41), (7,41,40,47,27,26,25) ]
                
def outer_as_tris( f ):
    '''Given an outer heptagon, return the desired triangles.'''
    ind = [ (0,1,3), (1,2,3), (0,3,4), (0,4,6), (4,5,6) ]
    return [ (f[t[0]],f[t[1]],f[t[2]]) for t in ind ]

def inner_as_tris( f ):
    '''Given an inner heptagon, return the desired triangles.'''
    ind = [ (0,1,3), (1,2,3), (0,3,4), (0,4,6), (6,4,5) ]
    return [ (f[t[0]],f[t[1]],f[t[2]]) for t in ind ]
    
outer_faces_as_tris = flatten( outer_as_tris(f) for f in outer_faces )
inner_faces_as_tris = flatten( inner_as_tris(f) for f in inner_faces )
                
# for better shape we move the tetrahedron vertices inwards
corner_verts = [ mul(p,0.6) for p in tet_verts+inner_tet_verts ]

outputOBJ( corner_verts + arm_sides, outer_faces + inner_faces, 'kq.obj' ) # this one is 'correct' but has bent faces which most packages seem to find hard
outputOBJ( corner_verts + arm_sides, outer_faces_as_tris + inner_faces_as_tris, 'kq_surface.obj' ) # this one has the wrong topology but is triangulated
print 'Outputted kq.obj and kq_surface.obj'

# In Paraview, I opened kq.obj and applied these filters: Extract Edges, Tube. Then I opened kq_surface.obj and rendered it as a surface. This dual rendering
# allows us to emphasise the real edges, not the internal ones.

# ------ visualise with VTK --------
    
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
track = vtk.vtkInteractorStyleTrackballCamera()
iren.SetInteractorStyle(track)
ren.SetBackground(0.95, 0.9, 0.85)
renWin.SetSize(800, 600)
  
surface = makePolyData( corner_verts + arm_sides, outer_faces_as_tris + inner_faces_as_tris )
edges = makePolyData( corner_verts + arm_sides, outer_faces + inner_faces )

kq_ids    = [ 1, 2, 0, 23, 20, 8, 22, 19, 7, 21, 18, 6, 12, 14, 13, 3, 17, 11, 5, 16, 10, 4, 15, 9 ]
plane_ids = [ 0, 1, 2, 3, 4, 5, 6, 10, 11, 7, 8, 9, 13, 17, 12, 101, 102, 15, 14, 16, 100, 20, 103, 21, 19, 104, 105, 106, 107, 108, 22, 18, 23 ]

cellIds = flatten( [i]*5 for i in kq_ids ) # each of the 24 heptagons is made of 5 triangles
surfaceCellData = vtk.vtkFloatArray()
for val in cellIds:
    surfaceCellData.InsertNextValue( val )
surface.GetCellData().SetScalars( surfaceCellData )

lut = vtk.vtkLookupTable()
lut.SetNumberOfTableValues(25)
lut.Build()
for i in range(24):
    rgb = vtk.vtkMath.HSVToRGB( random.random(), random.uniform(0.5,1), random.uniform(0.7,1) )
    lut.SetTableValue( i, ( rgb[0], rgb[1], rgb[2], 1 ) )
lut.SetTableValue( 24, 1, 1, 1 )

surfaceMapper = vtk.vtkPolyDataMapper()
if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
    surfaceMapper.SetInputData(surface)
else:
    surfaceMapper.SetInput(surface)
surfaceMapper.SetScalarRange(0,24)
surfaceMapper.SetLookupTable(lut)
surfaceActor = vtk.vtkActor()
surfaceActor.SetMapper(surfaceMapper)
ren.AddActor(surfaceActor)

lines = vtk.vtkExtractEdges()
if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
    lines.SetInputData(edges)
else:
    lines.SetInput(edges)
tube = vtk.vtkTubeFilter()
tube.SetInputConnection(lines.GetOutputPort())
tube.SetRadius(0.005)
tube.SetNumberOfSides(20)

sphere = vtk.vtkSphereSource()
sphere.SetRadius(0.005)
sphere.SetPhiResolution(20)
sphere.SetThetaResolution(20)
vertices = vtk.vtkGlyph3D()
if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
    vertices.SetInputData(edges)
else:
    vertices.SetInput(edges)
vertices.SetSourceConnection(sphere.GetOutputPort())

borders = vtk.vtkAppendPolyData()
borders.AddInputConnection(tube.GetOutputPort())
borders.AddInputConnection(vertices.GetOutputPort())
tubeMapper = vtk.vtkPolyDataMapper()
tubeMapper.SetInputConnection(borders.GetOutputPort())
tubeActor = vtk.vtkActor()
tubeActor.SetMapper(tubeMapper)
tubeActor.GetProperty().SetColor(0,0,0)
ren.AddActor(tubeActor)

plane = getDual( getHyperbolicPlaneTiling( 3, 7, 9  ) ) # (we do it this way to get a vertex at the center instead of a cell)
plane_trans = vtk.vtkTransform()
plane_trans.Translate(0,0,-0.75)
plane_trans.Scale(0.7,0.7,0.7)
trans = vtk.vtkTransformPolyDataFilter()
trans.SetTransform(plane_trans)
if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
    trans.SetInputData(plane)
else:
    trans.SetInput(plane)
trans.Update()
plane_scalars = vtk.vtkIntArray()
plane_scalars.SetNumberOfValues( trans.GetOutput().GetNumberOfPolys() )
for i in range( trans.GetOutput().GetNumberOfPolys() ):
    plane_scalars.SetValue( i, plane_ids[ i ] if i in range( len( plane_ids ) ) else 99 )
trans.GetOutput().GetCellData().SetScalars( plane_scalars )

planeMapper = vtk.vtkPolyDataMapper()
if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
    planeMapper.SetInputData( trans.GetOutput() )
else:
    planeMapper.SetInput( trans.GetOutput() )
planeMapper.SetLookupTable(lut)
planeMapper.SetScalarModeToUseCellData()
planeMapper.SetScalarRange(0,24)
planeActor = vtk.vtkActor()
planeActor.SetMapper(planeMapper)
planeActor.GetProperty().EdgeVisibilityOn()
planeActor.GetProperty().SetAmbient(1)
planeActor.GetProperty().SetDiffuse(0)
ren.AddActor(planeActor)

cell_centers = vtk.vtkCellCenters()
if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
    cell_centers.SetInputData( trans.GetOutput() )
else:
    cell_centers.SetInput( trans.GetOutput() )
plane_labels = vtk.vtkLabeledDataMapper()
plane_labels.SetLabelModeToLabelScalars()
plane_labels.SetInputConnection(cell_centers.GetOutputPort())
plane_labels_actor = vtk.vtkActor2D()
plane_labels_actor.SetMapper(plane_labels)
#ren.AddActor(plane_labels_actor)

kq_cell_centers = vtk.vtkCellCenters()
if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
    kq_cell_centers.SetInputData(surface)
else:
    kq_cell_centers.SetInput(surface)
kq_labels = vtk.vtkLabeledDataMapper()
kq_labels.SetInputConnection(kq_cell_centers.GetOutputPort())
kq_labels.SetLabelModeToLabelScalars()
kq_labels.SetLabelFormat("%.0f")
kq_labels.GetLabelTextProperty().SetJustificationToCentered()
kq_labels.GetLabelTextProperty().SetVerticalJustificationToCentered()
kq_labels_actor = vtk.vtkActor2D()
kq_labels_actor.SetMapper(kq_labels)
#ren.AddActor(kq_labels_actor)

iren.Initialize()
 
ren.ResetCamera()
ren.GetActiveCamera().Zoom(1.5)
renWin.Render()
 
iren.Start()
