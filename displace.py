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

def generateHair(pts, widths, npts, count=900000):
    surface_pts, surface_norms = sample_torus(1.0, 0.3, count)
    for (x, y, z), (nx, ny, nz) in zip(surface_pts, surface_norms):
        # --- ADD DIRECTIONAL VARIATION HERE ---
        jitter = 0.9  # Increase for wilder variation
        nx += random.uniform(-jitter, jitter)
        ny += random.uniform(-jitter, jitter)
        nz += random.uniform(-jitter, jitter)

        # Normalize the new vector
        length = math.sqrt(nx * nx + ny * ny + nz * nz)
        nx /= length
        ny /= length
        nz /= length
        # ---------------------------------------

        # Generate 4 control points along the modified direction
        for i in range(4):
            t = i / 3.0
            px = x + nx * 0.1 * t
            py = y + ny * 0.1 * t
            pz = z + nz * 0.1 * t
            pts.extend([px, py, pz])
        npts.append(4)
        widths.append(0.001)



# Create the RenderMan interface
ri = prman.Ri()


# Output settings
ri.Begin("__render")  # or a filename like "pointlight.rib"
ri.Display("torus-displaced.tiff", "it", "rgb")

ri.Format(640, 480, 1.0)

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


# Displaced torus
ri.AttributeBegin()
ri.Rotate(-90, 1, 0, 0)
#ri.Scale(0.4, 0.4, 0.4)
#ri.Translate(-1, 0, -1)

# Displacement bound
ri.Attribute("displacementbound", {"float sphere": [0.21]})

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
        "float scale1": [.07],  # Larger displacement for the first spiral
        "float repeatU1": [10.5],  # Repeat factor for the first spiral
        "float repeatV1": [3.0],  # Repeat factor for the first spiral
        "float scale2": [0.01],  # Smaller displacement for the second spiral
        "float repeatU2": [150],  # Repeat factor for the second spiral (smaller)
        "float repeatV2": [-55],  # Repeat

        "float noiseAmount1": [0.0125],   # Larger bumps noise strength
        "float noiseFreq1": [10.0],     # Larger bumps frequency
        "float noiseAmount2": [0.002],   # Smaller bumps noise strength
        "float noiseFreq2": [50.0]  ,    # Smaller bumps frequency
        "float noiseAmount3": [0.002],   # Smaller bumps noise strength
        "float noiseFreq3": [50.0]      # Smaller bumps frequency
    }
)



# Apply displacement shader
ri.Displace(
    "PxrDisplace", "pxrdisp",
    {"reference float dispScalar": ["disp:resultF"]}
)



# # Torus material
ri.Bxdf("PxrSurface","yarnShader",
{
    "float diffuseGain" : [1.0],
    "color diffuseColor" : [0.85, 0.75, 0.6],  # Warm wool-like color
    "float diffuseRoughness" : [0.5],
    
    "float fuzzGain" : [0.2],  # Soft fuzziness
    "color fuzzColor" : [1.0, 0.9, 0.8],  # Light fuzz color (can be off-white)
    
    "float subsurfaceGain" : [0.1],
    "color subsurfaceColor" : [0.85, 0.75, 0.6],  # Slightly warm subsurface
    "float subsurfaceDmfp" : [8.0],
    
    "float specularRoughness" : [0.4],  # Slightly rough specular reflection
    "color specularFaceColor" : [0.0, 0.0, 0.0],
    "color specularEdgeColor" : [0.0, 0.0, 0.0],
    
    #"normal bumpNormal" : [0.05, 0.1, 0.02],  # Subtle bump map for texture
})

# ri.Bxdf("PxrSurface","yarnShader",
# {

#     "color diffuseColor" : [0.85, 0.75, 0.6],  # Warm wool-like color

# })


ri.TransformBegin()
ri.Scale(0.9, 0.9, 0.9)
ri.Rotate(-40, 1, 0, 0)
ri.Torus(1, 0.3, 0, 360, 360)
ri.TransformEnd()
# ri.AttributeEnd()  # if not hair this is needed





# Hair
ri.TransformBegin()
ri.Scale(0.9, 0.9, 0.9)
ri.Rotate(-40, 1, 0, 0)
hair_pts, hair_widths, hair_npts = [], [], []
generateHair(hair_pts, hair_widths, hair_npts, count=15000)

ri.AttributeBegin()
ri.Bxdf('PxrMarschnerHair', 'hairShader', {
    'float diffuseGain': [0.3],  # Allow some diffuse reflection
    'color diffuseColor': [1.0, 0.9, 0.8],#[0.0, 1.0, 0.0],  # Green diffuse color
    'color specularColorR': [1.0, 0.9, 0.8],#[0.2, 1.0, 0.2],  # Greenish specular reflections
    'color specularColorTRT': [1.0, 0.9, 0.8], # [0.3, 1.0, 0.3],
    'color specularColorTT': [1.0, 0.9, 0.8], # [0.3, 1.0, 0.3],
    'float specularGainR': [1.0],
    'float specularGainTRT': [1.0],
    'float specularGainTT': [1.0]
})

ri.Curves("cubic", hair_npts, "nonperiodic", {
    ri.P: hair_pts,
    "float width": hair_widths
})
ri.AttributeEnd()
ri.TransformEnd()






ri.AttributeEnd()

# End world
ri.WorldEnd()
ri.End()
