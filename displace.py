import prman, math, random, os

# Sample points on a torus surface
def sample_torus(major_radius=1.0, minor_radius=0.3, count=500):
    pts, norms = [], []
    for _ in range(count):
        u = random.uniform(0, 2 * math.pi)
        v = random.uniform(0, 2 * math.pi)

        x = (major_radius + minor_radius * math.cos(v)) * math.cos(u)
        y = (major_radius + minor_radius * math.cos(v)) * math.sin(u)
        z = minor_radius * math.sin(v)

        # Surface normal at point
        nx = math.cos(u) * math.cos(v)
        ny = math.sin(u) * math.cos(v)
        nz = math.sin(v)

        pts.append((x, y, z))
        norms.append((nx, ny, nz))
    return pts, norms

# def generateHair(pts, widths, npts, count=900000):
#     surface_pts, surface_norms = sample_torus(1.0, 0.3, count)
#     for (x, y, z), (nx, ny, nz) in zip(surface_pts, surface_norms):
#         # --- ADD DIRECTIONAL VARIATION HERE ---
#         jitter = 0.9  # Increase for wilder variation
#         nx += random.uniform(-jitter, jitter)
#         ny += random.uniform(-jitter, jitter)
#         nz += random.uniform(-jitter, jitter)

#         # Normalize the new vector
#         length = math.sqrt(nx * nx + ny * ny + nz * nz)
#         nx /= length
#         ny /= length
#         nz /= length
#         # ---------------------------------------

#         # Generate 4 control points along the modified direction
#         for i in range(4):
#             t = i / 3.0
#             px = x + nx * 0.1 * t
#             py = y + ny * 0.1 * t
#             pz = z + nz * 0.1 * t
#             pts.extend([px, py, pz])
#         npts.append(4)
#         widths.append(0.001)


# def generateHair(pts, widths, npts, count=900000):
#     surface_pts, surface_norms = sample_torus(1.0, 0.3, count)
#     for (x, y, z), (nx, ny, nz) in zip(surface_pts, surface_norms):
#         # --- CURLY VARIATION USING SINUSOIDAL FUNCTIONS ---
#         jitter = 1.5  # Increased jitter for more random variation
#         curl_strength = random.uniform(0.5, 2.0)  # Control how tightly the hair curls
        
#         # Increase the curl factor for tighter curls
#         curl_factor = random.uniform(6.0, 10.0)  # Increased frequency for tighter curls
#         angle_offset = random.uniform(0, math.pi)  # Offset to randomize curls along the strand

#         # Modify direction based on sinusoidal curls
#         for i in range(4):
#             t = i / 3.0  # Parametric range for the hair strand
            
#             # Calculate curl using a sine wave, increasing amplitude for larger curls
#             curl_x = math.sin(curl_factor * t + angle_offset) * 0.4  # Larger curls in X-axis
#             curl_y = math.cos(curl_factor * t + angle_offset) * 0.4  # Larger curls in Y-axis
#             curl_z = math.sin(curl_factor * t + angle_offset) * 0.1  # Slight curl in Z (smaller)

#             # Combine with the original direction and jitter for randomness
#             nx += random.uniform(-jitter, jitter) + curl_x
#             ny += random.uniform(-jitter, jitter) + curl_y
#             nz += random.uniform(-jitter, jitter) + curl_z

#             # Normalize the new direction vector
#             length = math.sqrt(nx * nx + ny * ny + nz * nz)
#             nx /= length
#             ny /= length
#             nz /= length
            
#             # Generate control points along the curly direction
#             px = x + nx * 0.2 * t  # Increase to make hairs longer
#             py = y + ny * 0.2 * t
#             pz = z + nz * 0.2 * t
#             pts.extend([px, py, pz])
        
#         npts.append(4)  # Add 4 control points for each hair
#         widths.append(0.001)  # Adjust the width to match the fuzziness of the hair



def generateHair(pts, widths, npts, count=900000):
    surface_pts, surface_norms = sample_torus(1.0, 0.3, count)
    for (x, y, z), (nx, ny, nz) in zip(surface_pts, surface_norms):
        # --- CURLY VARIATION USING MULTI-AXIS SINUSOIDAL FUNCTIONS ---
        jitter = 1.5  # Randomness to introduce slight variation in curl direction
        curl_strength = random.uniform(1.5, 3.0)  # Control how tightly the hair curls
        
        # Increased curl factor for tighter curls
        curl_factor = random.uniform(15.0, 30.0)  # Higher frequency for tight, 4C curls
        angle_offset = random.uniform(0, math.pi)  # Offset for randomizing the start of curls

        # More control points for smoother and tighter curls
        num_control_points = 10  # Increased control points for smoother, tighter curls
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
            px = x + nx * 0.12 * t  # Increase to make hairs longer
            py = y + ny * 0.12 * t
            pz = z + nz * 0.12 * t
            pts.extend([px, py, pz])
        
        npts.append(num_control_points)  # Append the updated number of control points for each hair strand
        widths.append(0.001)  # Width of the hair strand (adjust as needed for fuzziness)



