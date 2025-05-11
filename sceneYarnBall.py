#!/usr/bin/env rmanpy
import prman

# import the python functions
import sys
import sys, os.path, subprocess
import argparse
import math
import random
import time


# Main rendering routine
def main(
    filename,
    shadingrate=10,
    pixelvar=0.1,
    fov=48.0,
    width=1024,
    height=720,
    integrator="PxrPathTracer",
    integratorParams={},
):
    print("shading rate {} pivel variance {} using {} {}".format(shadingrate, pixelvar, integrator, integratorParams))
    ri = prman.Ri()  # create an instance of the RenderMan interface

    # this is the begining of the rib archive generation we can only
    # make RI calls after this function else we get a core dump
    ri.Begin(filename)
    ri.Option("searchpath", {"string archive": "./assets/:@"}) # add searchpaths 
    ri.Option("searchpath", {"string texture": "./textures/:@"})

    # now we add the display element using the usual elements
    # FILENAME DISPLAY Type Output format
    ri.Display("scene.exr", "it", "rgba")
    ri.Format(width, height, 1)

    # setup the raytrace / integrators
    ri.Hider("raytrace", {"int incremental": [1]})
    ri.ShadingRate(shadingrate)
    ri.PixelVariance(pixelvar)
    ri.Integrator(integrator, "integrator", integratorParams)
    ri.Option("statistics", {"filename": ["stats.txt"]})
    ri.Option("statistics", {"endofframe": [1]})


    # CAMERA
    # ri.Projection(ri.PERSPECTIVE, {ri.FOV: fov})
    # ri.Rotate(12, 1, 0, 0)
    # ri.Translate(0, 0.75, 2.5)

    # Set up Perspective Projection with Depth of Field
    ri.Projection(ri.PERSPECTIVE, {
        ri.FOV: fov,                # Field of view (already part of your setup)
        "float fstop": [2.0],       # Smaller fstop = more blur (shallow depth of field)
        "float focalLength": [50.0],  # Focal length in mm, e.g., 50mm lens
        "float focusDistance": [2.5]  # Distance from camera to focus point (scene units)
    })

    # Adjust the camera's orientation and position
    ri.Rotate(-5, 1, 0, 0)          # Camera rotation; value, x, y, z; -5
    #ri.Rotate(225, 0, 1, 0)         # Camera rotation; value, x, y, z
    #ri.Rotate(12, 0, 0, 1)          # Camera rotation; value, x, y, z
    ri.Translate(0, .50, 2)      # Camera position (focusDistance should match if you want to focus here)


    # LIGHTS
    # now we start our world
    ri.WorldBegin()
    #######################################################################
    # Lighting We need geo to emit light
    #######################################################################
    # ri.TransformBegin()
    # ri.AttributeBegin()
    # ri.Declare("domeLight", "string")
    # ri.Declare("visibility:camera", "uniform int")  # <--- Declare this line

    # ri.Rotate(-90, 1, 0, 0)
    # #ri.Rotate(100, 0, 0, 1)

    # #ri.Attribute("visibility", {"int camera": [0]})

    # # ri.Light("PxrDomeLight", "domeLight", {"string lightColorMap": "Luxo-Jr_4000x2000.tex"})
    # # ri.Light("PxrDomeLight", "domeLight", {"string lightColorMap": "brown_photostudio_02_1k.tex"}) 
    # ri.Light("PxrDomeLight", "domeLight", {"string lightColorMap": "photo_studio_loft_hall_1k.tex", "float intensity": [0.8], "float exposure": [-1.0], "int visibility:camera": [1]}) 
    # # brown_photostudio_02_1k.tex
    # ri.AttributeEnd()
    # ri.TransformEnd()

    ri.TransformBegin()
    ri.AttributeBegin()

    ri.Declare("domeLight", "string")
    ri.Declare("lightColorMap", "uniform string")  # good practice

    ri.Rotate(225, 0, 1, 0)         # Camera rotation; value, x, y, z
    ri.Rotate(-85, 1, 0, 0)
    ri.Rotate(10, 0, 0, 1)          # Camera rotation; value, x, y, z


    # This is where you make the dome light visible to the camera:
    ri.Attribute("visibility", {"camera": [1]})  

    ri.Light("PxrDomeLight", "domeLight", {
        "string lightColorMap": "photo_studio_loft_hall_1k.tex",
        "float intensity": [0.8],
        "float exposure": [-1.0]
    })

    ri.AttributeEnd()
    ri.TransformEnd()



    # # simple disk light example:
    # ri.TransformBegin()
    # ri.AttributeBegin()
    # ri.Declare("Light0", "string")
    # ri.Translate(0, 0.8, 0)
    # ri.Rotate(90, 1, 0, 0)
    # ri.Scale(0.5, 0.5, 0.5)
    # ri.Light("PxrDiskLight", "Light0", {"float intensity": 30})
    # ri.AttributeEnd()
    # ri.TransformEnd()
    #######################################################################
    # end lighting
    #######################################################################


    # # FLOOR
    # ri.AttributeBegin()
    # ri.Attribute("identifier", {"name": "floor"})
    # # ri.ReadArchive('cornell.rib')
    # ri.Bxdf("PxrDiffuse", "smooth", {"color diffuseColor": [0.8, 0.8, 0.8]})
    # ri.Polygon({ri.P: [-1, -1, 1, 1, -1, 1, 1, -1, -2, -1, -1, -2]})
    # ri.AttributeEnd()
    
    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "floor"})

    # Load texture
    ri.Pattern("PxrTexture", "floorTexture", {
        "string filename": "wood_table_001_diff_1k.tex"  # Or the full path if needed
    })

    ri.Pattern("PxrTexture", "floorRoughness", {
        "string filename": "wood_table_001_rough_1k.tex"
    })

    # Use texture as diffuse color
    ri.Bxdf("PxrSurface", "smooth", {
        "reference color diffuseColor": ["floorTexture:resultRGB"],
        "reference float specularRoughness": ["floorRoughness:resultR"]
    })

    # Apply geometry with UV coordinates
    ri.Polygon({
        "P": [-1, -1, 1,
            1, -1, 1,
            1, -1, -2,
            -1, -1, -2],
        "st": [0, 0,
            1, 0,
            1, 1,
            0, 1]
        #ri.UV: [0, 0, 1, 0, 1, 1, 0, 1]  # Define UV coordinates for proper mapping
    })

    ri.AttributeEnd()

    

    # YARN BALL
    ri.TransformBegin()
    ri.Translate(0.3, -.85, -0.8)
    # ri.AttributeBegin()
    # ri.Bxdf("PxrDiffuse", "core_shader", {
    #     "color diffuseColor": [0.1, 0.5, 0.7]  # Darker green
    # })
    # ri.Sphere(.2, -.2, .2, 360.0)  # Sphere at the center
    # ri.AttributeEnd()

    # Torus loops
    num_tori = 1

    for i in range(num_tori):
        rx = math.sin(i * 1.1) * 180
        ry = math.cos(i * 0.7) * 180
        rz = math.sin(i * 0.3) * 180

        tx = math.sin(i * 0.9) * 0.05
        ty = math.cos(i * 0.6) * 0.05
        tz = math.sin(i * 0.4) * 0.05

        ri.TransformBegin()

        ri.Translate(tx, ty, tz)
        ri.Rotate(rx, 1, 0, 0)
        ri.Rotate(ry, 0, 1, 0)
        ri.Rotate(rz, 0, 0, 1)

        ri.AttributeBegin()
        ri.Bxdf("PxrDiffuse", f"yarn_shader_{i}", {
            "color diffuseColor": [0.2, 0.8, 0.2]  # Lighter green yarn
        })

        ri.Torus(.25, 0.0095, 0.0, 360.0, 360.0)
        ri.AttributeEnd()

        #drawHairCurvesOnTorus(ri, torus_radius=0.25, num_curves=10, seed_offset=i)

        ri.TransformEnd()

    ri.TransformEnd()


    # end our world
    ri.WorldEnd()
    # and finally end the rib file
    ri.End()






