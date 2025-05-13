#!/usr/bin/env rmanpy

import prman, math, random, os

def uniform_sphere_sample(count):
    pts, norms = [], []
    for _ in range(count):
        z = random.uniform(-1, 1)
        θ = random.uniform(0, 2*math.pi)
        r = math.sqrt(1 - z*z)
        x = r * math.cos(θ)
        y = r * math.sin(θ)
        # note: swapping to render with y-up (if needed)
        pts.append((x, z, y))
        norms.append((x, z, y))
    return pts, norms

def generateHairSphere(pts, widths, npts, count=300):
    surface_pts, surface_norms = uniform_sphere_sample(count)
    for (x, y, z), (nx, ny, nz) in zip(surface_pts, surface_norms):
        # each curve has 4 control points
        for i in range(4):
            t = i / 3.0
            px = x + nx * 0.1 * t
            py = y + ny * 0.1 * t
            pz = z + nz * 0.1 * t
            pts.extend([px, py, pz])
        npts.append(4)
        widths.append(0.003)    # <-- one width per curve

# — Init RenderMan —
ri = prman.Ri()
ri.Option("rib", {"string asciistyle": "indented"})

print("Saving to:", os.getcwd())

#ri.Begin("__spherehair.rib")
#ri.Display("SphereHair", "it", "rgba")
#ri.Display("/home/s5723321/Renderman/Lecture3Lightingcopy3/hair_output.exr", "file", "rgba")
ri.Begin("__render")  # or a filename like "pointlight.rib"
ri.Display("torus-hair.tiff", "it", "rgb")
#ri.Display("SphereHair", "it", "rgba")
#ri.Display("hair_output.exr", "file", "rgba")

ri.Format(1024, 1024, 1)
ri.Projection(ri.PERSPECTIVE, {ri.FOV: 40})
ri.ShadingRate(1.0)

ri.WorldBegin()
ri.Translate(0, 0, 5)

# Base sphere
ri.AttributeBegin()
ri.Bxdf("PxrDiffuse", "diff", {"color diffuseColor": [0.3, 0.6, 0.9]})
ri.Sphere(1, -1, 1, 360)
ri.AttributeEnd()

# Generate hair
hair_pts, hair_widths, hair_npts = [], [], []
generateHairSphere(hair_pts, hair_widths, hair_npts, count=500)

ri.AttributeBegin()
ri.Bxdf("PxrMarschnerHair", "hairShader", {"color diffuseColor": [0.6, 0.4, 0.3]})

ri.Curves(
    "cubic",
    hair_npts,
    "nonperiodic",
    {
        ri.P: hair_pts,
        "float width": hair_widths
    }
)

ri.AttributeEnd()
ri.WorldEnd()
ri.End()
print("RenderMan hair test completed.")