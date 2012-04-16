#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Program to visualize dust bunnies.
# Jonas Juselius <jonas.juselius@uit.no> 04/2012
#

import vtk
from argparse import ArgumentParser

parser = ArgumentParser(description="Convert legacy VTK files to .png")
parser.add_argument('infile', nargs='+',
        action='store',
        default=None,
        help='name of input file in .vtk format',
        metavar='file.vtk')
parser.add_argument('--outfile', '-o', nargs=1,
        action='store',
        default=None,
        help='name of output file in .png format',
        metavar='file.png')
parser.add_argument('--size', '-s',
        action='store',
        type=int,
        default=800,
        help='picture tile size (N x N) '
        '[default: %(default)s x %(default)s]',
        metavar='N')
parser.add_argument('--separation', '-S',
        action='store',
        type=int,
        default=45,
        help='separation of actors in combi-view mode'
        '[default: %(default)s]', metavar='N')
parser.add_argument('--color-scheme', '-c',
        action='store',
        choices=('default', 'bw', 'wb'),
        default='default',
        help='color scheme')
parser.add_argument('--fiber', '-f',
        action='store_true',
        default=False,
        help='render using 3D fibers')
parser.add_argument('--rotations', '-r',
        action='store_true',
        default=False,
        help='Use different rotations for each tile')
parser.add_argument('--offscreen', '-x',
        action='store_true',
        default=False,
        help='Use offscreen rendering if available')
parser.add_argument('--multiview', '-m',
        action='store_true',
        default=False,
        help='Render each file in a separate viewport')

args = parser.parse_args()


def main():
    renderers = []
    rotor = 0
    if not args.multiview:
        if len(args.infile) > 2:
            raise RuntimeError(
                    'Combi-view not supported for more than 2 files')
        if len(args.infile) > 1:
            args.rotations = True
        viewports = get_viewports(1)
        renderers.append(create_renderer(viewports[0]))
        for i in args.infile:
            actor = create_actor(i)
            transform_combiview(actor, rotor, args.separation)
            renderers[0].AddActor(actor)
            if args.rotations:
                rotor += 1
            renderers[0].ResetCamera()
        renderers[0].ResetCamera()
    else:
        viewports = get_viewports(len(args.infile))
        for i, v in zip(args.infile, viewports):
            actor = create_actor(i)
            transform_multiview(actor, rotor)
            if args.rotations:
                rotor += 1
            renderers.append(create_renderer(v, actor))

    camera = renderers[0].GetActiveCamera()
    for i in renderers[1:]:
        i.SetActiveCamera(camera)
    window = create_scene(renderers)
    if args.outfile:
        save_screenshot(args.outfile[0], window, args.offscreen)
    else:
        view_scene(window)


def get_viewports(n):
    viewports = []
    if n == 1:
        viewports.append((0.0, 0.0, 1.0, 1.0))
    elif n == 2:
        viewports.append((0.0, 0.0, 0.5, 1.0))
        viewports.append((0.5, 0.0, 1.0, 1.0))
    elif n == 3:
        viewports.append((0.0, 0.0, 0.333333, 1.0))
        viewports.append((0.333333, 0.0, 0.666666, 1.0))
        viewports.append((0.666666, 0.0, 1.0, 1.0))
    elif n == 4:
        viewports.append((0.0, 0.5, 0.5, 1.0))
        viewports.append((0.5, 0.5, 1.0, 1.0))
        viewports.append((0.0, 0.0, 0.5, 0.5))
        viewports.append((0.5, 0.0, 1.0, 0.5))
    return viewports


def create_actor(fname=None):
    if fname:
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(fname)
        reader.Update()
        prop = reader
    else:
        prop = vtk.vtkCubeSource()  # for testing

    if args.fiber:
        tube = vtk.vtkTubeFilter()
        tube.SetInputConnection(reader.GetOutputPort())
        prop = tube

# Create the mapper that corresponds the objects of the vtk file
# into graphics elements
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(prop.GetOutputPort())
#    mapper.SetScalarMaterialModeToAmbientAndDiffuse()

# Create the Actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    bbox = actor.GetBounds()
    o = []
    for i in range(3):
        m = i * 2
        n = m + 1
        o.append((bbox[n] + bbox[m]) / 2.0)
    actor.SetOrigin(o)
