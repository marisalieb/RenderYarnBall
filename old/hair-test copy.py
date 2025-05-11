import prman

ri = prman.Ri()
ri.Begin("__render")

ri.Display("test", "it", "rgba")
ri.Format(512, 512, 1)
ri.Projection(ri.PERSPECTIVE, {ri.FOV: 30})
ri.WorldBegin()

ri.Translate(0, 0, 5)

# Example points (4 points for the curve)
hair_points = [
    0.0, 0.0, 0.0,  # Point 1
    0.0, 0.2, 0.0,  # Point 2
    0.0, 0.4, 0.0,  # Point 3
    0.0, 0.6, 0.0   # Point 4
]

# Corresponding widths (same number of widths as points)
hair_widths = [0.01, 0.01, 0.01, 0.01]  # One width for each vertex

# Number of points in the curve (1 curve with 4 points)
hair_npoints = [4]

# # Assertions to ensure the correct format and data types
# assert isinstance(hair_points, list), "hair_points should be a list."
# assert all(isinstance(coord, float) for coord in hair_points), "All points should be floats."
# assert len(hair_points) % 3 == 0, "Points should be in groups of 3 (x, y, z)."
# assert isinstance(hair_widths, list), "hair_widths should be a list."
# assert all(isinstance(w, float) for w in hair_widths), "Widths should be floats."
# assert len(hair_widths) == len(hair_points) // 3, "There should be one width for each vertex."
# assert isinstance(hair_npoints, list), "hair_npoints should be a list."
# assert all(isinstance(n, int) for n in hair_npoints), "npoints should be integers."
# assert sum(hair_npoints) == len(hair_widths), "The total number of widths should match the sum of npoints."

ri.AttributeBegin()
ri.Bxdf("PxrMarschnerHair", "hairShader", {
    "color hairColor": [1.0, 0.5, 0.2]
})

# Correct way to pass width
ri.Curves("cubic", hair_npoints, "nonperiodic", {
    ri.P: hair_points,
    ri.WIDTH: hair_widths  # Pass the width directly as a list
})

ri.AttributeEnd()

ri.WorldEnd()
ri.End()
