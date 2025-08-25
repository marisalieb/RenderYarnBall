#!/usr/bin/env rmanpy
import prman

import sys
import os.path, subprocess
import argparse
import math
import random
import time
import numpy as np


def sample_torus(major_radius=1.0, minor_radius=0.3, count=500):
    pts, norms = [], []
    for _ in range(count):
        u = random.uniform(0, 2 * math.pi) # Angle around the major radius, as a full circle in radians is 2pi
        v = random.uniform(0, 2 * math.pi) # Angle around the minor radius

		# parametric equation for torus
        x = (major_radius + minor_radius * math.cos(v)) * math.cos(u)
        y = (major_radius + minor_radius * math.cos(v)) * math.sin(u)
        z = minor_radius * math.sin(v)

        # outward pointing surface normals at the sampled point
        nx = math.cos(u) * math.cos(v)
        ny = math.sin(u) * math.cos(v)
        nz = math.sin(v)

        pts.append((x, y, z))
        norms.append((nx, ny, nz))
	
	# return 3d coords on the torus and their normals
    return pts, norms


def generate_hair(pts, widths, npts,
                 count=900, major_radius=1.0,
                 minor_radius=0.3, hair_length=0.02,
                 hair_width=0.001):

    # get hair root positions and normals from the torus
    surface_pts, surface_norms = sample_torus(
        major_radius, minor_radius, count)

    # loop over each hair root
    for (x, y, z), (nx, ny, nz) in zip(surface_pts, surface_norms):
        jitter = 0.6  # used for curliness

        # More control points for smoother and tighter curls
        num_control_points = 10

        # vary the length of the hairs
        variation = random.uniform(0.5, 2.5)
        strand_length = hair_length * variation

        for i in range(num_control_points):

            t = i / (num_control_points - 1) # range of the points in the hair strand, 0/9, 1/9 etc, so from 0 to 1 in total

            # Combine with jitter and original direction for natural randomness
            nx += random.uniform(-jitter, jitter)
            ny += random.uniform(-jitter, jitter) 
            nz += random.uniform(-jitter, jitter)

            length = math.sqrt(nx * nx + ny * ny + nz * nz)
            nx /= length
            ny /= length
            nz /= length

			# move each point in the strand along the surface normal, incrementally
            px = x + nx * strand_length * t 
            py = y + ny * strand_length * t
            pz = z + nz * strand_length * t
            pts.extend([px, py, pz]) 

        npts.append(num_control_points)
        widths.append(hair_width)


