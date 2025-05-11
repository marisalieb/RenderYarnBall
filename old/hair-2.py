import math
import random
import os




def generate_linear_hair_rib(filename, num_strands=100, points_per_strand=6, radius=1.0):
    with open(filename, "w") as f:
        f.write('Curves "linear" [')
        f.write(" ".join([str(points_per_strand)] * num_strands))
        f.write('] "nonperiodic"\n')

        # Geometry
        f.write('"vertex point P" [\n')
        for _ in range(num_strands):
            theta = random.uniform(0, 2 * math.pi)
            phi = random.uniform(0, math.pi)
            for j in range(points_per_strand):
                r = radius + j * 0.05
                x = r * math.sin(phi) * math.cos(theta)
                y = r * math.cos(phi)
                z = r * math.sin(phi) * math.sin(theta)
                f.write(f"{x:.4f} {y:.4f} {z:.4f} ")
        f.write("]\n")

        # Width
        f.write('"varying float width" [\n')
        for _ in range(num_strands):
            for j in range(points_per_strand):
                w = 0.02 * (1 - j / (points_per_strand - 1))
                f.write(f"{w:.4f} ")
        f.write("]\n")

        # Color
        f.write('"varying color Cs" [\n')
        for _ in range(num_strands * points_per_strand):
            f.write("0.1 0.1 0.1 ")
        f.write("]\n")

        # t
        f.write('"vertex float t" [\n')
        for _ in range(num_strands):
            for j in range(points_per_strand):
                f.write(f"{j / (points_per_strand - 1):.4f} ")
        f.write("]\n")

    print(f"✅ Linear hair rib written to: {filename}")

print("Writing hair.rib...")
generate_linear_hair_rib("hair2.rib", num_strands=100, points_per_strand=6, radius=1.0)
print("Done.")


import math
import random

def generate_cubic_hair_rib(filename, num_strands=100, points_per_strand=6, radius=1.0):
    rendered_points_per_strand = points_per_strand - 3  # for cubic b-spline

    with open(filename, "w") as f:
        f.write('Attribute "Ri" "string Basis" ["b-spline"]\n')
        f.write('Curves "cubic" [')
        f.write(" ".join([str(points_per_strand)] * num_strands))
        f.write('] "nonperiodic"\n')

        # Geometry
        f.write('"vertex point P" [\n')
        for _ in range(num_strands):
            theta = random.uniform(0, 2 * math.pi)
            phi = random.uniform(0, math.pi)
            for j in range(points_per_strand):
                r = radius + j * 0.05
                x = r * math.sin(phi) * math.cos(theta)
                y = r * math.cos(phi)
                z = r * math.sin(phi) * math.sin(theta)
                f.write(f"{x:.4f} {y:.4f} {z:.4f} ")
        f.write("]\n")

        # Width
        f.write('"varying float width" [\n')
        for _ in range(num_strands):
            for j in range(rendered_points_per_strand):
                w = 0.02 * (1 - j / (rendered_points_per_strand - 1))
                f.write(f"{w:.4f} ")
        f.write("]\n")

        # Color (dark gray)
        f.write('"varying color Cs" [\n')
        for _ in range(num_strands * rendered_points_per_strand):
            f.write("0.1 0.1 0.1 ")
        f.write("]\n")

        # t
        f.write('"vertex float t" [\n')
        for _ in range(num_strands):
            for j in range(rendered_points_per_strand):
                f.write(f"{j / (rendered_points_per_strand - 1):.4f} ")
        f.write("]\n")

    print(f"✅ Cubic hair rib written to: {filename}")



print("Writing hair.rib...")
generate_cubic_hair_rib("hairc.rib", num_strands=100, points_per_strand=6, radius=1.0)
print("Done.")