#!/usr/bin/env rmanpy

import prman, math, random, os
import sys
import subprocess

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



# shadername2 = "check"
# checkAndCompileShader(shadername2)

shadername3 = "spiral_displace"
checkAndCompileShader(shadername3)

shadername4 = "show_uvs"
checkAndCompileShader(shadername4)

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


def create_torus(ri, major_radius=1.0, minor_radius=0.3, sides=64, rings=32):
    points = []
    st = []
    polys = []

    for i in range(rings):
        theta = 2 * math.pi * i / rings
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        for j in range(sides):
            phi = 2 * math.pi * j / sides
            cos_phi = math.cos(phi)
            sin_phi = math.sin(phi)

            x = (major_radius + minor_radius * cos_phi) * cos_theta
            y = (major_radius + minor_radius * cos_phi) * sin_theta
            z = minor_radius * sin_phi

            u = i / rings
            v = j / sides

            points.append([x, y, z])
            st.append([u, v])

    # Build quad faces
    for i in range(rings):
        for j in range(sides):
            p0 = i * sides + j
            p1 = i * sides + (j + 1) % sides
            p2 = ((i + 1) % rings) * sides + (j + 1) % sides
            p3 = ((i + 1) % rings) * sides + j
            polys.append([p0, p1, p2, p3])

    # Flatten
    nverts = [4] * len(polys)
    verts = [v for face in polys for v in face]
    flat_points = [coord for pt in points for coord in pt]

    ST = [coord for uv in st for coord in uv]

    # Declare primvars
    ri.Attribute("displacementbound", {
        "float sphere": [20.0],
        "string coordinatesystem": ["world"]
    })

    ri.Attribute("dice", {
        "float micropolygonlength": [0.1],
        "int watertight": [1]
    })

    ri.Pattern(
        "spiral_displace", "spiral_displace",
        {
            "float repeatU": [18.0],
            "float repeatV": [4.0],
            "float scale": [20.0]
        }
    )

    ri.Displace("PxrDisplace", "disp", {
        "reference float dispAmount": ["spiral_displace:disp"]
    })

    ri.Bxdf("PxrSurface", "plastic", {
        "color diffuseColor": [0.7, 0.7, 0.7],
    })

    ri.Geometry("PointsPolygons", {
        "int[] nvertices": nverts,
        "int[] vertices": verts,
        "point P": flat_points,
        "float[2] st": ST
    })



# — RenderMan Setup —
ri = prman.Ri()
ri.Option("rib", {"string asciistyle": "indented"})

output_path = "/home/s5723321/Renderman/Lecture3Lightingcopy3"
#print("Saving to:", output_path)

ri.Begin("__spheretorushair2.rib")
ri.Display("/home/s5723321/Renderman/Lecture3Lightingcopy3/hair_output2.exr", "file", "rgba")

ri.Format(1024, 1024, 1)
ri.Projection(ri.PERSPECTIVE, {ri.FOV: 40})
ri.ShadingRate(1.0)

ri.WorldBegin()

ri.Translate(0, 0, 4)
ri.Rotate(-30, 1, 0, 0)
#ri.Rotate(-150, 0, 1, 0)

ri.AttributeBegin()
ri.Light("PxrDomeLight", "domeLight", {
    "color lightColor": [1.0, 1.0, 1.0],
    "float intensity": [2.0]
})

ri.AttributeEnd()

ri.AttributeBegin()

# # Force fine dicing
# ri.Attribute("dice", {
#     "float micropolygonlength": [0.1],  # Tiny value for high tessellation
#     "int watertight": [1]
# })

# # Match or exceed your displacement amount
# ri.Attribute("displacementbound", {
#     "float sphere": [20],
#     "string coordinatesystem": ["world"]
# })

# # Apply dummy pattern
# ri.Pattern(
#     "spiral_displace", "spiral_displace",
#     {
#         "float scale": [20.0]  # Large, obvious displacement
#     }
# )

# # Displace with constant large value
# ri.Displace(
#     "PxrDisplace", "displace", {
#         "reference float dispAmount": ["spiral_displace:disp"]
#     }
# )

# # Basic material
# ri.Bxdf("PxrSurface", "plastic", {
#     "color diffuseColor": [0.7, 0.7, 0.7],
# })

# # The torus
# ri.Torus(1.0, 0.3, 0, 360, 360)

create_torus(ri)


ri.AttributeEnd()



ri.WorldEnd()
ri.End()
print("RenderMan torus hair render completed.")