# Main rendering routine
def main(
    filename,
    shadingrate=1,
    pixelvar=0.01,
    fov=48.0,
    width=1920,
    height=1080,
    integrator="PxrPathTracer",
    integratorParams={},
):
    print("shading rate {} pivel variance {} using {} {}".format(shadingrate, pixelvar, integrator, integratorParams))
    ri = prman.Ri()  # create an instance of the RenderMan interface


    ri.Begin(filename)
    ri.Option("searchpath", {"string texture": "./textures/:@"})

    ri.Display("scene.exr", "it", "rgba")
    ri.Format(width, height, 1)

    ri.ShadingRate(shadingrate)
    ri.PixelVariance(pixelvar)
    
    # enable for higher quality
    # ri.Hider("raytrace", {
    # "int incremental": [1],
    # "int maxsamples": [1024]
    #     })

    # ri.PixelFilter("gaussian", 2, 2) 

    ri.Integrator(integrator, "integrator", integratorParams)
    ri.Option("statistics", {"filename": ["stats.txt"]})
    ri.Option("statistics", {"endofframe": [1]})

    ri.Projection(ri.PERSPECTIVE, {ri.FOV: fov})

    # # IMAGE ONE
    ri.Rotate(-5, 1, 0, 0) 
    ri.Translate(0.07065, .945328750, 1.075)
    ri.DepthOfField(32, .0250, .1125925) 
    

    ri.WorldBegin()



    # LIGHTS
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Declare("domeLight", "string")
    ri.Declare("lightColorMap", "uniform string")

    ri.Rotate(230, 0, 1, 0)  
    ri.Rotate(-90, 1, 0, 0)
    ri.Rotate(10, 0, 0, 1) 

    # This is where to make the dome light visible to the camera:
    ri.Attribute("visibility", {"camera": [1]})  

    ri.Light("PxrDomeLight", "domeLight", {
        "string lightColorMap": "brown_photostudio_02_1k.tex",
        "float intensity": [.5],
        "float exposure": [.35]
    })

    ri.AttributeEnd()
    ri.TransformEnd()


    # additional key light in place of the window
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.TransformBegin()
    ri.Translate(2, 0, 0)
    ri.Translate(0, 0, -2)
    ri.Rotate(15, 1, 0, 0) 

    ri.Rotate(180, 0, 0, 1)
    ri.Light("PxrRectLight", "keyLight", {
        "float intensity": [5.0],
        "float exposure": [2.0],

    })
    ri.TransformEnd()

    ri.AttributeEnd()
    ri.TransformEnd()



    # FLOOR
    ri.TransformBegin()
    ri.Translate(0, .0, 0)
    ri.Translate(0, 0, -.5)
    ri.Rotate(90, 0, 1, 0)
    ri.Scale(1, 1, 1.5)
    ri.Translate(1.2975, 0, 0)

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "floor"})


    # Load roughness map
    ri.Pattern("PxrTexture", "floorRoughness", {
        "string filename": "wood_table_001_rough_1k.tex",
    })

    # Load texture
    ri.Pattern("PxrTexture", "floorTexture", {
        "string filename": "wood_table_001_diff_1k.tex"
    })


    # Use texture as diffuse color
    ri.Bxdf("PxrSurface", "smooth", {
        "reference color diffuseColor": ["floorTexture:resultRGB"],
        "color specularFaceColor": [0.3, 0.3, 0.3],
        "reference float specularRoughness": ["floorRoughness:resultR"]
    })

    scale = 1  # scale factor for x and z, used for testing

    P = [
        -1 * scale, -1, 1 * scale,
        1 * scale, -1, 1 * scale,
        1 * scale, -1, -2 * scale,
        -1 * scale, -1, -2 * scale
    ]

    ri.Polygon({
        "P": P,
        "st": [0, 0,
            1, 0,
            1, 1,
            0, 1]
    })

    ri.AttributeEnd()
    ri.TransformEnd()

    



    # YARN BALL 
    ri.TransformBegin()
    ri.Scale(0.7, 0.7, 0.7)
    ri.Translate(-0.13, -.87, -1.318)

    random.seed(3)  # makes randomness repeatable across runs

    ri.Translate(0, -.4925, 0)

    num_tori3 = 200 # number of tori in the base layer of the yarn ball
    rmaj_values = np.linspace(.8, 1.1, num_tori3)

    for i in range(num_tori3):
        rx = math.sin(i * 1.618) * 180 + random.uniform(-10, 10)
        ry = math.cos(i * 2.718) * 180 + random.uniform(-10, 10)
        rz = math.sin(i * 3.1415) * 180 + random.uniform(-10, 10)

        tx = math.sin(i * 0.06) * 0.0001 + random.uniform(-0.00005, 0.00005)
        ty = math.cos(i * 0.06) * 0.0001 + random.uniform(-0.00005, 0.00005)
        tz = math.sin(i * 0.06) * 0.0001 + random.uniform(-0.00005, 0.00005)


        ri.TransformBegin()
        ri.Translate(tx, ty, tz)
        ri.Rotate(rx, 1, 0, 0)
        ri.Rotate(ry, 0, 1, 0)
        ri.Rotate(rz, 0, 0, 1)

        ri.AttributeBegin()
        ri.TransformBegin()

        ri.Attribute("displacementbound", {"float sphere": [0.02]}) # .2
        ri.Attribute("dice", {
            "float micropolygonlength": [0.1]
        })

        ri.Pattern(
            "disp", "disp",
            {
                "float scale1": [.006543],  # Larger displacement for the first spiral
                "float repeatU1": [170],  # Repeat factor for the first spiral, 230
                "float repeatV1": [8],  # Repeat factor for the first spiral, 10

                "float scale2": [0.000625],  # 0.04
                "float repeatU2": [150],  # 
                "float repeatV2": [-37],  # -7 

                "float noiseAmount1": [0.0015],   # Larger bumps noise strength
                "float noiseFreq1": [.750],     # Larger bumps frequency

                "float noiseAmount2": [0.0032],   # 0.02, can make it bigger maybe slightly
                "float noiseFreq2": [14.0]  ,    # between 4 and 5 

                "float noiseAmount3": [0.0005],   # maybe 0.005 or 0.002 but maybe more just slight stripes not bumps
                "float noiseFreq3": [100.0]      # the smallest bumps on it
            }
        )

        ri.Displace(
            "PxrDisplace", "pxrdisp",
            {"reference float dispScalar": ["disp:resultF"]}
        )


        # colour spiral pattern to simulate strands of fibres
        ri.Pattern(
            "spiralColourNoise", "spiralColourNoise",
            {
                "float repeatU": [70], 
                "float repeatV": [-30.0],  
                "color colorA": [0.75, 0.06, 0.047],
                "color colorB": [1, 0.075, 0.05],
                "float noiseFreq1": [1500.750],
            }
        )

        ri.Pattern(
            "spiralSpecNoise", "spiralSpecNoise",
            {
                "float repeatU": [70],
                "float repeatV": [-10.0],
                "float noiseFreq1": [2000.750],
                "float maskScale": [2.5],
                "color colorA": [1, 1, 1],
                "color colorB": [0.007, .007, .007],
            }
        )


        ri.Bxdf("PxrSurface", "yarnShader",
        {
            "float diffuseGain" : [.50],
            "reference color diffuseColor": ["spiralColourNoise:resultRGB"],
            "float diffuseRoughness" : [0.6],

            "float fuzzGain" : [1.0],
            "color fuzzColor" : [1.0, 0.05, 0.05],

            # Subsurface scattering for fluffiness
            "int subsurfaceType"        : [1],     
            "float subsurfaceGain"      : [0.05], 
            "color subsurfaceColor"     : [1.0, 0.075, 0.02], 
            "float subsurfaceDmfp"      : [1.0], 

            # Match highlight color to base — subtle red sheen
            "color specularFaceColor" : [0.2, 0.05, 0.02],
            "color specularEdgeColor" : [0.25, 0.06, 0.025],
            "reference float specularRoughness": ["spiralSpecNoise:resultMask"],
            "int specularFresnelMode" : [0],   
        })

        # DISPLACED TORUS 
        Rmaj3 = random.uniform(.998, 1.2)
        ri.Scale(0.125, 0.125, 0.125)
        ri.Scale(.40510, .40510, .40510)
        ri.Torus(Rmaj3, 0.034181251, 0, 360, 360) 
        ri.TransformEnd()
        ri.AttributeEnd()


        # YARN HAIR
        ri.TransformBegin()

        hair_scale = .125 # derived from the torus scale, 0.125 is the scale of the yarn ball

        # Match the effective torus radii
        effective_major = Rmaj3 * 0.40510 *.125
        effective_minor = 0.034181251 * 0.40510 * .125
        hairlength = 0.0075 *hair_scale *1.25
        hairwidth = 0.000215 * hair_scale 


        hair_pts, hair_widths, hair_npts = [], [], []

        generate_hair(hair_pts, hair_widths, hair_npts, count=3000, major_radius=effective_major, minor_radius=effective_minor, hair_length=hairlength, hair_width=hairwidth)

        ri.AttributeBegin()

        ri.Bxdf('PxrMarschnerHair', 'yarnHairShader', {
            'float diffuseGain': [0.2],                     
            'color diffuseColor': [1.0, 0.075, 0.02],  

            'color specularColorR': [1.0, 1, 1],  
            'color specularColorTRT': [1.0, 0.075, 0.02],      
            'color specularColorTT': [1.0, 0.075, 0.02],

            'float specularGainR': [1],     
            'float specularGainTRT': [0.7],   
            'float specularGainTT': [0.6],    
        })


        # based on the lecture example on hair, these parameters are the minimum needed in the rib
        ri.Curves("cubic", hair_npts, "nonperiodic", {
            ri.P: hair_pts,
            "float width": hair_widths
        })

        ri.AttributeEnd()
        ri.TransformEnd()
        ri.TransformEnd()


    random.seed(18) 

    num_tori2 = 15 # number of tori in the top layer of the yarn ball
    rmaj_values = np.linspace(1.1, 1.3, num_tori2)

    for i in range(num_tori2):
        rx = math.sin(i * 1.618) * 180 + random.uniform(-10, 10)
        ry = math.cos(i * 2.718) * 180 + random.uniform(-10, 10)
        rz = math.cos(i * 3.1415) * 180 + random.uniform(-10, 10)

        tx = math.sin(i * 0.06) * 0.0001 + random.uniform(-0.00005, 0.00005)
        ty = math.cos(i * 0.06) * 0.0001 + random.uniform(-0.00005, 0.00005)
        tz = math.sin(i * 0.06) * 0.0001 + random.uniform(-0.00005, 0.00005)

        ri.TransformBegin()

        ri.Translate(tx, ty, tz)
        ri.Rotate(rx, 1, 0, 0)
        ri.Rotate(ry, 0, 1, 0)
        ri.Rotate(rz, 0, 0, 1)

        ri.AttributeBegin()


        ri.Attribute("displacementbound", {"float sphere": [0.02]}) # .2
        ri.Attribute("dice", {
            "float micropolygonlength": [0.1]
        })

        ri.Pattern(
            "disp", "disp",
            {
                "float scale1": [.006543],
                "float repeatU1": [170],
                "float repeatV1": [8],

                "float scale2": [0.000625],
                "float repeatU2": [150],
                "float repeatV2": [-37],

                "float noiseAmount1": [0.0015],
                "float noiseFreq1": [.750],

                "float noiseAmount2": [0.0032],
                "float noiseFreq2": [14.0]  , 

                "float noiseAmount3": [0.0005],
                "float noiseFreq3": [100.0]
            }
        )

        ri.Displace(
            "PxrDisplace", "pxrdisp",
            {"reference float dispScalar": ["disp:resultF"]}
        )


        # colour spiral pattern to simulate strands of fibres
        ri.Pattern(
            "spiralColourNoise", "spiralColourNoise",
            {
                "float repeatU": [70], 
                "float repeatV": [-30.0], 
                "color colorA": [0.75, 0.06, 0.047],
                "color colorB": [1, 0.075, 0.05],
                "float noiseFreq1": [1500.750],
            }
        )

        ri.Pattern(
            "spiralSpecNoise", "spiralSpecNoise",
            {
                "float repeatU": [70], 
                "float repeatV": [-10.0],
                "float noiseFreq1": [2000.750],
                "float maskScale": [2.5],
                "color colorA": [1, 1, 1],
                "color colorB": [0.007, .007, .007],
            }
        )


        ri.Bxdf("PxrSurface", "yarnShader",
        {
            "float diffuseGain" : [.50],
            "reference color diffuseColor": ["spiralColourNoise:resultRGB"],
            "float diffuseRoughness" : [0.6],

            "float fuzzGain" : [1.0],  # Increase fuzz for soft, warm look
            "color fuzzColor" : [1.0, 0.05, 0.05],

            # Subsurface scattering for fluffiness
            "int subsurfaceType"        : [1],   
            "float subsurfaceGain"      : [0.05],    
            "color subsurfaceColor"     : [1.0, 0.075, 0.02],
            "float subsurfaceDmfp"      : [1.0], 

            "color specularFaceColor" : [0.2, 0.05, 0.02],
            "color specularEdgeColor" : [0.25, 0.06, 0.025], 
            "reference float specularRoughness": ["spiralSpecNoise:resultMask"],
            "int specularFresnelMode" : [0],   
        })

        # DISPLACED TORUS
        Rmaj2 = random.uniform(1.2, 1.3)
        ri.Scale(0.125, 0.125, 0.125)
        ri.Scale(.40510, .40510, .40510)
        ri.Torus(Rmaj2, 0.034181251, 0, 360, 360)

        ri.AttributeEnd()






        # YARN HAIR
        ri.TransformBegin()

        hair_scale = .125
        # Match the effective torus radii
        effective_major = Rmaj2 * 0.40510 *.125
        effective_minor = 0.034181251 * 0.40510 * .125
        hairlength = 0.0075 *hair_scale *1.25
        hairwidth = 0.000215 * hair_scale 

        hair_pts, hair_widths, hair_npts = [], [], []

        generate_hair(hair_pts, hair_widths, hair_npts, count=6000, major_radius=effective_major, minor_radius=effective_minor, hair_length=hairlength, hair_width=hairwidth)

        ri.AttributeBegin()

        ri.Bxdf('PxrMarschnerHair', 'yarnHairShader', {
            'float diffuseGain': [0.2],                     
            'color diffuseColor': [1.0, 0.075, 0.02],  

            'color specularColorR': [1.0, 1, 1],  
            'color specularColorTRT': [1.0, 0.075, 0.02],      
            'color specularColorTT': [1.0, 0.075, 0.02],

            'float specularGainR': [1],    
            'float specularGainTRT': [0.7],  
            'float specularGainTT': [0.6],      
        })

        ri.Curves("cubic", hair_npts, "nonperiodic", {
            ri.P: hair_pts,
            "float width": hair_widths
        })

        ri.AttributeEnd()
        ri.TransformEnd()
        ri.TransformEnd()



    # single yarn strand off to the side
    ri.TransformBegin()
    ri.TransformBegin()
    ri.AttributeBegin()
    ri.Attribute("displacementbound", {"float sphere": [0.02]})
    ri.Attribute("dice", {
        "float micropolygonlength": [0.1]
    })


    ri.Pattern(
        "disp", "disp",
        {
            "float scale1": [.006543], 
            "float repeatU1": [170], 
            "float repeatV1": [8], 

            "float scale2": [0.000625], 
            "float repeatU2": [150], 
            "float repeatV2": [-37], 

            "float noiseAmount1": [0.0015], 
            "float noiseFreq1": [.750],  

            "float noiseAmount2": [0.0032], 
            "float noiseFreq2": [14.0],  

            "float noiseAmount3": [0.0005], 
            "float noiseFreq3": [100.0] 
        }
    )

    ri.Displace(
        "PxrDisplace", "pxrdisp",
        {"reference float dispScalar": ["disp:resultF"]}
    )

    ri.Pattern(
        "spiralColourNoise", "spiralColourNoise",
        {
            "float repeatU": [70], 
            "float repeatV": [-30.0], 
            "color colorA": [0.75, 0.06, 0.047],
            "color colorB": [1, 0.075, 0.05],
            "float noiseFreq1": [1500.750],
        }
    )

    ri.Pattern(
        "spiralSpecNoise", "spiralSpecNoise",
        {
            "float repeatU": [70],  
            "float repeatV": [-10.0], 
            "float noiseFreq1": [2000.750],
            "float maskScale": [2.5],
            "color colorA": [1, 1, 1],
            "color colorB": [0.007, .007, .007],
        }
    )


    ri.Bxdf("PxrSurface", "yarnShader",
    {
        "float diffuseGain" : [.50],
        "reference color diffuseColor": ["spiralColourNoise:resultRGB"],
        "float diffuseRoughness" : [0.6],

        "reference float specularRoughness": ["spiralSpecNoise:resultMask"],
        "float fuzzGain" : [1.0],
        "color fuzzColor" : [1.0, 0.05, 0.05],

        "int subsurfaceType"        : [1],     
        "float subsurfaceGain"      : [0.05],   
        "color subsurfaceColor"     : [1.0, 0.075, 0.02],
        "float subsurfaceDmfp"      : [1.0], 

        "color specularFaceColor" : [0.2, 0.05, 0.02],
        "color specularEdgeColor" : [0.25, 0.06, 0.025], 
        "int specularFresnelMode" : [0],   
    })

    ri.Rotate(90, 1, 0, 0)
    ri.Translate(-0.075, -0.0510, 0.05)
    ri.Rotate(10, 0, 1, 0)
    ri.Rotate(10, 0, 0, 1)

    ri.Scale(0.125, 0.125, 0.125)
    ri.Scale(.40510, .40510, .40510)
    ri.Torus(1.5, 0.04324181251, 0, 360, 200)

    ri.AttributeEnd()
    ri.TransformEnd() 

    ri.TransformEnd()

    ri.TransformEnd()

    # end  world
    ri.WorldEnd()

    # and finally end the rib file
    ri.End()


