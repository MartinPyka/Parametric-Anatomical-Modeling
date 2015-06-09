"""Python script for automated rendering for pam animations.
Usage: Call Blender with this python script to automatically load a model, adjust settings, create animation and render it.

$ blender -b file.blend --python render_animation.py -- arg1=value arg2=42 arg3=12.3

Your blendfile has to be prepared for pam and model and simulation data must be correct. If no model is given in argv,
the script tries to find one with the same name in the same directory. Anything else should be predefined in the blend file
or passed by argv to overwrite.

Possible arguments:

st: :float: start time
et: :float: end time
sf: :int: start frame
ef: :int: end frame
m:  :string: pam model
s:  :string: simulation data
"""

import bpy
import pam
import sys

if '--' in sys.argv and len(sys.argv) > sys.argv.index('--'):
    args = sys.argv[sys.argv.index('--') + 1:]
else:
    args = None

possible_arguments = {  'st': ('pam_anim_animation.startTime', 'd'),
                        'et': ('pam_anim_animation.endTime', 'd'),
                        'sf': ('pam_anim_animation.startFrame', 'i'),
                        'ef': ('pam_anim_animation.endFrame', 'i'),
                        'm' : ('model', 's'), # Gets a special treatment
                        's' : ('pam_anim_data.simulationData', 's')}

for arg in args:
    for parg in possible_arguments:
        if arg.split('=')[0] == parg:
            value = arg.split('=')[1]
            target = possible_arguments[parg]
            if target[1] == 'd':
                value = float(value)
            elif target[1] == 'i':
                value = int(value)
            elif target[1] == 'b':
                value = bool(int(value))

            if parg == 'm':
                pam.model.load(value)
                break

            op = bpy.context.scene
            for path in target[0].split('.')[:-1]:
                op = getattr(op, path)
            setattr(op, target[0].split('.')[-1], value)

            # Set the start and end frame for rendering
            if parg == 'sf':
                bpy.context.scene.frame_start = value
            elif parg == 'ef':
                bpy.context.scene.frame_end = value

if not pam.model.NG_LIST:
    pam.model.load(bpy.data.filepath.replace(".blend", ".pam"))

bpy.ops.pam_anim.generate()

bpy.ops.render.render(animation=True)