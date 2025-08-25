### Rendering project


##### Run instructions
To run this project and render the images, run the files directly in python. There are two different files for the two rendered images. The files are render_image_ONE.py and render_image_TWO.py. 

Dependencies:
- numpy

#
##### Notes

The HDRI and wooden table textures were replaced by 1k textures instead of the 4k texture used in the render to stay within the assignment submission file size limit.

Additionally the following settings were reduced for this submission hand-in compared to the final render images, in order to enable faster code tests without long render times. The images that I handed in with higher render settings took between 9-12 hours which is why I reduced it for this hand in to make the running of the code more testable.
The following settings were reduced:
- shading rate: set to 10 now from previouly 2
- pixel variance: set to 0.1 now from previously 0.01
- maxsamples: disabled
- pixel filter: disabled