def drawHairCurvesOnTorus(ri, torus_radius=0.25, num_curves=10, seed_offset=0):
    points = []  # This will hold all the points for all curves
    width = []   # This will hold the width of each curve point
    npoints = [] # This will hold the number of points per curve

    random.seed(seed_offset)
    ru = random.uniform

    # Loop to generate multiple hair-like curves
    for i in range(num_curves):
        # Create random offsets for each curve's starting point
        angle = ru(0, 2 * math.pi)  # Random angle on the torus
        offset_x = torus_radius * math.cos(angle) + ru(-0.02, 0.02)  # Slight randomness to X
        offset_z = torus_radius * math.sin(angle) + ru(-0.02, 0.02)  # Slight randomness to Z
        offset_y = ru(0.05, 0.1)  # Random height for the curve above the torus

        # Generate a cubic curve with at least 4 points
        # Each curve will have 4 control points (x, y, z)
        points.extend([offset_x, offset_y, offset_z])  # 1st point
        points.extend([offset_x + ru(-0.01, 0.01), offset_y + ru(-0.02, 0.02), offset_z + ru(-0.01, 0.01)])  # 2nd point
        points.extend([offset_x + ru(-0.01, 0.01), offset_y + ru(-0.02, 0.02), offset_z + ru(-0.01, 0.01)])  # 3rd point
        points.extend([offset_x + ru(-0.01, 0.01), offset_y + ru(0.02, 0.05), offset_z + ru(-0.01, 0.01)])  # 4th point

        # Set widths for the hair strands (optional)
        # Each curve has 4 widths corresponding to its 4 points
        width.extend([0.003, 0.002, 0.002, 0.003])  # Varying width values for each point
        npoints.append(4)  # 4 points per cubic curve

    # Now use the ri.Curves function to draw the curves with width as varying float
    # We'll directly pass the varying width parameter for the curves
    ri.AttributeBegin()  # Start a new attribute block to apply specific settings
    ri.Attribute("varying float width", width)  # Pass the varying width parameter
    ri.Curves("cubic", npoints, "nonperiodic", {
        ri.P: points  # The list of all points for all curves
    })
    ri.AttributeEnd()  # End the attribute block




