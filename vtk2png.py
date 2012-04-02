#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# by Panos Mavrogiorgos, email: pmav99 <> gmail
# mods by jonas juselius <jonas.juselius@uit.no>

import sys
sys.path.append('/usr/lib/paraview')

#import paraview.vtk 
#from paraview.servermanager import *
import vtk 
import time
from argparse import ArgumentParser

parser = ArgumentParser(description = "Convert legacy VTK files to .png")
parser.add_argument('infile', nargs=1,
        action='store',
        default=None,
        help='name of input file in .vtk format',
        metavar='input.vtk')
parser.add_argument('outfile', nargs='?',
        action='store',
        default=None,
        help='name of output file in .png format',
        metavar='output.png')
parser.add_argument('--size',
        action='store',
        type=int,
        default=808,
        help='size of generated picture N x N' 
        '[default: %(default) x %(default)',
        metavar='N')
parser.add_argument('--colors',
        action='store',
        choices=('default', 'bw', 'wb'),
        default='default',
        help='color scheme')

args = parser.parse_args()

def main():
# Turn on off-screen rendering, if available
#    gfx_factory = vtk.vtkGraphicsFactory()
#    gfx_factory.SetOffScreenOnlyMode(1)
#    gfx_factory.SetUseMesaClasses(1)

#    img_factory = vtk.vtkImagingFactory()
#    img_factory.SetUseMesaClasses(1)

    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(args.infile[0])
    reader.Update() # Needed because of GetScalarRange
    output = reader.GetOutput()
    scalar_range = output.GetScalarRange()

# Create the mapper that corresponds the objects of the vtk file
# into graphics elements
    mapper = vtk.vtkPolyDataMapper()
#    mapper = vtk.vtkDataSetMapper()
    mapper.SetInput(output)
    mapper.SetScalarRange(scalar_range)
    mapper.SetScalarMaterialModeToDiffuse()
    mapper.SetScalarMaterialModeToAmbientAndDiffuse()
    mapper.SetScalarMaterialModeToAmbientAndDiffuse()

    transform = vtk.vtkTransform()
    transform.RotateX(75.0)
# Create the Actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.SetOrigin(0.0, 0.0, 0.0)
    actor.SetUserTransform(transform)
    props = actor.GetProperty()
#    props.SetAmbientColor(0.4, 1.0, 0.5)
    props.SetDiffuseColor(0.3, 0.2, 1.0)
    props.SetOpacity(1.0)
    props.SetLineWidth(1.0)


# Create the Renderer
    renderer1 = vtk.vtkRenderer()
    renderer1.AddActor(actor)
    renderer1.SetBackground(0.1, 0.2, 0.31) 
    renderer1.SetViewport(0.0, 0.0, 0.5, 1.0) 
    camera1 = renderer1.GetActiveCamera()

    renderer2 = vtk.vtkRenderer()
    renderer2.AddActor(actor)
    renderer2.SetBackground(0.1, 0.2, 0.31) 
    renderer2.SetViewport(0.5, 0.0, 1.0, 1.0) 
    renderer2.SetActiveCamera(camera1)
#    camera2 = renderer1.GetActiveCamera()

#    light = vtk.vtkLight()
#    light.SetFocalPoint(0.0, 0.0, 0.0)
#    light.SetPosition(0.0, 0.0, 1.0)
#    light.SetColor(1.0, 0.0, 0.0)
#    light.SetIntensity(0.5)
#    renderer1.AddLight(light)
    light_kit = vtk.vtkLightKit()
    light_kit.AddLightsToRenderer(renderer1)
    light_kit.SetHeadLightWarmth(0.1)
    light_kit.SetFillLightWarmth(0.1)
    light_kit.SetKeyLightWarmth(0.9)
    light_kit.SetKeyLightAzimuth(10.9)

    camera1.SetViewUp(0.0, 0.0, 1.0)
    camera1.SetPosition(-1.0, 0.0, 0.0)
    camera1.ParallelProjectionOn()
    camera1.SetFocalPoint(0.0, 0.0, 0.0)
    camera1.SetViewAngle(45)

#    camera2.SetViewUp(0.0, 0.0, 1.0)
#    camera2.SetPosition(0.0, 1.0, 0.0)
#    camera2.ParallelProjectionOn()
#    camera2.SetFocalPoint(0.0, 0.0, 0.0)
#    camera2.SetViewAngle(45)

    renderer1.ResetCamera()
    renderer2.ResetCamera()

# Create the RendererWindow
    renderer_window = vtk.vtkRenderWindow()
    renderer_window.AddRenderer(renderer1)
    renderer_window.AddRenderer(renderer2)
    renderer_window.SetSize(1000,500)
#    renderer_window.SetOffScreenRendering(1)

#    renderer_window.Render()

# Create the RendererWindowInteractor and display the vtk_file
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderer_window)
    interactor.Initialize()
    interactor.Start()

    # screenshot code:
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renderer_window)
    w2if.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName("screenshot.png")
    writer.SetInput(w2if.GetOutput())
    writer.Write()

if __name__ == '__main__':
    main()
# vim:et:sw=4
