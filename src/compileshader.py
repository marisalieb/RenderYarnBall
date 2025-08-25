#!/usr/bin/env rmanpy

import prman, os
import sys
import subprocess

print("Current working directory:", os.getcwd())

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



shadername4 = "disp"
checkAndCompileShader(shadername4)

shadername9 = "spiralColourNoise"
checkAndCompileShader(shadername9) 

shadername10 = "spiralSpecNoise"
checkAndCompileShader(shadername10)