def checkAndCompileShader(shader):
    if (
        os.path.isfile(shader + ".oso") != True
        or os.stat(shader + ".osl").st_mtime - os.stat(shader + ".oso").st_mtime > 0
    ):
        print("compiling shader %s" % (shader))
        try:
            subprocess.check_call(["oslc", shader + ".osl"])
        except subprocess.CalledProcessError:
            sys.exit("shader compilation failed")


if __name__ == "__main__":
    # shaderName = "starBall"
    # checkAndCompileShader(shaderName)

    parser = argparse.ArgumentParser(description="Modify render parameters")

    parser.add_argument(
        "--shadingrate",
        "-s",
        nargs="?",
        const=10.0,
        default=10.0,
        type=float,
        help="modify the shading rate default to 10",
    )

    parser.add_argument(
        "--pixelvar", "-p", nargs="?", const=0.1, default=0.1, type=float, help="modify the pixel variance default  0.1"
    )
    parser.add_argument(
        "--fov", "-f", nargs="?", const=48.0, default=48.0, type=float, help="projection fov default 48.0"
    )
    parser.add_argument(
        "--width", "-wd", nargs="?", const=1024, default=1024, type=int, help="width of image default 1024"
    )
    parser.add_argument(
        "--height", "-ht", nargs="?", const=720, default=720, type=int, help="height of image default 720"
    )

    parser.add_argument("--rib", "-r", action="count", help="render to rib not framebuffer")
    parser.add_argument("--default", "-d", action="count", help="use PxrDefault")
    parser.add_argument("--vcm", "-v", action="count", help="use PxrVCM")
    parser.add_argument("--direct", "-t", action="count", help="use PxrDirect")
    parser.add_argument("--wire", "-w", action="count", help="use PxrVisualizer with wireframe shaded")
    parser.add_argument("--normals", "-n", action="count", help="use PxrVisualizer with wireframe and Normals")
    parser.add_argument("--st", "-u", action="count", help="use PxrVisualizer with wireframe and ST")

    args = parser.parse_args()


    shadingrate = args.shadingrate if args.shadingrate is not None else 10.0
    pixelvar = args.pixelvar if args.pixelvar is not None else 0.1
    fov = args.fov if args.fov is not None else 48.0
    width = args.width if args.width is not None else 1024
    height = args.height if args.height is not None else 720



    if args.rib:
        filename = "domelight2.rib"
    else:
        filename = "__render"

    integratorParams = {}
    integrator = "PxrPathTracer"
    if args.default:
        integrator = "PxrDefault"
    if args.vcm:
        integrator = "PxrVCM"
    if args.direct:
        integrator = "PxrDirectLighting"
    if args.wire:
        integrator = "PxrVisualizer"
        integratorParams = {"int wireframe": [1], "string style": ["shaded"]}
    if args.normals:
        integrator = "PxrVisualizer"
        integratorParams = {"int wireframe": [1], "string style": ["normals"]}
    if args.st:
        integrator = "PxrVisualizer"
        integratorParams = {"int wireframe": [1], "string style": ["st"]}

    main(filename, args.shadingrate, args.pixelvar, args.fov, args.width, args.height, integrator, integratorParams)