# Set actor properties
    props = actor.GetProperty()
    props.SetAmbientColor(0.6, 0.6, 0.6)
    if args.color_scheme == 'wb' and not args.fiber:
        props.SetDiffuseColor(0.1, 0.1, 0.1)
    else:
        props.SetDiffuseColor(0.9, 0.9, 0.9)
#    props.SetOpacity(0.3)
#    props.SetLineWidth(1)
#    props.SetRepresentationToSurface()
#    props.SetRepresentationToWireframe()
    return actor

def transform_multiview(actor, rotation=0):
    if rotation == 0:
        actor.RotateY(-90.0)
    elif rotation == 1:
        actor.RotateY(90.0)
    elif rotation == 2:
        actor.RotateX(-90.0)
        actor.RotateZ(0.0)
    elif rotation == 3:
        actor.RotateZ(-90.0)
    else:
        raise RuntimeError('Invalid transformation spec. This is a bug')

def transform_combiview(actor, rotation=0, transl=45):
    if rotation == 0:
        actor.RotateY(-90.0)
        transl = -transl
    elif rotation == 1:
        actor.RotateY(90.0)
    else:
        raise RuntimeError('Invalid transformation spec. This is a bug')
    actor.AddPosition(transl, 0.0, 0.0)

def create_renderer(viewport=None, actor=None):
# Create the Renderer
    renderer = vtk.vtkRenderer()
    if args.color_scheme == 'bw':
        renderer.SetBackground(0.0, 0.0, 0.0)
    elif args.color_scheme == 'wb':
        renderer.SetBackground(1.0, 1.0, 1.0)
    else:
        renderer.SetBackground(0.1, 0.2, 0.31)
    if viewport:
        renderer.SetViewport(viewport)

    light_kit = vtk.vtkLightKit()
    light_kit.AddLightsToRenderer(renderer)
    light_kit.SetHeadLightWarmth(0.2)
    light_kit.SetFillLightWarmth(0.5)
    light_kit.SetKeyLightWarmth(0.5)
    light_kit.SetKeyLightAzimuth(0.0)

#    camera = renderer.GetActiveCamera()
#    camera.SetViewUp(0.0, 0.0, 1.0)
#    camera.SetPosition(0.0, 0.0, 50.0)
#    camera.ParallelProjectionOn()
#    camera.SetFocalPoint(0.0, 0.0, 0.0)
#    camera.SetViewAngle(45)

    if actor:
        renderer.AddActor(actor)
    renderer.ResetCamera()
    return renderer


def create_scene(renderers):
    n = len(renderers)
    if n < 4:
        sx = args.size * n
        sy = args.size
    elif n == 4:
        sx = sy = args.size * 2
    else:
        raise ValueError("Too many input files!")

# Create the RendererWindow
    window = vtk.vtkRenderWindow()
    window.SetSize(sx, sy)
    for i in renderers:
        window.AddRenderer(i)
    return window


def view_scene(window):
# Create an interactor and display the vtk_file
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)
    interactor.RemoveObservers('UserEvent')
    interactor.AddObserver('UserEvent', dump_screen, 1.0)
    interactor.Initialize()
    interactor.Start()


def save_screenshot(fname, window, offscreen=False):
    if offscreen:
        set_off_screen_rendering(window)
    window.Render()
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(window)
    w2if.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(fname)
    writer.SetInput(w2if.GetOutput())
    writer.Write()


def dump_screen(obj, event):
    window = obj.GetRenderWindow()
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(window)
    w2if.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName('screenshot.png')
    writer.SetInput(w2if.GetOutput())
    writer.Write()


def set_off_screen_rendering(window):
    'Turn on off-screen rendering, if available'
    gfx_factory = vtk.vtkGraphicsFactory()
    gfx_factory.SetOffScreenOnlyMode(1)
    gfx_factory.SetUseMesaClasses(1)

    img_factory = vtk.vtkImagingFactory()
    img_factory.SetUseMesaClasses(1)

    window.SetOffScreenRendering(1)


if __name__ == '__main__':
    main()

# vim:et:sw=4
