#!/usr/bin/env rmanpy
import prman

# import the python functions
import sys
import sys, os.path, subprocess
import argparse
import math
import random
import time


import numpy as np
# from scipy.spatial import cKDTree

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

# def sample_sphere(radius=1.0, count=500):
#     pts, norms = [], []
#     for _ in range(count):
#         # Uniform sampling using spherical coordinates
#         theta = random.uniform(0, 2 * math.pi)     # Longitude
#         phi = math.acos(random.uniform(-1, 1))     # Latitude (uniform on sphere)

#         # Convert spherical to Cartesian coordinates
#         x = radius * math.sin(phi) * math.cos(theta)
#         y = radius * math.sin(phi) * math.sin(theta)
#         z = radius * math.cos(phi)

#         # For a sphere, normal is just the normalized position vector
#         nx, ny, nz = x / radius, y / radius, z / radius

#         pts.append((x, y, z))
#         norms.append((nx, ny, nz))

#     return pts, norms


def generate_hair(pts, widths, npts, count=900, major_radius=1.0, minor_radius=0.3, hair_length=0.02, hair_width=0.001):
    #surface_pts, surface_norms = sample_torus(1.0, 0.01118, count)
    surface_pts, surface_norms = sample_torus(major_radius, minor_radius, count)
    for (x, y, z), (nx, ny, nz) in zip(surface_pts, surface_norms):
        # --- CURLY VARIATION USING MULTI-AXIS SINUSOIDAL FUNCTIONS ---
        jitter = 1.5  # Randomness to introduce slight variation in curl direction
        curl_strength = random.uniform(1.5, 3.0)  # Control how tightly the hair curls
        
        # Increased curl factor for tighter curls
        curl_factor = random.uniform(15.0, 30.0)  # Higher frequency for tight, 4C curls
        angle_offset = random.uniform(0, math.pi)  # Offset for randomizing the start of curls

        # More control points for smoother and tighter curls
        num_control_points = 10  # Increased control points for smoother, tighter curls

        variation = random.uniform(0.5, 2.5)  # Vary hair length ±50%
        strand_length = hair_length * variation

        for i in range(num_control_points):  # Iterate through control points
            t = i / (num_control_points - 1)  # Parametric range for the hair strand
            
            # Create multi-axis curls, one along X, one along Y, one along Z
            curl_x = math.sin(curl_factor * t + angle_offset) * 0.6  # Larger curls in X
            curl_y = math.cos(curl_factor * t + angle_offset) * 0.6  # Larger curls in Y
            curl_z = math.sin(curl_factor * t + angle_offset) * 0.2  # Smaller curls in Z
            
            # Add a vertical offset for extra randomness (simulating coiled curls)
            vertical_curl = math.cos(curl_factor * t * 2) * 0.2  # Vertical curl, gives it a coiled effect
            curl_x += vertical_curl
            curl_y += vertical_curl

            # Combine with jitter and original direction for natural randomness
            nx += random.uniform(-jitter, jitter) + curl_x
            ny += random.uniform(-jitter, jitter) + curl_y
            nz += random.uniform(-jitter, jitter) + curl_z

            # Normalize the new direction vector
            length = math.sqrt(nx * nx + ny * ny + nz * nz)
            nx /= length
            ny /= length
            nz /= length

            # Generate control points along the curly direction (longer hair strands)
            px = x + nx * strand_length * t  # Increase to make hairs longer 0.012
            py = y + ny * strand_length * t
            pz = z + nz * strand_length * t
            pts.extend([px, py, pz])
        
        npts.append(num_control_points)  # Append the updated number of control points for each hair strand
        widths.append(hair_width)  # 0.001 beofre but maybe too thick; Width of the hair strand (adjust as needed for fuzziness)

# def generate_hairSphere(pts, widths, npts, count=900, radius = .5, hair_length=0.02, hair_width=0.001):
#     #surface_pts, surface_norms = sample_torus(1.0, 0.01118, count)
#     surface_pts_s, surface_norms_s = sample_sphere(radius, count)
#     for (x, y, z), (nx, ny, nz) in zip(surface_pts_s, surface_norms_s):
#         # --- CURLY VARIATION USING MULTI-AXIS SINUSOIDAL FUNCTIONS ---
#         jitter = 1.5  # Randomness to introduce slight variation in curl direction
#         curl_strength = random.uniform(1.5, 3.0)  # Control how tightly the hair curls
        
#         # Increased curl factor for tighter curls
#         curl_factor = random.uniform(15.0, 30.0)  # Higher frequency for tight, 4C curls
#         angle_offset = random.uniform(0, math.pi)  # Offset for randomizing the start of curls

#         # More control points for smoother and tighter curls
#         num_control_points = 10  # Increased control points for smoother, tighter curls
#         variation = random.uniform(0.5, 1.5)  # Vary hair length ±50%
#         strand_length = hair_length * variation
#         for i in range(num_control_points):  # Iterate through control points
#             t = i / (num_control_points - 1)  # Parametric range for the hair strand
            
#             # Create multi-axis curls, one along X, one along Y, one along Z
#             curl_x = math.sin(curl_factor * t + angle_offset) * 0.6  # Larger curls in X
#             curl_y = math.cos(curl_factor * t + angle_offset) * 0.6  # Larger curls in Y
#             curl_z = math.sin(curl_factor * t + angle_offset) * 0.2  # Smaller curls in Z
            
#             # Add a vertical offset for extra randomness (simulating coiled curls)
#             vertical_curl = math.cos(curl_factor * t * 2) * 0.2  # Vertical curl, gives it a coiled effect
#             curl_x += vertical_curl
#             curl_y += vertical_curl

#             # Combine with jitter and original direction for natural randomness
#             nx += random.uniform(-jitter, jitter) + curl_x
#             ny += random.uniform(-jitter, jitter) + curl_y
#             nz += random.uniform(-jitter, jitter) + curl_z

#             # Normalize the new direction vector
#             length = math.sqrt(nx * nx + ny * ny + nz * nz)
#             nx /= length
#             ny /= length
#             nz /= length

#             # Generate control points along the curly direction (longer hair strands)
#             px = x + nx * strand_length * t  # Increase to make hairs longer 0.012
#             py = y + ny * strand_length * t
#             pz = z + nz * strand_length * t
#             pts.extend([px, py, pz])
        
#         npts.append(num_control_points)  # Append the updated number of control points for each hair strand
#         widths.append(hair_width)  # 0.001 beofre but maybe too thick; Width of the hair strand (adjust as needed for fuzziness)





def wobbly_torus(ri, major_radius=13.251, minor_radius=0.34181251, u_steps=64, v_steps=32, wobble_freq=3, wobble_amp=0.5):
    points = []
    normals = []
    u_range = [2 * math.pi * i / u_steps for i in range(u_steps)]
    v_range = [2 * math.pi * j / v_steps for j in range(v_steps)]

    for u in u_range:
        # Wobble the major radius
        R_wobble = major_radius + math.sin(u * wobble_freq) * wobble_amp
        for v in v_range:
            x = (R_wobble + minor_radius * math.cos(v)) * math.cos(u)
            y = (R_wobble + minor_radius * math.cos(v)) * math.sin(u)
            z = minor_radius * math.sin(v)
            points.append([x, y, z])
            # Normal (optional): compute actual normals here if needed

    # flatten [[x,y,z], …] → [x,y,z, x,y,z, …]
    points_flat = [coord for p in points for coord in p]

    # RenderMan expects a mesh: turn point grid into a quad mesh
    nverts = []
    verts = []
    for i in range(u_steps):
        for j in range(v_steps):
            i0 = i * v_steps + j
            i1 = ((i + 1) % u_steps) * v_steps + j
            i2 = ((i + 1) % u_steps) * v_steps + (j + 1) % v_steps
            i3 = i * v_steps + (j + 1) % v_steps

            nverts.append(4)
            verts += [i0, i1, i2, i3]

    ri.PointsPolygons(
        nverts,          # list of 4s, one per quad
        verts,           # flattened list of vertex-indices
        { "P": points_flat }  # a single dict mapping the token "P" to your point array
    )




