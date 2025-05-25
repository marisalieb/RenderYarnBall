Python Format

ri.Bxdf('PxrSurface','id',
{
	'float inputMaterial' : ['No Value'], 
	'int utilityPattern' : [0], 
	'float diffuseGain' : [1.0], 
	'color diffuseColor' : [0.18,0.18,0.18], 
	'float diffuseRoughness' : [0.0], 
	'int specularFresnelMode' : [0], 
	'color specularFaceColor' : [0,0,0], 
	'color specularEdgeColor' : [0,0,0], 
	'float specularFresnelShape' : [5.0], 
	'color specularIor' : [1.5,1.5,1.5], 
	'color specularExtinctionCoeff' : [0.0,0.0,0.0], 
	'float specularRoughness' : [0.2], 
	'int roughSpecularFresnelMode' : [0], 
	'color roughSpecularFaceColor' : [0,0,0], 
	'color roughSpecularEdgeColor' : [0,0,0], 
	'float roughSpecularFresnelShape' : [5.0], 
	'color roughSpecularIor' : [1.5,1.5,1.5], 
	'color roughSpecularExtinctionCoeff' : [0.0,0.0,0.0], 
	'float roughSpecularRoughness' : [0.6], 
	'int clearcoatFresnelMode' : [0], 
	'color clearcoatFaceColor' : [0,0,0], 
	'color clearcoatEdgeColor' : [0,0,0], 
	'float clearcoatFresnelShape' : [5.0], 
	'color clearcoatIor' : [1.5,1.5,1.5], 
	'color clearcoatExtinctionCoeff' : [0.0,0.0,0.0], 
	'float clearcoatThickness' : [0.0], 
	'color clearcoatAbsorptionTint' : [0.0,0.0,0.0], 
	'float clearcoatRoughness' : [0.0], 
	'float specularEnergyCompensation' : [0.0], 
	'float clearcoatEnergyCompensation' : [0.0], 
	'float iridescenceFaceGain' : [0], 
	'float iridescenceEdgeGain' : [0], 
	'float iridescenceFresnelShape' : [5.0], 
	'int iridescenceMode' : [0], 
	'color iridescencePrimaryColor' : [1,0,0], 
	'color iridescenceSecondaryColor' : [0,0,1], 
	'float iridescenceRoughness' : [0.2], 
	'float fuzzGain' : [0.0], 
	'color fuzzColor' : [1,1,1], 
	'float fuzzConeAngle' : [8], 
	'int subsurfaceType' : [0], 
	'float subsurfaceGain' : [0.0], 
	'color subsurfaceColor' : [0.830,0.791,0.753], 
	'float subsurfaceDmfp' : [10], 
	'color subsurfaceDmfpColor' : [0.851,0.557,0.395], 
	'float shortSubsurfaceGain' : [0.0], 
	'color shortSubsurfaceColor' : [0.9,0.9,0.9], 
	'float shortSubsurfaceDmfp' : [5], 
	'float longSubsurfaceGain' : [0.0], 
	'color longSubsurfaceColor' : [0.8,0.0,0.0], 
	'float longSubsurfaceDmfp' : [20], 
	'float subsurfaceDirectionality' : [0.0], 
	'float subsurfaceBleed' : [0.0], 
	'float subsurfaceDiffuseBlend' : [0.0], 
	'int subsurfaceResolveSelfIntersections' : [0], 
	'float subsurfaceIor' : [1.4], 
	'float singlescatterGain' : [0.0], 
	'color singlescatterColor' : [0.830,0.791,0.753], 
	'float singlescatterMfp' : [10], 
	'color singlescatterMfpColor' : [0.851,0.557,0.395], 
	'color irradianceTint' : [1.0,1.0,1.0], 
	'float irradianceRoughness' : [0.0], 
	'float unitLength' : [0.1], 
	'float refractionGain' : [0.0], 
	'float reflectionGain' : [0.0], 
	'color refractionColor' : [1,1,1], 
	'float glassRoughness' : [0.1], 
	'float glowGain' : [0.0], 
	'color glowColor' : [1,1,1], 
	'normal bumpNormal' : [0,0,0], 
	'color shadowColor' : [0.0,0.0,0.0], 
	'int shadowMode' : [0], 
	'float presence' : [1], 
	'int presenceCached' : [1], 
	'int mwStartable' : [0], 
	'float roughnessMollificationClamp' : [32], 
})