if __name__ == "__main__":

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
        "--pixelvar", "-p", nargs="?", const=0.01, default=0.1, type=float, help="modify the pixel variance default  0.1"
    )
    parser.add_argument(
        "--fov", "-f", nargs="?", const=48.0, default=48.0, type=float, help="projection fov default 48.0"
    )
    parser.add_argument(
        "--width", "-wd", nargs="?", const=1024, default=1920, type=int, help="width of image default 1024"
    )
    parser.add_argument(
        "--height", "-ht", nargs="?", const=720, default=1080, type=int, help="height of image default 720"
    )

    parser.add_argument("--rib", "-r", action="count", help="render to rib not framebuffer")
    parser.add_argument("--default", "-d", action="count", help="use PxrDefault")
    parser.add_argument("--vcm", "-v", action="count", help="use PxrVCM")
    parser.add_argument("--direct", "-t", action="count", help="use PxrDirect")
    parser.add_argument("--wire", "-w", action="count", help="use PxrVisualizer with wireframe shaded")
    parser.add_argument("--normals", "-n", action="count", help="use PxrVisualizer with wireframe and Normals")
    parser.add_argument("--st", "-u", action="count", help="use PxrVisualizer with wireframe and ST")

    args = parser.parse_args()

    shadingrate = args.shadingrate if args.shadingrate is not None else 1.0
    pixelvar = args.pixelvar if args.pixelvar is not None else 0.01
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