def wobbly_torus_uvs(ri,
                     major_radius=13.251, minor_radius=0.34181251,
                     u_steps=64, v_steps=32,
                     wobble_freq=3, wobble_amp=0.5):
    # --- 1) Build CLOSED grids of u and v (0…2π inclusive) ---
    us = [2*math.pi * i/u_steps for i in range(u_steps+1)]
    vs = [2*math.pi * j/v_steps for j in range(v_steps+1)]

    points = []
    st_flat = []

    for u in us:
        su = u/(2*math.pi)   # normalized s in [0,1]
        Rw = major_radius + math.sin(u*wobble_freq)*wobble_amp
        for v in vs:
            tv = v/(2*math.pi)  # normalized t

            # record UV
            st_flat.extend([su, tv])

            # record point
            x = (Rw + minor_radius * math.cos(v)) * math.cos(u)
            y = (Rw + minor_radius * math.cos(v)) * math.sin(u)
            z = minor_radius * math.sin(v)
            points.append((x,y,z))

    # flatten point list
    points_flat = [c for p in points for c in p]

    # --- 2) Build quad connectivity over the (u_steps+1)x(v_steps+1) grid ---
    nverts = []
    verts  = []
    # note: each row has (v_steps+1) points
    row_len = v_steps + 1
    for i in range(u_steps):
        for j in range(v_steps):
            i0 = i   * row_len + j
            i1 = (i+1)* row_len + j
            i2 = (i+1)* row_len + (j+1)
            i3 = i   * row_len + (j+1)
            nverts.append(4)
            verts.extend([i0, i1, i2, i3])

    # --- 3) Emit exactly like your working call, but now with UVs too ---
    ri.PointsPolygons(
        nverts,
        verts,
        {
          "P":  points_flat,
          "st": st_flat
        }
    )


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

    # this is the begining of the rib archive generation we can only
    # make RI calls after this function else we get a core dump
    ri.Begin(filename)
    #ri.Begin("pointlight.rib")
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
    
    # ri.Hider("raytrace", {
    # "int incremental": [1],
    # "int maxsamples": [512]
    #     })

    # # PixelFilter: "gaussian" 2 2
    # ri.PixelFilter("gaussian", 2, 2) 

    ri.Integrator(integrator, "integrator", integratorParams)
    ri.Option("statistics", {"filename": ["stats.txt"]})
    ri.Option("statistics", {"endofframe": [1]})

    #ri.DepthOfField(1.4, 0.05, 6.8)
    # CAMERA
    # ri.Projection(ri.PERSPECTIVE, {ri.FOV: fov})
    # ri.Rotate(12, 1, 0, 0)
    # ri.Translate(0, 0.75, 2.5)
    #ri.Projection("perspective", {"fov": [15]})

    #ri.Projection("perspective", {"fov": [fov]})

    # # # Set up Perspective Projection with Depth of Field
    # ri.Projection(ri.PERSPECTIVE, {
    #     ri.FOV: fov,                # Field of view (already part of your setup)
    #     "float fstop": [8.0],       # Smaller fstop = more blur (shallow depth of field)
    #     "float focalLength": [50.0],  # Focal length in mm, e.g., 50mm lens
    #     "float focusDistance": [2.5]  # Distance from camera to focus point (scene units)
    # })


    ri.Projection(ri.PERSPECTIVE, {ri.FOV: fov})

    # Adjust the camera's orientation and position



    # # IMAGE TWO!!!!
    # ri.Rotate(-50, 1, 0, 0)          # Camera rotation; value, x, y, z; -5
    # ri.Rotate(0, 0, 1, 0)         # Camera rotation; value, x, y, z
    # #ri.Rotate(12, 0, 0, 1)          # Camera rotation; value, x, y, z
    # ri.Translate(0, -.50, 2)      # Camera position (focusDistance should match if you want to focus here)
    # #ri.DepthOfField(1.40, .050, 1.00)
    


    # # IMAGE TWO NEW!!!!
    # ri.Rotate(-50, 1, 0, 0)          # Camera rotation; value, x, y, z; -5
    # ri.Rotate(0, 0, 1, 0)         # Camera rotation; value, x, y, z
    # #ri.Rotate(12, 0, 0, 1)          # Camera rotation; value, x, y, z
    # ri.Translate(0.15, .1050, 1.3572)      # Camera position (focusDistance should match if you want to focus here)
    # #ri.DepthOfField(1.40, .050, 1.00)
    



    # # # IMAGE ONE!!!!
    # ri.Rotate(-5, 1, 0, 0)          # Camera rotation; value, x, y, z; -5
    # ri.Rotate(0, 0, 1, 0)         # Camera rotation; value, x, y, z
    # #ri.Rotate(12, 0, 0, 1)          # Camera rotation; value, x, y, z
    # ri.Translate(0, .50, 2)      # Camera position (focusDistance should match if you want to focus here)
    # # ri.DepthOfField(3.40, .050, .925)  # aktuell
    
    # # IMAGE ONE NEW SIZE!!!!
    ri.Rotate(-5, 1, 0, 0)          # Camera rotation; value, x, y, z; -5
    # ri.Rotate(0, 0, 1, 0)         # Camera rotation; value, x, y, z
    #ri.Rotate(12, 0, 0, 1)          # Camera rotation; value, x, y, z
    ri.Translate(0.07065, .945328750, 1.075)      # Camera position (focusDistance should match if you want to focus here)
    # ri.DepthOfField(32, .0250, .1125925)  # aktuell
    

    
    
    # 1.4 0.05 6.8     1.4 0.1 7
    # now we start our world
    ri.WorldBegin()


    # LIGHTS
    ri.TransformBegin()
    ri.AttributeBegin()

    ri.Declare("domeLight", "string")
    ri.Declare("lightColorMap", "uniform string")  # good practice

    ri.Rotate(230, 0, 1, 0)         # Camera rotation; value, x, y, z
    ri.Rotate(-90, 1, 0, 0)
    ri.Rotate(10, 0, 0, 1)    #10      # Camera rotation; value, x, y, z
    # ??? ri.Translate(0, -1, 0)      # Camera position (focusDistance should match if you want to focus here)

    # This is where you make the dome light visible to the camera:
    ri.Attribute("visibility", {"camera": [1]})  

    ri.Light("PxrDomeLight", "domeLight", {
        "string lightColorMap": "brown_photostudio_02_4k.tex",
        "float intensity": [.5],
        "float exposure": [.35]
    })

    ri.AttributeEnd()
    ri.TransformEnd()



    ri.TransformBegin()
    ri.AttributeBegin()
    # ri.Translate(0, 0, 0)  # Move the light to the origin

    # Example: add a strong rectangular key light
    ri.TransformBegin()
    #ri.Translate(2, 4, 5)         # position
    ri.Translate(2, 0, 0)
    ri.Translate(0, 0, -2)
    ri.Rotate(15, 1, 0, 0)       # point it down onto the scene
    #ri.Rotate(45, 0, 1, 0)
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
    ri.Translate(0, 0, .315)

    ri.AttributeBegin()
    ri.Attribute("identifier", {"name": "floor"})





    # #ri.Attribute("displacementbound", {"float sphere": [0.2]}) # .2
    # ri.Attribute("displacementbound", {
    # "float sphere": [0.3],
    # "string coordinatesystem": "object"
    #     })


    # ri.Attribute("dice", {
    #     "float micropolygonlength": [0.5]
    # })



    # # Load displacement texture (height map)
    # ri.Pattern("PxrTexture", "floorDisplacementTex", {
    #     "string filename": "wood_table_001_disp_1k.tex",
    #   #  "int linearize": [1]  # Optional, linearize height maps if needed
    # })

    # # Displacement pattern using the texture
    # ri.Displace("PxrDisplace", "floorDisplacement", {
    #     "reference float dispScalar": ["floorDisplacementTex:resultR"],
    #     "float dispAmount": [.01],  # Adjust depth of displacement
    # })


    # Load roughness map
    ri.Pattern("PxrTexture", "floorRoughness", {
        "string filename": "wood_table_001_rough_4k.tex",
       # "int linearize": [1]  # Ensures correct interpretation

    })

    # Load texture
    ri.Pattern("PxrTexture", "floorTexture", {
        "string filename": "wood_table_001_diff_4k.tex"  # Or the full path if needed
    })

    # ri.Pattern("PxrTexture", "floorRoughness", {
    #     "string filename": "wood_table_001_rough_1k.tex"
    # })

    # Use texture as diffuse color
    ri.Bxdf("PxrSurface", "smooth", {
        "reference color diffuseColor": ["floorTexture:resultRGB"],
        #"float specularRoughness": [0.05],  # Very shiny
         # "color specularFaceColor": [0.63, 0.63, 0.63],  # White specular highlight
        "color specularFaceColor": [0.3, 0.3, 0.3],  # White specular highlight

        "reference float specularRoughness": ["floorRoughness:resultR"]

        #"reference float specularRoughness": ["floorRoughness:resultR"]
    })





    
    # ri.Pattern("wood", "woodTx", {})

    # # Use texture as diffuse color
    # ri.Bxdf("PxrDisney", "floorShader", {
    #     "reference color baseColor": ["woodTx:Cout"],
    #     # "reference float roughness": ["floorRoughness:resultR"],

    #     # # Optional parameters for more realism
    #     # "float metallic": [0.0],  # Non-metallic surface
    #     # "float specular": [0.5],  # Adjust specular reflection
    #     # "float anisotropic": [0.0]  # No anisotropy
    # })

    # ri.Displace("PxrDisplace", "floorDisplacement", {
    #     "reference float dispScalar": ["woodTx:Bout"],
    #     "float dispAmount": [.02],  # Adjust depth of displacement
    # })



    # Apply geometry with UV coordinates
    scale = 1  # scale factor for x and z

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
    # ri.TransformBegin()
    ri.Translate(-0.13, -.87, -1.318)

    # ri.Translate(0, -.495, 0)  # Slightly adjust position to avoid z-fighting


    #ri.Scale(1.5, 1.5, 1.5)

    # ri.Translate(0.1, 0.65, -1.35) # ADD this for close up!!!


    # # SPHERE
    # ri.AttributeBegin()
    # ri.Bxdf("PxrSurface", "yarnBallShader",
    # {
    #     "float diffuseGain" : [0.9],  # Bring back warmth
    #     "color diffuseColor" : [1.0, 0.95, 0.9],  # Slightly warmer diffuse
    #     "float diffuseRoughness" : [0.5],



    # })
    # # ri.Scale(0.25, 0.25, 0.25)  # Scale down the sphere
    # # ri.Sphere(.515, -.515, .515, 360.0)  # Sphere at the center .4975
    
    # #radius = .515
    # #surface_pts_s, surface_norms_s = sample_sphere(radius, count)
    # #hair_pts_s, hair_widths_s, hair_npts_s = [], [], []
    # #generate_hairSphere(hair_pts_s, hair_widths_s, hair_npts_s, count=40000, radius=.515, hair_length=0.02, hair_width=0.0004)

    # ri.AttributeBegin()

    # ri.Pattern("PxrFractal", "hairColorNoise", {
    #     "int layers": [3],
    #     "float frequency": [100.0],
    #     "float gain": [0.5],
    #     "float lacunarity": [2.0],
    #     "int octaveCount": [4],
    #     "color colorScale": [0.06, 0.04, 0.03],
    #     "color colorOffset": [1.0, 0.9, 0.8]
    # })

    # ri.Bxdf('PxrMarschnerHair', 'yarnHairShader', {
    #     'float diffuseGain': [0.5],
    #     'color diffuseColor': [1.0, 0.9, 0.8],

    #     'reference color specularColorR': ['hairColorNoise:resultRGB'],
    #     'color specularColorTRT': [1.0, 0.9, 0.75],
    #     'color specularColorTT': [1.0, 0.85, 0.7],

    #     'float specularGainR': [0.1],
    #     'float specularGainTRT': [0.4],
    #     'float specularGainTT': [0.5],
    # })

    # # ri.Curves("cubic", hair_npts_s, "nonperiodic", {
    # #     ri.P: hair_pts_s,
    # #     "float width": hair_widths_s
    # # })

    # ri.AttributeEnd()
    # ri.AttributeEnd()

    
    random.seed(3)  # makes your randomness repeatable across runs

    # # Torus loops
    # num_tori = 0 # 150
    # # R_min, R_max = 10.0, 13.0   # your desired outer‐radius range
    # # tube_r       = 0.5          # fixed tube radius (adjust as needed)

    # for i in range(num_tori):
    #     rx = math.sin(i * 1.1) * 180
    #     ry = math.cos(i * 0.7) * 180
    #     rz = math.sin(i * 0.3) * 180

    #     tx = math.sin(i * 0.69) * 0.015
    #     ty = math.cos(i * 0.6) * 0.015
    #     tz = math.sin(i * 0.64) * 0.015


    #     ri.TransformBegin()
    #     ri.AttributeBegin()
    #     ri.TransformBegin()

    #     ri.Translate(tx, ty, tz)
    #     ri.Rotate(rx, 1, 0, 0)
    #     ri.Rotate(ry, 0, 1, 0)
    #     ri.Rotate(rz, 0, 0, 1)



    #     ri.Attribute("displacementbound", {"float sphere": [0.4]}) # .2
    #     ri.Attribute("dice", {
    #         "float micropolygonlength": [0.1]
    #     })

    #     # ri.Scale(.040510, .040510, .040510)
    #     # ri.Torus(13.251, 0.24181251, 0, 360, 360)

    #     # ri.Pattern(
    #     #     "disp", "disp",
    #     #     {
    #     #         "float scale1": [.1],  # Larger displacement for the first spiral
    #     #         "float repeatU1": [130],  # Repeat factor for the first spiral
    #     #         "float repeatV1": [3.0],  # Repeat factor for the first spiral

    #     #         "float scale2": [0.02],  # 0.04
    #     #         "float repeatU2": [150],  # 
    #     #         "float repeatV2": [-37],  # -7 

    #     #         "float noiseAmount1": [0.035],   # Larger bumps noise strength
    #     #         "float noiseFreq1": [.3],     # Larger bumps frequency

    #     #         "float noiseAmount2": [0.04],   # 0.02, can make it bigger maybe slightly
    #     #         "float noiseFreq2": [2.0]  ,    # between 4 and 5 

    #     #         "float noiseAmount3": [0.00],   # maybe 0.005 or 0.002 but maybe more just slight stripes not bumps
    #     #         "float noiseFreq3": [80.0]      # the smallest bumps on it
    #     #     }
    #     # )

    #     ri.Pattern(
    #         "disp", "disp",
    #         {
    #             "float scale1": [.06],  # Larger displacement for the first spiral
    #             "float repeatU1": [230],  # Repeat factor for the first spiral
    #             "float repeatV1": [10.0],  # Repeat factor for the first spiral

    #             "float scale2": [0.0],  # 0.04
    #             "float repeatU2": [150],  # 
    #             "float repeatV2": [-37],  # -7 

    #             "float noiseAmount1": [0.035],   # Larger bumps noise strength
    #             "float noiseFreq1": [.3],     # Larger bumps frequency

    #             "float noiseAmount2": [0.02],   # 0.02, can make it bigger maybe slightly
    #             "float noiseFreq2": [2.0]  ,    # between 4 and 5 

    #             "float noiseAmount3": [0.00],   # maybe 0.005 or 0.002 but maybe more just slight stripes not bumps
    #             "float noiseFreq3": [80.0]      # the smallest bumps on it
    #         }
    #     )

    #     # # Apply displacement shader
    #     # ri.Displace(
    #     #     "PxrDisplace", "pxrdisp",
    #     #     {"reference float dispScalar": ["disp:resultF"]}
    #     # )


    #     # colour spiral pattern to simulate strands of fibres
    #     ri.Pattern(
    #         "spiralColour", "spiralColour",
    #         {
    #             #"float scale1": [.127],  # Larger displacement for the first spiral
    #             "float repeatU": [900],  # Repeat factor for the first spiral
    #             "float repeatV": [-250.0],  # Repeat factor for the first spiral
    #             #"float blendSharpness" : [10],  # Blend sharpness for the color transition
    #             "color colorB": [0.9, 0.85, 0.8],
    #             "color colorA": [1, 0.095, 0.09],
    #             #            "color colorA": [0.8, 0.7, 0.63],
    #             # "color colorB": [.95, 0.88, 0.73],
    #             # "color colorA": [0.65, 0.55, 0.4],
    #             # "color colorB": [0.85, 0.75, 0.6],

    #         }
    #     )

    #     ri.Bxdf("PxrSurface", "yarnShader",
    #     {
    #         "float diffuseGain" : [.50],  # Bring back warmth
    #         #"reference color diffuseColor": ["spiralColour:resultRGB"],
    #         "color diffuseColor" : [1.0, 0.075, 0.05],  # Slightly warmer diffuse
    #         "float diffuseRoughness" : [0.6],  # Softer light scatter

    #         "float fuzzGain" : [1.0],  # Increase fuzz for soft, warm look
    #         "color fuzzColor" : [1.0, 0.05, 0.05],

    #         # "float subsurfaceGain": [0.3],
    #         # "color subsurfaceColor": [1.0, 0.05, 0.09],
    #         # "float subsurfaceDmfp": [5.0],  # Increase for fluffier light spread
            
    #         # Subsurface scattering for fluffiness
    #         "int subsurfaceType"        : [1],              # 1 = Standard SSS model
    #         "float subsurfaceGain"      : [0.05],           # Tiny amount of SSS
    #         "color subsurfaceColor"     : [1.0, 0.075, 0.02],# Match base color
    #         "float subsurfaceDmfp"      : [1.0], 
    #         # "float subsurfaceGain" : [0.2],
    #         # "color subsurfaceColor" : [0.85, 0.75, 0.6],
    #         # "float subsurfaceDmfp" : [5.0],  # Shorter scattering = less waxy


    #         # Match highlight color to base — subtle red sheen
    #         # "color specularFaceColor" : [0.2, 0.05, 0.02],
    #         "color specularEdgeColor" : [0.25, 0.06, 0.025], # fresnel edge sheen
    #         "float specularRoughness" : [0.6],               # Soft highlights
    #         "int specularFresnelMode" : [0],   
    #     })


    #     Rmaj1 = random.uniform(8.0, 12.0)
    #     #ri.Torus(.325, 0.05, 0.0, 360.0, 360.0)
    #     ri.Scale(.040510, .040510, .040510)
    #     ri.Torus(Rmaj1, 0.24181251, 0, 360, 360)
    #     #wobbly_torus_uvs(ri)

    #     # # 4) scale your torus so its “1.0” major circle becomes Rmaj
    #     # ri.Scale(Rmaj, Rmaj, Rmaj)
    #     # # 5) draw a unit torus with tube radius = tube_r / Rmaj
    #     # ri.Torus(1.0, tube_r/Rmaj, 0, 360, 360)

    #     ri.TransformEnd()  # End the torus transform
    #     ri.AttributeEnd()




    ri.Translate(0, -.495, 0)  # Slightly adjust position to avoid z-fighting

    num_tori3 = 0 # 214 #214  # 213 #50 
    rmaj_values = np.linspace(.8, 1.1, num_tori3)
    # print("rmaj_values", rmaj_values)

    for i in range(num_tori3):
        # rx = math.sin(i * 1.1) * 180
        # ry = math.cos(i * 0.7) * 180
        # rz = math.sin(i * 0.3) * 180

        # tx = math.sin(i * 0.6) * 0.0001
        # ty = math.cos(i * 0.6) * 0.0001
        # tz = math.sin(i * 0.6) * 0.0001
        
        rx = math.sin(i * 1.618) * 180 + random.uniform(-10, 10)
        ry = math.cos(i * 2.718) * 180 + random.uniform(-10, 10)
        rz = math.sin(i * 3.1415) * 180 + random.uniform(-10, 10)

        tx = math.sin(i * 0.06) * 0.0001 + random.uniform(-0.00005, 0.00005)
        ty = math.cos(i * 0.06) * 0.0001 + random.uniform(-0.00005, 0.00005)
        tz = math.sin(i * 0.06) * 0.0001 + random.uniform(-0.00005, 0.00005)


        ri.TransformBegin()
        # ri.TransformBegin()

        ri.Translate(tx, ty, tz)
        ri.Rotate(rx, 1, 0, 0)
        ri.Rotate(ry, 0, 1, 0)
        ri.Rotate(rz, 0, 0, 1)

        ri.AttributeBegin()

        ri.TransformBegin()


        ri.Attribute("displacementbound", {"float sphere": [0.4]}) # .2
        ri.Attribute("dice", {
            "float micropolygonlength": [0.1]
        })



        # ri.Pattern(
        #     "disp", "disp",
        #     {
        #         "float scale1": [.006],  # Larger displacement for the first spiral
        #         "float repeatU1": [230],  # Repeat factor for the first spiral
        #         "float repeatV1": [10.0],  # Repeat factor for the first spiral

        #         "float scale2": [0.0],  # 0.04
        #         "float repeatU2": [150],  # 
        #         "float repeatV2": [-37],  # -7 

        #         "float noiseAmount1": [0.000035],   # Larger bumps noise strength
        #         "float noiseFreq1": [.3],     # Larger bumps frequency

        #         "float noiseAmount2": [0.004],   # 0.02, can make it bigger maybe slightly
        #         "float noiseFreq2": [10.0],

        #         "float noiseAmount3": [0.00],   # maybe 0.005 or 0.002 but maybe more just slight stripes not bumps
        #         "float noiseFreq3": [80.0]      # the smallest bumps on it
        #     }
        # )

        ri.Pattern(
            "disp", "disp",
            {
                "float scale1": [.003],  # Larger displacement for the first spiral
                "float repeatU1": [230],  # Repeat factor for the first spiral
                "float repeatV1": [10.0],  # Repeat factor for the first spiral

                "float scale2": [0.0],  # 0.04
                "float repeatU2": [150],  # 
                "float repeatV2": [-37],  # -7 

                "float noiseAmount1": [0.0015],   # Larger bumps noise strength
                "float noiseFreq1": [.750],     # Larger bumps frequency

                "float noiseAmount2": [0.0032],   # 0.02, can make it bigger maybe slightly
                "float noiseFreq2": [14.0]  ,    # between 4 and 5 

                "float noiseAmount3": [0.00],   # maybe 0.005 or 0.002 but maybe more just slight stripes not bumps
                "float noiseFreq3": [80.0]      # the smallest bumps on it
            }
        )

        # # Apply displacement shader
        # ri.Displace(
        #     "PxrDisplace", "pxrdisp",
        #     {"reference float dispScalar": ["disp:resultF"]}
        # )


        # # colour spiral pattern to simulate strands of fibres
        # ri.Pattern(
        #     "spiralColour", "spiralColour",
        #     {
        #         #"float scale1": [.127],  # Larger displacement for the first spiral
        #         "float repeatU": [100],  # Repeat factor for the first spiral
        #         "float repeatV": [-25.0],  # Repeat factor for the first spiral
        #         #"float blendSharpness" : [10],  # Blend sharpness for the color transition
        #         # "color colorB": [0.9, 0.85, 0.8], # WHITEISH
        #         # "color colorA": [1, 0.095, 0.09],
        #         "color colorB": [0.9, 0.85, 0.8],
        #         "color colorA": [1, 0.095, 0.09],
        #         #            "color colorA": [0.8, 0.7, 0.63],
        #         # "color colorB": [.95, 0.88, 0.73],
        #         # "color colorA": [0.65, 0.55, 0.4],
        #         # "color colorB": [0.85, 0.75, 0.6],

        #     }
        # )

        ri.Pattern(
            "spiralSpec", "spiralSpec",
            {
                #"float scale1": [.127],  # Larger displacement for the first spiral
                "float repeatU": [200],  # Repeat factor for the first spiral
                "float repeatV": [-45.0],  # Repeat factor for the first spiral
                #"float blendSharpness" : [10],  # Blend sharpness for the color transition
                # "color colorB": [0.9, 0.85, 0.8], # WHITEISH
                # "color colorA": [1, 0.095, 0.09],
                "color colorA": [0, 0, 0],  # Pure black for specular
                "color colorB": [.6, .6, .6],  # Pure white for specular
                #            "color colorA": [0.8, 0.7, 0.63],
                # "color colorB": [.95, 0.88, 0.73],
                # "color colorA": [0.65, 0.55, 0.4],
                # "color colorB": [0.85, 0.75, 0.6],

            }
        )

        ri.Bxdf("PxrSurface", "yarnShader",
        {
            "float diffuseGain" : [.50],  # Bring back warmth
            # "reference color diffuseColor": ["spiralSpec:resultRGB"],
            "color diffuseColor" : [1.0, 0.075, 0.05],  # Slightly warmer diffuse
            "float diffuseRoughness" : [0.6],  # Softer light scatter


            # FOR WHITE SHINY WOOL!!!
            # # "reference float specularRoughness": ["spiralSpec:resultMask"],
            # # # "reference color specularFaceColor": ["spiralSpec:resultRGB"],
            # # "float specularGain": [1.0],
            # "color specularFaceColor": [1.0, 1.0, 1.0],
            # "color specularEdgeColor": [1.0, 1.0, 1.0],
            # "int specularFresnelMode": [1],         # Enable Fresnel
            # "color specularIor": [1.5],  # float or colour?           # Default dielectric IOR
            # "reference float specularRoughness": ["spiralSpec:resultMask"]





            "float fuzzGain" : [1.0],  # Increase fuzz for soft, warm look
            "color fuzzColor" : [1.0, 0.05, 0.05],

            # "float subsurfaceGain": [0.3],
            # "color subsurfaceColor": [1.0, 0.05, 0.09],
            # "float subsurfaceDmfp": [5.0],  # Increase for fluffier light spread
            
            # Subsurface scattering for fluffiness
            "int subsurfaceType"        : [1],              # 1 = Standard SSS model
            "float subsurfaceGain"      : [0.05],           # Tiny amount of SSS
            "color subsurfaceColor"     : [1.0, 0.075, 0.02],# Match base color
            "float subsurfaceDmfp"      : [1.0], 
            # "float subsurfaceGain" : [0.2],
            # "color subsurfaceColor" : [0.85, 0.75, 0.6],
            # "float subsurfaceDmfp" : [5.0],  # Shorter scattering = less waxy


            # Match highlight color to base — subtle red sheen
            "color specularFaceColor" : [0.2, 0.05, 0.02],
            "color specularEdgeColor" : [0.25, 0.06, 0.025], # fresnel edge sheen
            "float specularRoughness" : [0.6],               # Soft highlights
            "int specularFresnelMode" : [0],   
        })
        # ri.AttributeEnd()
        # ri.TransformEnd()


        # DISPLACED TORUS 
        Rmaj3 = random.uniform(.998, 1.2)
        #Rmaj2 = float(rmaj_values[i])
        #ri.Torus(.325, 0.05, 0.0, 360.0, 360.0)
        ri.Scale(0.125, 0.125, 0.125)  # Scale down the sphere
        ri.Scale(.40510, .40510, .40510)
        ri.Torus(Rmaj3, 0.024181251, 0, 360, 360)
        ri.TransformEnd()  # End the torus transform
        ri.AttributeEnd()


        # YARN HAIR
        ri.TransformBegin()

        hair_scale = .125
        # Match the effective torus radii
        effective_major = Rmaj3 * 0.40510 *.125 # 13.251 * 0.040510
        effective_minor = 0.024181251 * 0.40510 * .125
        hairlength = 0.0075 *hair_scale
        hairwidth = 0.000215 * hair_scale


        hair_pts, hair_widths, hair_npts = [], [], []

        # # !!!!
        # generate_hair(hair_pts, hair_widths, hair_npts, count=3000, major_radius=effective_major, minor_radius=effective_minor, hair_length=hairlength, hair_width=hairwidth)

        ri.AttributeBegin()


        # ri.Bxdf('PxrMarschnerHair', 'yarnHairShader', {
        #     'float diffuseGain': [0.2],                      # Less diffuse = more specular
        #     'color diffuseColor': [1.0, 0.075, 0.02],            # Pure white base

        #     'color specularColorR': [1.0, 0.075, 0.02],          # White reflection
        #     'color specularColorTRT': [1.0, 0.075, 0.02],        # White transmission/refraction
        #     'color specularColorTT': [1.0, 0.075, 0.02],

        #     'float specularGainR': [1],                    # Strong reflection
        #     'float specularGainTRT': [0.7],                  # Soft glancing light
        #     'float specularGainTT': [0.6],                   # Light transmission
        # })

        ri.Bxdf('PxrMarschnerHair', 'yarnHairShader', {
            'float diffuseGain': [0.2],                     
            'color diffuseColor': [1.0, 0.075, 0.02],  

            'color specularColorR': [1.0, 1, 1],  
            'color specularColorTRT': [1.0, 0.075, 0.02],      
            'color specularColorTT': [1.0, 0.075, 0.02],

            'float specularGainR': [1],                    # Strong reflection
            'float specularGainTRT': [0.7],                  # Soft glancing light
            'float specularGainTT': [0.6],                   # Light transmission
        })


        # # based on the lecture example on hair, these parameters are the minimum needed in the rib
        # ri.Curves("cubic", hair_npts, "nonperiodic", {
        #     ri.P: hair_pts,
        #     "float width": hair_widths
        # })

        ri.AttributeEnd()
        ri.TransformEnd()
        ri.TransformEnd()


    # ri.TransformBegin()
    # ri.Scale(.040510, .040510, .040510)
    # ri.Rotate(90, 1, 0, 0)
    # ri.AttributeBegin()
    # ri.Bxdf("PxrSurface", "yarnShader",
    # {
    #     "color diffuseColor": [1.0, 0.95, 0.9], 

    # })
    # #wobbly_torus(ri)

    # ri.AttributeEnd()




    # ri.TransformEnd()



    # ri.TransformBegin()
    # ri.Scale(0.125, 0.125, 0.125)  # Scale down the sphere
    # ri.Scale(.40510, .40510, .40510)
    # ri.Sphere(1.2, -1.2, 1.2, 360.0)  # Sphere at the center .4975
    # ri.TransformEnd()  # End the torus transform



    random.seed(3)  # makes your randomness repeatable across runs
    manual_rotations = [
        [-5.240707458162173, 180.88458450591904, 177.3991033309616],
        [186.54888206652072, -168.90417928342112, -185.3133800064442],
        [-14.186727925766133, 112.1894558945035, 182.69721007521622],
        [-186.91755406702566, -48.032190496513756, -178.17800138777665],
        [38.16153994509036, -14.610547343105235, 184.2825773102739],
        [183.7215436210862, 101.22591204278933, -188.05089448983549],
        [-47.76817224885389, -152.536153329304, 180.14483186219377],
        [-162.17874014175823, 180.8449782892215, -171.4210501175282],
        [73.58197689300779, -165.2378494670148, 188.09387024244586],
        [165.47000668887625, 136.7041576710969, -188.73072587472566],
        [-83.63698494005737, -89.53962231085663, 175.87774767419745],
        [-165.37653935829763, 13.880939057365039, -183.38082359237887],
        [92.78768478417058, 56.75148486929578, 181.99514491839085],
        [140.28350021782694, -137.56042226582895, -172.64428874836142],
        [-111.273872108123, 169.30958135518037, 182.8776229338847],
        [-136.5925385363655, -180.92643500818687, -175.59360111721927],
        [124.35448761863015, 148.68357602693644, 178.3040090849092],
        [116.29047708574323, -106.80276058684998, -180.67476811838492],
        [-144.74715180330872, 32.1272294365995, 183.52015586031217],
        [-115.93009355783185, 32.029710551357724, -183.74630785963038]
    ]
    manual_positions = [
        [1.039200385961945e-05, 0.0001125720304108054, -4.344711407601869e-05],
        [5.556088419899075e-05, 9.684640474576521e-05, 3.964254577538334e-05],
        [4.877575144322161e-05, 0.00010159898462371676, 3.609640634904096e-05],
        [-1.9702767058463495e-06, 5.148554442578714e-05, 5.4455681040476976e-05],
        [6.588012940110092e-05, 8.663013788527736e-05, 5.386113974123629e-05],
        [-6.851093313799158e-06, 6.723234303587433e-05, 7.610003455595424e-05],
        [2.3814049211999248e-05, 7.868073124481149e-05, 4.373483406804534e-05],
        [7.64161019456326e-05, 0.00014040785851811234, 5.790339952220884e-05],
        [5.308866790158064e-05, 0.00011008119429534836, 1.7290415921708118e-05],
        [8.680784800757933e-05, 0.00013475146962854055, 1.0265408476284153e-05],
        [8.3343436067238e-05, 0.00011981026395378798, 1.0883253452457878e-05],
        [9.940221592207919e-05, 0.0001270627988340705, 6.185372256214777e-05],
        [1.9076243414679077e-05, 4.491905855693145e-05, 5.6732080758846386e-05],
        [5.1710993911650185e-05, 0.00011695729644207325, 0.00010999390606280119],
        [8.402933583728298e-05, 7.267238878566986e-05, 8.647692554161212e-05],
        [5.2096252909226734e-05, 4.226968294448139e-05, 0.00012611242260761186],
        [8.991567820980639e-05, 9.357287637705597e-06, 9.349895096072552e-05],
        [0.00010313894199874717, 3.759429342926969e-05, 0.00010590582713152619],
        [0.0001345263387271205, 2.2245064235721015e-05, 8.382699365213268e-05],
        [7.777874713928374e-05, 5.1321600981589464e-05, 7.090374694814725e-05],
    ]
    #ri.Translate(0, -.495, 0)  # Slightly adjust position to avoid z-fighting

    num_tori2 = 0 #50 
    rmaj_values = np.linspace(1.1, 1.3, num_tori2)
    # print("rmaj_values", rmaj_values)

    # for i in range(num_tori2):
    # for i, (tx, ty, tz) in enumerate(manual_positions):
    for i, ((tx, ty, tz), (rx, ry, rz)) in enumerate(zip(manual_positions, manual_rotations)):

        # rx = math.sin(i * 1.618) * 180 + random.uniform(-10, 10)
        # ry = math.cos(i * 2.718) * 180 + random.uniform(-10, 10)
        # rz = math.cos(i * 3.1415) * 180 + random.uniform(-10, 10)
        # # print("rx, ry, rz", rx, ry, rz)

        # tx = math.sin(i * 0.06) * 0.0001 + random.uniform(-0.00005, 0.00005)
        # ty = math.cos(i * 0.06) * 0.0001 + random.uniform(-0.00005, 0.00005)
        # tz = math.sin(i * 0.06) * 0.0001 + random.uniform(-0.00005, 0.00005)

        ri.TransformBegin()
        # ri.TransformBegin()

        ri.Translate(tx, ty, tz)
        #print("tx, ty, tz", tx, ty, tz)
        ri.Rotate(rx, 1, 0, 0)
        ri.Rotate(ry, 0, 1, 0)
        ri.Rotate(rz, 0, 0, 1)

        ri.AttributeBegin()


        ri.Attribute("displacementbound", {"float sphere": [0.04]}) # .2
        ri.Attribute("dice", {
            "float micropolygonlength": [0.1]
        })

        # ri.Scale(.040510, .040510, .040510)
        # ri.Torus(13.251, 0.24181251, 0, 360, 360)

        # ri.Pattern(
        #     "disp", "disp",
        #     {
        #         "float scale1": [.1],  # Larger displacement for the first spiral
        #         "float repeatU1": [130],  # Repeat factor for the first spiral
        #         "float repeatV1": [3.0],  # Repeat factor for the first spiral

        #         "float scale2": [0.02],  # 0.04
        #         "float repeatU2": [150],  # 
        #         "float repeatV2": [-37],  # -7 

        #         "float noiseAmount1": [0.035],   # Larger bumps noise strength
        #         "float noiseFreq1": [.3],     # Larger bumps frequency

        #         "float noiseAmount2": [0.04],   # 0.02, can make it bigger maybe slightly
        #         "float noiseFreq2": [2.0]  ,    # between 4 and 5 

        #         "float noiseAmount3": [0.00],   # maybe 0.005 or 0.002 but maybe more just slight stripes not bumps
        #         "float noiseFreq3": [80.0]      # the smallest bumps on it
        #     }
        # )

        ri.Pattern(
            "disp", "disp",
            {
                "float scale1": [.003],  # Larger displacement for the first spiral
                "float repeatU1": [230],  # Repeat factor for the first spiral
                "float repeatV1": [10.0],  # Repeat factor for the first spiral

                "float scale2": [0.0],  # 0.04
                "float repeatU2": [150],  # 
                "float repeatV2": [-37],  # -7 

                "float noiseAmount1": [0.0015],   # Larger bumps noise strength
                "float noiseFreq1": [.750],     # Larger bumps frequency

                "float noiseAmount2": [0.0032],   # 0.02, can make it bigger maybe slightly
                "float noiseFreq2": [14.0]  ,    # between 4 and 5 

                "float noiseAmount3": [0.00],   # maybe 0.005 or 0.002 but maybe more just slight stripes not bumps
                "float noiseFreq3": [80.0]      # the smallest bumps on it
            }
        )

        # # Apply displacement shader
        # ri.Displace(
        #     "PxrDisplace", "pxrdisp",
        #     {"reference float dispScalar": ["disp:resultF"]}
        # )


        # # colour spiral pattern to simulate strands of fibres
        # ri.Pattern(
        #     "spiralColour", "spiralColour",
        #     {
        #         #"float scale1": [.127],  # Larger displacement for the first spiral
        #         "float repeatU": [100],  # Repeat factor for the first spiral
        #         "float repeatV": [-25.0],  # Repeat factor for the first spiral
        #         #"float blendSharpness" : [10],  # Blend sharpness for the color transition
        #         # "color colorB": [0.9, 0.85, 0.8], # WHITEISH
        #         # "color colorA": [1, 0.095, 0.09],
        #         "color colorB": [0.9, 0.85, 0.8],
        #         "color colorA": [1, 0.095, 0.09],
        #         #            "color colorA": [0.8, 0.7, 0.63],
        #         # "color colorB": [.95, 0.88, 0.73],
        #         # "color colorA": [0.65, 0.55, 0.4],
        #         # "color colorB": [0.85, 0.75, 0.6],

        #     }
        # )

        ri.Pattern(
            "spiralSpec", "spiralSpec",
            {
                #"float scale1": [.127],  # Larger displacement for the first spiral
                "float repeatU": [200],  # Repeat factor for the first spiral
                "float repeatV": [-45.0],  # Repeat factor for the first spiral
                #"float blendSharpness" : [10],  # Blend sharpness for the color transition
                # "color colorB": [0.9, 0.85, 0.8], # WHITEISH
                # "color colorA": [1, 0.095, 0.09],
                "color colorA": [0, 0, 0],  # Pure black for specular
                "color colorB": [.6, .6, .6],  # Pure white for specular
                #            "color colorA": [0.8, 0.7, 0.63],
                # "color colorB": [.95, 0.88, 0.73],
                # "color colorA": [0.65, 0.55, 0.4],
                # "color colorB": [0.85, 0.75, 0.6],

            }
        )

        ri.Bxdf("PxrSurface", "yarnShader",
        {
            "float diffuseGain" : [.50],  # Bring back warmth
            # "reference color diffuseColor": ["spiralSpec:resultRGB"],
            "color diffuseColor" : [1.0, 0.075, 0.05],  # Slightly warmer diffuse
            "float diffuseRoughness" : [0.6],  # Softer light scatter


            # FOR WHITE SHINY WOOL!!!
            # # "reference float specularRoughness": ["spiralSpec:resultMask"],
            # # # "reference color specularFaceColor": ["spiralSpec:resultRGB"],
            # # "float specularGain": [1.0],
            # "color specularFaceColor": [1.0, 1.0, 1.0],
            # "color specularEdgeColor": [1.0, 1.0, 1.0],
            # "int specularFresnelMode": [1],         # Enable Fresnel
            # "color specularIor": [1.5],  # float or colour?           # Default dielectric IOR
            # "reference float specularRoughness": ["spiralSpec:resultMask"]





            "float fuzzGain" : [1.0],  # Increase fuzz for soft, warm look
            "color fuzzColor" : [1.0, 0.05, 0.05],

            # "float subsurfaceGain": [0.3],
            # "color subsurfaceColor": [1.0, 0.05, 0.09],
            # "float subsurfaceDmfp": [5.0],  # Increase for fluffier light spread
            
            # Subsurface scattering for fluffiness
            "int subsurfaceType"        : [1],              # 1 = Standard SSS model
            "float subsurfaceGain"      : [0.05],           # Tiny amount of SSS
            "color subsurfaceColor"     : [1.0, 0.075, 0.02],# Match base color
            "float subsurfaceDmfp"      : [1.0], 
            # "float subsurfaceGain" : [0.2],
            # "color subsurfaceColor" : [0.85, 0.75, 0.6],
            # "float subsurfaceDmfp" : [5.0],  # Shorter scattering = less waxy


            # Match highlight color to base — subtle red sheen
            "color specularFaceColor" : [0.2, 0.05, 0.02],
            "color specularEdgeColor" : [0.25, 0.06, 0.025], # fresnel edge sheen
            "float specularRoughness" : [0.6],               # Soft highlights
            "int specularFresnelMode" : [0],   
        })
        # ri.AttributeEnd()
        # ri.TransformEnd()


        # DISPLACED TORUS
        Rmaj2 = random.uniform(1.2, 1.3)
        #Rmaj2 = float(rmaj_values[i])
        #ri.Torus(.325, 0.05, 0.0, 360.0, 360.0)
        ri.Scale(0.125, 0.125, 0.125)  # Scale down the sphere
        ri.Scale(.40510, .40510, .40510)
        ri.Torus(Rmaj2, 0.024181251, 0, 360, 360)
        #wobbly_torus_uvs(ri)

        # ri.TransformEnd()
        ri.AttributeEnd()






        # YARN HAIR
        ri.TransformBegin()

        hair_scale = .125
        # Match the effective torus radii
        effective_major = Rmaj2 * 0.40510 *.125 # 13.251 * 0.040510
        effective_minor = 0.024181251 * 0.40510 * .125
        hairlength = 0.0075 *hair_scale
        hairwidth = 0.000215 * hair_scale


        hair_pts, hair_widths, hair_npts = [], [], []

        # # !!!!
        # generate_hair(hair_pts, hair_widths, hair_npts, count=4000, major_radius=effective_major, minor_radius=effective_minor, hair_length=hairlength, hair_width=hairwidth)

        ri.AttributeBegin()


        # ri.Bxdf('PxrMarschnerHair', 'yarnHairShader', {
        #     'float diffuseGain': [0.2],                      # Less diffuse = more specular
        #     'color diffuseColor': [1.0, 0.075, 0.02],            # Pure white base

        #     'color specularColorR': [1.0, 0.075, 0.02],          # White reflection
        #     'color specularColorTRT': [1.0, 0.075, 0.02],        # White transmission/refraction
        #     'color specularColorTT': [1.0, 0.075, 0.02],

        #     'float specularGainR': [1],                    # Strong reflection
        #     'float specularGainTRT': [0.7],                  # Soft glancing light
        #     'float specularGainTT': [0.6],                   # Light transmission
        # })

        ri.Bxdf('PxrMarschnerHair', 'yarnHairShader', {
            'float diffuseGain': [0.2],                     
            'color diffuseColor': [1.0, 0.075, 0.02],  

            'color specularColorR': [1.0, 1, 1],  
            'color specularColorTRT': [1.0, 0.075, 0.02],      
            'color specularColorTT': [1.0, 0.075, 0.02],

            'float specularGainR': [1],                    # Strong reflection
            'float specularGainTRT': [0.7],                  # Soft glancing light
            'float specularGainTT': [0.6],                   # Light transmission
        })



        # ri.Curves("cubic", hair_npts, "nonperiodic", {
        #     ri.P: hair_pts,
        #     "float width": hair_widths
        # })

        ri.AttributeEnd()
        ri.TransformEnd()
        ri.TransformEnd()


    ri.TransformBegin()


    # ri.Scale(.040510, .040510, .040510)
    # ri.Rotate(90, 1, 0, 0)
    # ri.AttributeBegin()
    # ri.Bxdf("PxrSurface", "yarnShader",
    # {
    #     "color diffuseColor": [1.0, 0.95, 0.9], 

    # })
    # #wobbly_torus(ri)

    # ri.AttributeEnd()

    ri.TransformBegin()


    ri.AttributeBegin()


    ri.Attribute("displacementbound", {"float sphere": [0.04]}) # .2
    ri.Attribute("dice", {
        "float micropolygonlength": [0.1]
    })


    ri.Pattern(
        "disp", "disp",
        {
            "float scale1": [.004],  # Larger displacement for the first spiral
            "float repeatU1": [230],  # Repeat factor for the first spiral
            "float repeatV1": [10.0],  # Repeat factor for the first spiral

            "float scale2": [0.0],  # 0.04
            "float repeatU2": [150],  # 
            "float repeatV2": [-37],  # -7 

            "float noiseAmount1": [0.0015],   # Larger bumps noise strength
            "float noiseFreq1": [.750],     # Larger bumps frequency

            "float noiseAmount2": [0.0032],   # 0.02, can make it bigger maybe slightly
            "float noiseFreq2": [14.0]  ,    # between 4 and 5 

            "float noiseAmount3": [0.00],   # maybe 0.005 or 0.002 but maybe more just slight stripes not bumps
            "float noiseFreq3": [80.0]      # the smallest bumps on it
        }
    )

    # Apply displacement shader
    ri.Displace(
        "PxrDisplace", "pxrdisp",
        {"reference float dispScalar": ["disp:resultF"]}
    )


    ri.Bxdf("PxrSurface", "yarnShader",
    {
        "float diffuseGain" : [.50],  # Bring back warmth
        "color diffuseColor" : [1.0, 0.075, 0.05],  # Slightly warmer diffuse
        "float diffuseRoughness" : [0.6],  # Softer light scatter



        "float fuzzGain" : [1.0],  # Increase fuzz for soft, warm look
        "color fuzzColor" : [1.0, 0.05, 0.05],


        # Subsurface scattering for fluffiness
        "int subsurfaceType"        : [1],              # 1 = Standard SSS model
        "float subsurfaceGain"      : [0.05],           # Tiny amount of SSS
        "color subsurfaceColor"     : [1.0, 0.075, 0.02],# Match base color
        "float subsurfaceDmfp"      : [1.0], 

        # Match highlight color to base — subtle red sheen
        "color specularFaceColor" : [0.2, 0.05, 0.02],
        "color specularEdgeColor" : [0.25, 0.06, 0.025], # fresnel edge sheen
        "float specularRoughness" : [0.6],               # Soft highlights
        "int specularFresnelMode" : [0],   
    })


    ri.Rotate(90, 1, 0, 0)
    ri.Translate(-0.075, -0.0510, 0.05)
    ri.Rotate(10, 0, 1, 0)
    ri.Rotate(10, 0, 0, 1)

    ri.Scale(0.125, 0.125, 0.125)
    ri.Scale(.40510, .40510, .40510)
    ri.Torus(1.5, 0.0324181251, 0, 360, 200)

    ri.AttributeEnd()
    ri.TransformEnd() 

    




    ri.TransformEnd()




    
    # # SINGLE YARN
    # ri.TransformBegin()
    # ri.Translate(0, .03071024135, -0.0234569)
    # ri.Scale(.040510, .040510, .040510)
    # ri.Rotate(110, 1, 0, 0)
    # ri.Rotate(10, 0, 1, 0)
    # ri.Translate(0, 0.10, -0.4350)
    # ri.Scale(1.5, 1.5, 1.5)
    # ri.Scale(0.125, 0.125, 0.125)  # Scale down the sphere
    # #ri.Rotate(90, 0, 0, 1)
    # ri.Translate(-10.5, 0, 0) #left side

    # ri.Translate(0, 0, 8) # down?

    # ri.AttributeBegin()
    # ri.Attribute("displacementbound", {"float sphere": [0.4]}) # .2
    # ri.Attribute("dice", {
    #     "float micropolygonlength": [0.1]
    # })

    # ri.Pattern(
    #     "disp", "disp",
    #     {
    #         "float scale1": [.127],  # Larger displacement for the first spiral
    #         "float repeatU1": [100],  # Repeat factor for the first spiral
    #         "float repeatV1": [3.0],  # Repeat factor for the first spiral

    #         "float scale2": [0.005],  # 0.04
    #         "float repeatU2": [150],  # 
    #         "float repeatV2": [-37],  # -7 

    #         "float noiseAmount1": [0.035],   # Larger bumps noise strength
    #         "float noiseFreq1": [.3],     # Larger bumps frequency

    #         "float noiseAmount2": [0.04],   # 0.02, can make it bigger maybe slightly
    #         "float noiseFreq2": [2.0]  ,    # between 4 and 5 

    #         "float noiseAmount3": [0.00],   # maybe 0.005 or 0.002 but maybe more just slight stripes not bumps
    #         "float noiseFreq3": [80.0]      # the smallest bumps on it
    #     }
    # )

    # # # Apply displacement shader
    # # ri.Displace(
    # #     "PxrDisplace", "pxrdisp",
    # #     {"reference float dispScalar": ["disp:resultF"]}
    # # )


    # # colour spiral pattern to simulate strands of fibres
    # ri.Pattern(
    #     "spiralColour", "spiralColour",
    #     {
    #         #"float scale1": [.127],  # Larger displacement for the first spiral
    #         "float repeatU": [900],  # Repeat factor for the first spiral
    #         "float repeatV": [-250.0],  # Repeat factor for the first spiral
    #         #"float blendSharpness" : [10],  # Blend sharpness for the color transition
    #         "color colorB": [0.9, 0.85, 0.8],
    #         "color colorA": [1, 0.95, 0.9],
    #         #            "color colorA": [0.8, 0.7, 0.63],
    #         # "color colorB": [.95, 0.88, 0.73],
    #         # "color colorA": [0.65, 0.55, 0.4],
    #         # "color colorB": [0.85, 0.75, 0.6],

    #     }
    # )

    # ri.Bxdf("PxrSurface", "yarnShader",
    # {
    #     "float diffuseGain" : [0.9],  # Bring back warmth
    #     "reference color diffuseColor": ["spiralColour:resultRGB"],
    #     "float diffuseRoughness" : [0.6],  # Softer light scatter

    #     # "float fuzzGain" : [0.8],  # Increase fuzz for soft, warm look
    #     # "color fuzzColor" : [1.0, 0.95, 0.85],

    #     # # "float subsurfaceGain" : [0.2],
    #     # # "color subsurfaceColor" : [0.85, 0.75, 0.6],
    #     # # "float subsurfaceDmfp" : [5.0],  # Shorter scattering = less waxy

    #     # "float specularRoughness" : [0.65],  # Slightly blurrier reflections
    #     # "color specularFaceColor" : [0.3, 0.28, 0.25],  # Even softer warm specular
    #     # "color specularEdgeColor" : [0.5, 0.45, 0.4],  # Milder fresnel effect

    # })
    # ri.Torus(13.251, 0.31251, 0, 360, 200)
    # ri.AttributeEnd()
    # ri.TransformEnd()





    ri.TransformEnd()

    # end our world
    ri.WorldEnd()
    # and finally end the rib file
    ri.End()





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
