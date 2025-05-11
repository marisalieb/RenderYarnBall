#!/usr/bin/env rmanpy

import prman, math, random, os
import sys
import subprocess
import array


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

# shadername4 = "show_uvs"
# checkAndCompileShader(shadername4)

def make_subdiv_torus(ri,
                      major=1.0, minor=0.3,
                      sides=64, rings=32,
                      bound=25.0, dice_sz=0.05, disp_scale=20.0):
    # 1) Build P & (optionally ST)
    P, ST = [], []
    for i in range(rings):
        theta = 2*math.pi*i/rings
        cθ, sθ = math.cos(theta), math.sin(theta)
        for j in range(sides):
            phi = 2*math.pi*j/sides
            cφ, sφ = math.cos(phi), math.sin(phi)
            x = (major + minor*cφ)*cθ
            y = minor*sφ
            z = (major + minor*cφ)*sθ
            P += [x,y,z]
            ST += [i/rings, j/sides]

    # 2) Build quads
    nverts, verts = [], []
    for i in range(rings):
        for j in range(sides):
            p0 = i*sides + j
            p1 = i*sides + (j+1)%sides
            p2 = ((i+1)%rings)*sides + (j+1)%sides
            p3 = ((i+1)%rings)*sides + j
            verts += [p0,p1,p2,p3]
            nverts.append(4)

    # 3) Convert to typed arrays
    P_arr      = array.array('f', P)
    #ST_arr     = array.array('f', ST)
    nverts_arr = array.array('i', nverts)
    verts_arr  = array.array('i', verts)

    # 4) Setup attributes and displacement
    ri.AttributeBegin()
    ri.ShadingRate(0.1)
    ri.Attribute("dice", {"float micropolygonlength":[dice_sz], "int watertight":[1]})
    ri.Attribute("displacementbound", {"float sphere":[bound], "string coordinatesystem":["world"]})
    ri.Pattern("spiral_displace","pattern",{"float repeatU":[18.0],"float repeatV":[4.0],"float scale":[disp_scale]})
    ri.Displace("PxrDisplace","disp",{"reference float dispAmount":["pattern:disp"]})
    ri.Bxdf("PxrSurface","mat",{"color diffuseColor":[0.8,0.8,0.8]})

    # 5) Use generic Geometry call for SubdivisionMesh
    ri.Geometry("SubdivisionMesh", {
        "string scheme":   ["catmull-clark"],
        "int[] nvertices": nverts_arr,
        "int[] vertices":  verts_arr,
        "point P":         P_arr,
        # If you want UVs:
        # "float[2] st":     ST_arr
    })
    ri.AttributeEnd()





# — RenderMan Setup —
ri = prman.Ri()
ri.Option("rib", {"string asciistyle": "indented"})

output_path = "/home/s5723321/Renderman/Lecture3Lightingcopy3"
#print("Saving to:", output_path)

ri.Begin("__spheretorushair2.rib")
ri.Display("/home/s5723321/Renderman/Lecture3Lightingcopy3/hair_output2.exr", "file", "rgba")

ri.Format(1024, 1024, 1)
ri.Projection(ri.PERSPECTIVE, {ri.FOV: 40})
ri.ShadingRate(1)

ri.WorldBegin()

ri.Translate(0, 0, 20)
ri.Rotate(-30, 1, 0, 0)
#ri.Rotate(-150, 0, 1, 0)

ri.AttributeBegin()
ri.Light("PxrDomeLight", "domeLight", {
    "color lightColor": [1.0, 1.0, 1.0],
    "float intensity": [2.0]
})

ri.AttributeEnd()

# ri.Sphere(1, -1, 1, 360)  # Should render clearly


ri.AttributeBegin()
#ri.Translate(0, 0, -40000)
# # Force fine dicing
# ri.ShadingRate(0.1)
# ri.Attribute("dice", {
#     "float micropolygonlength": [0.05],  # Tiny value for high tessellation
#     "int watertight": [1]
# })

# # Match or exceed your displacement amount
# ri.Attribute("displacementbound", {
#     "float sphere": [25],
#     "string coordinatesystem": ["world"]
# })

# # 3) Your displacement pattern (constant test or spiral)
# ri.Pattern("spiral_displace", "spiral_displace", {
#     "float repeatU": [18.0],
#     "float repeatV": [4.0],
#     "float scale":   [20.0]   # max displacement
# })


# # Displace with constant large value
# ri.Displace(
#     "PxrDisplace", "displace", {
#         "reference float dispAmount": ["spiral_displace:disp"]
#     }
# )


# ri.Bxdf("PxrSurface", "plastic", {
#     "color diffuseColor": [1.0, 0.0, 0.0],  # Bright red to test visibility
# })

# # The torus
ri.Torus(1.0, 0.3, 0, 360, 360)
# #make_subdiv_torus(ri)
# # Use the RIB file with a mesh exported from Maya
# ri.Scale(0.0001, 0.0001, 0.0001)  # Shrink it massively
# ri.ReadArchive("torus-maya2.rib")


ri.AttributeEnd()

# ri.AttributeBegin()
# ri.Translate(0, 0, -20)   # Pull torus back into view
# ri.Scale(0.01, 0.01, 0.01)  # Scale way down
# ri.Bxdf("PxrSurface", "bxdf", {
#     "color diffuseColor": [1, 0, 0]  # RED — make sure it's visible
# })

# ri.ReadArchive("torus-maya2.rib")
# ri.AttributeEnd()

# # Add visible test sphere
# ri.AttributeBegin()
# ri.Translate(0, 0, 0)
# ri.Bxdf("PxrSurface", "sphere_test", {
#     "color diffuseColor": [0.0, 1.0, 0.0],
# })
# ri.Sphere(0.5, -0.5, 0.5, 360)
# ri.AttributeEnd()


ri.WorldEnd()
ri.End()
print("RenderMan torus hair render completed.")
