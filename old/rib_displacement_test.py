# rib_displacement_test.py

rib = """##RenderMan RIB
Display "displaced_sphere.exr" "file" "rgba"
Format 512 512 1
PixelSamples 4 4
ShadingRate 1
Option "searchpath" "shader" ["./:../:./shaders"]

Projection "perspective" "fov" [30]
Translate 0 0 4
Rotate -30 1 0 0

WorldBegin

LightSource "PxrDistantLight" 1 "intensity" [1]

Surface "PxrDisney"
Displacement "myDisplacement" "float dispAmount" [0.2]

Sphere 1 -1 1 360

WorldEnd
"""

with open("displaced_sphere.rib", "w") as f:
    f.write(rib)

print("Wrote displaced_sphere.rib")