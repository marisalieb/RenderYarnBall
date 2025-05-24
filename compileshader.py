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

# shadername3 = "displace_noise"
# checkAndCompileShader(shadername3)

shadername4 = "disp"
checkAndCompileShader(shadername4)

shadername5 = "spiralColour"
checkAndCompileShader(shadername5) # bigger maybe slightly

shadername6 = "disp_wobbly"
checkAndCompileShader(shadername6)

shadername7 = "wood"
checkAndCompileShader(shadername7)

shadername8 = "spiralSpec"
checkAndCompileShader(shadername8) # bigger maybe slightly