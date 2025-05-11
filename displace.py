import prman

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
ri.Scale(0.4, 0.4, 0.4)
ri.Translate(-1, 0, -1)

# Displacement bound
ri.Attribute("displacementbound", {"float sphere": [0.21]})

# Spiral displacement pattern
ri.Pattern(
    "disp", "disp",
    {
        "float scale": [0.2],
        "float repeatU": [10.5],
        "float repeatV": [1.0]
    }
)

# Apply displacement shader
ri.Displace(
    "PxrDisplace", "pxrdisp",
    {"reference float dispScalar": ["disp:resultF"]}
)

# Torus material
ri.Bxdf(
    "PxrDisney", "forTheTorus",
    {"color baseColor": [0.8, 0.1, 0.1]}
)

ri.TransformBegin()
ri.Scale(0.9, 0.9, 0.9)
ri.Rotate(-40, 1, 0, 0)
ri.Torus(1, 0.3, 0, 360, 360)
ri.TransformEnd()
ri.AttributeEnd()

# Ground/sphere patch
ri.Bxdf(
    "PxrDisney", "forTheSphere",
    {"color baseColor": [0.1, 0.8, 0.1]}
)
ri.Patch(
    "bilinear",
    {"P": [
        2, -10, 10,
        2, -10, -10,
        2, 10, 10,
        2, 10, -10
    ]}
)

# End world
ri.WorldEnd()
ri.End()
