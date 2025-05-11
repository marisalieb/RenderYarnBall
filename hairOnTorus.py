#!/usr/bin/env rmanpy

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

# Generate hair curves from points and normals
def generateHair(pts, widths, npts, count=300):
    surface_pts, surface_norms = sample_torus(1.0, 0.3, count)
    for (x, y, z), (nx, ny, nz) in zip(surface_pts, surface_norms):
        for i in range(4):
            t = i / 3.0
            px = x + nx * 0.1 * t
            py = y + ny * 0.1 * t
            pz = z + nz * 0.1 * t
            pts.extend([px, py, pz])
        npts.append(4)
        widths.append(0.003)  # one width per curve

# — RenderMan Setup —
ri = prman.Ri()
ri.Option("rib", {"string asciistyle": "indented"})

output_path = "/home/s5723321/Renderman/MarisaRender/"
print("Saving to:", output_path)

ri.Begin("torushair.rib")
ri.Display("hair_output.exr", "file", "rgba")

# Uncomment below to show in 'it' as well
# ri.Display("TorusHair", "it", "rgba")

ri.Format(1024, 1024, 1)
ri.Projection(ri.PERSPECTIVE, {ri.FOV: 40})
ri.ShadingRate(1.0)

ri.WorldBegin()
ri.Translate(0, 0, 9)
ri.Rotate(-30, 1, 0, 0)

# # Dome light for visibility
# ri.AttributeBegin()
# ri.LightSource("PxrDomeLight", "domeLight", {"float intensity": 1.2})
# ri.AttributeEnd()

# Base torus
ri.AttributeBegin()
ri.Bxdf("PxrDiffuse", "diff", {"color diffuseColor": [0.3, 0.6, 0.9]})
ri.Torus(1.0, 0.3, 0, 360, 360)
ri.AttributeEnd()

# Hair
hair_pts, hair_widths, hair_npts = [], [], []
generateHair(hair_pts, hair_widths, hair_npts, count=500)

ri.AttributeBegin()
ri.Bxdf("PxrMarschnerHair", "hairShader", {"color diffuseColor": [0.6, 0.4, 0.3]})

ri.Curves("cubic", hair_npts, "nonperiodic", {
    ri.P: hair_pts,
    "float width": hair_widths
})
ri.AttributeEnd()

ri.WorldEnd()
ri.End()
print("RenderMan torus hair render completed.")