# Create the RenderMan interface
ri = prman.Ri()


# Output settings
ri.Begin("__render")  # or a filename like "pointlight.rib"
ri.Display("torus-displaced.tiff", "it", "rgb")

ri.Format(1920, 1080, 1.0)

# Ray-traced hider with incremental sampling
ri.Hider("raytrace", {"int incremental": 1})
ri.PixelVariance(0.1)

# Use the PxrPathTracer integrator
ri.Integrator("PxrPathTracer", "integrator", {})


# Camera setup
ri.Projection("perspective", {"float fov": [30]})
ri.Translate(0, 0, 5)

# Begin world description
ri.WorldBegin()

# Dome light
ri.AttributeBegin()
ri.Rotate(-90, 1, 0, 0)
ri.Light(
    "PxrDomeLight", "theLight",
    {
        "float exposure": [0.0],
        "string lightColorMap": ["textures/EnvMap.tx"]
    }
)
ri.AttributeEnd()


ri.TransformBegin()
ri.Scale(0.7, 0.7, 0.7)
# Displaced torus
ri.AttributeBegin()
ri.Rotate(-90, 1, 0, 0)
#ri.Scale(0.4, 0.4, 0.4)
#ri.Translate(-1, 0, -1)

# Displacement bound
ri.Attribute("displacementbound", {"float sphere": [0.41]}) # 0.21

ri.Attribute("dice", {
    "float micropolygonlength": [0.1] # 0.1
})

# Spiral displacement pattern
# ri.Pattern(
#     "disp", "disp",
#     {
#         "float scale1": [.07],  # Larger displacement for the first spiral
#         "float repeatU1": [10.5],  # Repeat factor for the first spiral
#         "float repeatV1": [3.0],  # Repeat factor for the first spiral
#         "float scale2": [0.02],  # Smaller displacement for the second spiral
#         "float repeatU2": [60.5],  # Repeat factor for the second spiral (smaller)
#         "float repeatV2": [-15],  # Repeat factor for the second spiral (smaller)
#         "float bumpStrength": [0.25],  # Strength of the noise bumps
#     }
# )
# ri.Pattern(
#     "disp", "disp",
#     {
#         "float scale1": [.07],  # Larger displacement for the first spiral
#         "float repeatU1": [10.5],  # Repeat factor for the first spiral
#         "float repeatV1": [3.0],  # Repeat factor for the first spiral
#         "float scale2": [0.02],  # Smaller displacement for the second spiral
#         "float repeatU2": [150],  # Repeat factor for the second spiral (smaller)
#         "float repeatV2": [-55],  # Repeat
#         "float noiseAmount": [0.0125],   # Try 0.01 to 0.1
#         "float noiseFreq": [10.0]      # Try 10.0 to 30.0
#     }
# )

ri.Pattern(
    "disp", "disp",
    {
        "float scale1": [.127],  # Larger displacement for the first spiral
        "float repeatU1": [90],  # Repeat factor for the first spiral
        "float repeatV1": [3.0],  # Repeat factor for the first spiral

        "float scale2": [0.04],  # Smaller displacement for the second spiral # 0.04
        "float repeatU2": [150],  # Repeat factor for the second spiral (smaller)
        "float repeatV2": [-7],  # Repeat

        "float noiseAmount1": [0.035],   # Larger bumps noise strength # 0.075
        "float noiseFreq1": [.30],     # Larger bumps frequency # .3

        "float noiseAmount2": [0.02],   # 0.02, can make it bigger maybe slightly
        "float noiseFreq2": [4.0]  ,    # between 4 and 5 

        "float noiseAmount3": [0.00],   # maybe 0.005 or 0.002 but maybe more just slight stripes not bumps
        "float noiseFreq3": [80.0]      # the smallest bumps on it
    }
)



# Apply displacement shader
ri.Displace(
    "PxrDisplace", "pxrdisp",
    {"reference float dispScalar": ["disp:resultF"]}
)



# # # Torus material
# ri.Bxdf("PxrSurface","yarnShader",
# {
#     "float diffuseGain" : [1.0],
#     "color diffuseColor" : [0.85, 0.75, 0.6],  # Warm wool-like color
#     "float diffuseRoughness" : [0.5],
    
