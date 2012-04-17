#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Program to visualize dust bunnies.
# Jonas Juselius <jonas.juselius@uit.no> 04/2012
#

import vtk
from argparse import ArgumentParser

def parse_commandline():
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
    parser.add_argument('--angle', '-a',
            action='store',
            type=float,
            default=90.0,
            help='camera transformation angle [default: %(default)s]')
    parser.add_argument('--camera', '-C',
            action='store',
            type=str,
            default=None,
            help='camera azimuth, elevation, roll (e.g. aer)')
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
    parser.add_argument('--box', '-b',
            action='store_true',
            default=False,
            help='Draw the bounding box around each object')
    parser.add_argument('--offscreen', '-x',
            action='store_true',
            default=False,
            help='Use offscreen rendering if available')
    parser.add_argument('--multiview', '-m',
            action='store_true',
            default=False,
            help='Render each file in a separate viewport')

    return parser.parse_args()

def main():
    args = parse_commandline()
    renderers = []
    rotor = 0
    if not args.multiview:
        if len(args.infile) > 2:
            raise RuntimeError(
                    'Combi-view not supported for more than 2 files')
        if len(args.infile) > 1:
            args.rotations = True
        viewports = get_viewports(1)
        renderers.append(create_renderer(viewports[0], 
            color_scheme=args.color_scheme))
        for i in args.infile:
            (actor, source) = create_actor(i, color_scheme=args.color_scheme, 
                    fiber=args.fiber)
            renderers[0].AddActor(actor)
            if args.box:
                bbox = create_box(source)
                renderers[0].AddActor(bbox)
        renderers[0].ResetCamera()
        camera = renderers[0].GetActiveCamera()
        transform_camera(camera, args.camera, args.angle)
    else:
        viewports = get_viewports(len(args.infile))
        for i, v in zip(args.infile, viewports):
            (actor, source) = create_actor(i, color_scheme=args.color_scheme, 
                    fiber=args.fiber)
            transform_multiview(actor, rotor)
            if args.rotations:
                rotor += 1
            renderers.append(create_renderer(v, actor,
                color_scheme=args.color_scheme))
            if args.box:
                bbox = create_box(source)
                transform_multiview(bbox, rotor)
                renderers[-1].AddActor(bbox)

    camera = renderers[0].GetActiveCamera()
    for i in renderers[1:]:
        i.SetActiveCamera(camera)
    window = create_scene(renderers, args.size)
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


def create_actor(fname=None, color_scheme=None, fiber=False):
    if fname:
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(fname)
        reader.Update()
        prop = reader
    else:
        prop = vtk.vtkCubeSource()  # for testing

    if fiber:
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

# Set actor properties
    props = actor.GetProperty()
    props.SetAmbientColor(0.6, 0.6, 0.6)
    if color_scheme == 'wb' and not fiber:
        props.SetDiffuseColor(0.1, 0.1, 0.1)
    else:
        props.SetDiffuseColor(0.9, 0.9, 0.9)
#    props.SetOpacity(0.3)
#    props.SetLineWidth(1)
#    props.SetRepresentationToSurface()
#    props.SetRepresentationToWireframe()
    return (actor, reader)

def create_box(source):
    outline = vtk.vtkOutlineFilter()
    outline.SetInputConnection(source.GetOutputPort())
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(outline.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
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

def transform_camera(camera, transform=None, angle=90.0):
    if not transform:
        return
    if not isinstance(transform, str):
        raise TypeError('Transform must be a string. This is a bug.')

    transform = transform.lower()
    for i in transform:
        if i == 'e':
            camera.Elevation(angle)
        elif i == 'r':
            camera.Roll(angle)
        elif i == 'a':
            camera.Azimuth(angle)
        else:
            raise RuntimeError('Invalid transformation spec. This is a bug')

def create_renderer(viewport=None, actor=None, color_scheme=None):
# Create the Renderer
    renderer = vtk.vtkRenderer()
    if color_scheme == 'bw':
        renderer.SetBackground(0.0, 0.0, 0.0)
    elif color_scheme == 'wb':
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


def create_scene(renderers, size=500):
    n = len(renderers)
    if n < 4:
        sx = size * n
        sy = size
    elif n == 4:
        sx = sy = size * 2
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