def sample_torus(major_radius=1.0, minor_radius=0.3, count=500):
    pts, norms = [], []
    for _ in range(count):
        u = random.uniform(0, 2 * math.pi) # around the major radius, as a full circle in radians is 2pi
        v = random.uniform(0, 2 * math.pi) # around the minor radius

		# parametric equation for torus
        x = (major_radius + minor_radius * math.cos(v)) * math.cos(u)
        y = (major_radius + minor_radius * math.cos(v)) * math.sin(u)
        z = minor_radius * math.sin(v)

        # outward pointing surface normals at the sampled point
        nx = math.cos(u) * math.cos(v)
        ny = math.sin(u) * math.cos(v)
        nz = math.sin(v)

        pts.append((x, y, z))
        norms.append((nx, ny, nz))
	
	# return 3d coords on the torus and their normals
    return pts, norms



def generateHair(pts, widths, npts, count=900, major_radius=1.0, 
			minor_radius=0.3, hair_length=0.02, hair_width=0.001):


    surface_pts, surface_norms = sample_torus(major_radius, minor_radius, count)

    for (x, y, z), (nx, ny, nz) in zip(surface_pts, surface_norms):
        # --- CURLY VARIATION USING MULTI-AXIS SINUSOIDAL FUNCTIONS ---
        jitter = 1.5  # Randomness to introduce slight variation in curl direction
        curl_strength = random.uniform(1.5, 3.0)  # Control how tightly the hair curls
        
        # Increased curl factor for tighter curls
        curl_factor = random.uniform(15.0, 30.0)  # Higher frequency for tight, 4C curls
        angle_offset = random.uniform(0, math.pi)  # Offset for randomizing the start of curls

        # More control points for smoother and tighter curls
        num_control_points = 10  # Increased control points for smoother, tighter curls

        variation = random.uniform(0.5, 2.5)  # Vary hair length ±50%
        strand_length = hair_length * variation

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
            px = x + nx * strand_length * t  # Increase to make hairs longer 0.012
            py = y + ny * strand_length * t
            pz = z + nz * strand_length * t
            pts.extend([px, py, pz])
        
        npts.append(num_control_points)  # Append the updated number of control points for each hair strand
        widths.append(hair_width)  # 0.001 beofre but maybe too thick; Width of the hair strand (adjust as needed for fuzziness)




for loop:
		ri.Torus()

        # YARN HAIR
        ri.TransformBegin()

        hair_scale = .125
        # Match the effective torus radii
        effective_major = Rmaj2 * 0.40510 *.125 # 13.251 * 0.040510
        effective_minor = 0.024181251 * 0.40510 * .125
        hairlength = 0.0075 *hair_scale
        hairwidth = 0.000215 * hair_scale


        hair_pts, hair_widths, hair_npts = [], [], []

        # # !!!!
        generateHair(hair_pts, hair_widths, hair_npts, count=4000, major_radius=effective_major, minor_radius=effective_minor, hair_length=hairlength, hair_width=hairwidth)

        ri.AttributeBegin()


        ri.Bxdf('PxrMarschnerHair', 'yarnHairShader', {
            'float diffuseGain': [0.2],                     
            'color diffuseColor': [1.0, 0.075, 0.02],  

            'color specularColorR': [1.0, 1, 1],  
            'color specularColorTRT': [1.0, 0.075, 0.02],      
            'color specularColorTT': [1.0, 0.075, 0.02],

            'float specularGainR': [1],                    # Strong reflection
            'float specularGainTRT': [0.7],                  # Soft glancing light
            'float specularGainTT': [0.6],                   # Light transmission
        })


        ri.Curves("cubic", hair_npts, "nonperiodic", {
            ri.P: hair_pts,
            "float width": hair_widths
        })

        ri.AttributeEnd()
        ri.TransformEnd()
        ri.TransformEnd()