#     "float fuzzGain" : [0.2],  # Soft fuzziness
#     "color fuzzColor" : [1.0, 0.9, 0.8],  # Light fuzz color (can be off-white)
    
#     "float subsurfaceGain" : [0.1],
#     "color subsurfaceColor" : [0.85, 0.75, 0.6],  # Slightly warm subsurface
#     "float subsurfaceDmfp" : [8.0],
    
#     "float specularRoughness" : [0.4],  # Slightly rough specular reflection
#     "color specularFaceColor" : [0.0, 0.0, 0.0],
#     "color specularEdgeColor" : [0.0, 0.0, 0.0],
    
#     #"normal bumpNormal" : [0.05, 0.1, 0.02],  # Subtle bump map for texture
# })


ri.Pattern(
    "spiralColour", "spiralColour",
    {
        #"float scale1": [.127],  # Larger displacement for the first spiral
        "float repeatU": [700],  # Repeat factor for the first spiral
        "float repeatV": [-100.0],  # Repeat factor for the first spiral
        #"float blendSharpness" : [10],  # Blend sharpness for the color transition
        "color colorA": [0.65, 0.55, 0.4],
        "color colorB": [0.85, 0.75, 0.6],

    }
)

ri.Bxdf("PxrSurface","yarnShader",
{
    "reference color diffuseColor": ["spiralColour:resultRGB"],
    # "color diffuseColor" : [0.85, 0.75, 0.6],  # Warm wool-like color

})


ri.TransformBegin()
ri.Rotate(-40, 1, 0, 0)


#ri.Translate(0, 4.1, 3.5) # for overall view
ri.Translate(-0, 4.8, 4.45) # for detailed view


ri.Scale(.040510, .040510, .040510)
ri.Torus(13.251, 0.1481251, 0, 360, 360)

# ri.Scale(.10, .10, .10)
# ri.Torus(13.251, 0.1481251, 0, 360, 360)
# ri.Scale(1.9, 1.9, 01.9)
# ri.Torus(.3251, 0.00481251, 0, 360, 360)
ri.TransformEnd()




ri.AttributeEnd()

ri.TransformEnd()
# ri.AttributeEnd()  # if not hair this is needed





# # Hair
# ri.TransformBegin()
# ri.Scale(0.9, 0.9, 0.9)
# ri.Rotate(-40, 1, 0, 0)
# hair_pts, hair_widths, hair_npts = [], [], []

# # !!!!
# generateHair(hair_pts, hair_widths, hair_npts, count=15000)

# ri.AttributeBegin()
# # ri.Bxdf('PxrMarschnerHair', 'hairShader', {
# #     'float diffuseGain': [0.3],  # Allow some diffuse reflection
# #     'color diffuseColor': [1.0, 0.9, 0.8],#[0.0, 1.0, 0.0],  # Green diffuse color
# #     'color specularColorR': [1.0, 0.9, 0.8],#[0.2, 1.0, 0.2],  # Greenish specular reflections
# #     'color specularColorTRT': [1.0, 0.9, 0.8], # [0.3, 1.0, 0.3],
# #     'color specularColorTT': [1.0, 0.9, 0.8], # [0.3, 1.0, 0.3],
# #     'float specularGainR': [1.0],
# #     'float specularGainTRT': [1.0],
# #     'float specularGainTT': [1.0]
# # })
# ri.Pattern("PxrFractal", "hairColorNoise", {
#     "int layers": [3],
#     "float frequency": [100.0],
#     "float gain": [0.5],
#     "float lacunarity": [2.0],
#     "int octaveCount": [4],
#     "color colorScale": [0.05, 0.05, 0.05],  # subtle variation
#     "color colorOffset": [1.0, 0.95, 0.9]   # base off-white tone
# })

# ri.Bxdf('PxrMarschnerHair', 'yarnHairShader', {
#     'float diffuseGain': [0.2],
#     'color diffuseColor': [1.0, 0.95, 0.9],

#     'reference color specularColorR': ['hairColorNoise:resultRGB'],
#     'color specularColorTRT': [1.0, 0.95, 0.9],
#     'color specularColorTT': [1.0, 0.95, 0.9],

#     'float specularGainR': [0.63],
#     'float specularGainTRT': [0.7],
#     'float specularGainTT': [0.6],
# })


# ri.Curves("cubic", hair_npts, "nonperiodic", {
#     ri.P: hair_pts,
#     "float width": hair_widths
# })
# ri.AttributeEnd()
# ri.TransformEnd()







#ri.AttributeEnd()

# End world
ri.WorldEnd()
ri.End()
