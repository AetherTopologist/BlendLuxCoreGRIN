import os

import bpy
from bpy.props import IntProperty, FloatProperty, StringProperty, BoolProperty

from .. import COLORDEPTH_DESC
from ..base import LuxCoreNodeVolume
from ...utils import node as utils_node
from ...utils.light_descriptions import LIGHTGROUP_DESC
import bpy.utils.previews

VOLUME_PRIORITY_DESC = (
    "In areas where two or more volumes overlap, the volume with the highest "
    "priority number will be chosen and completely replace all other volumes"
)


def update_grin_preview(self, context):
    if self.use_uniform_gamma:
        # propagate uniform gamma to individual axes without triggering updates
        self["gamma_x"] = self.uniform_gamma
        self["gamma_y"] = self.uniform_gamma
        self["gamma_z"] = self.uniform_gamma

    self.generate_preview()
    utils_node.force_viewport_update(self, context)



class LuxCoreNodeVolGRIN(LuxCoreNodeVolume, bpy.types.Node):
    bl_label = "GRIN Volume"
    bl_width_default = 160

    # TODO: get name, default, description etc. from super class or something
    priority: IntProperty(update=utils_node.force_viewport_update, name="Priority", default=0, min=0,
                          description=VOLUME_PRIORITY_DESC)
    color_depth: FloatProperty(update=utils_node.force_viewport_update, name="Absorption Depth", default=1.0, min=0.000001,
                                subtype="DISTANCE", unit="LENGTH",
                                description=COLORDEPTH_DESC)
    lightgroup: StringProperty(update=utils_node.force_viewport_update, name="Light Group", description=LIGHTGROUP_DESC)

    n0: FloatProperty(update=utils_node.force_viewport_update,
                        name='IOR n₀',
                        default=1.0, min=0.1,
                        description="Refractive index at the center (n₀)")
    
    nr: FloatProperty(update=utils_node.force_viewport_update,
                        name='IOR n.r',
                        default=1.0, min=0.1,
                        description="Refractive index at the center (n.r)")
    
    radius: FloatProperty(update=utils_node.force_viewport_update,
                        name='Radius',
                        default=10.0, min=0.001,
                        description="Radius for experiment spherical GRIN effect")

    ###################################
    #xPRIMEray Properties
    beta: FloatProperty(update=update_grin_preview,
                        name="Beta (β) – Curve Strength",
                        default=2.0, min=0.0,
                        description="Controls strength of curvature along ray")

    use_uniform_gamma: BoolProperty(update=update_grin_preview,
                                   name="Uniform GRIN",
                                   default=True,
                                   description="Use a single gamma value for all axes")

    uniform_gamma: FloatProperty(update=update_grin_preview,
                                 name="Gamma",
                                 default=1.0, min=0.1,
                                 description="Exponent curvature for all directions")

    gamma_x: FloatProperty(update=update_grin_preview,
                          name="Gamma X (γx)",
                          default=1.0, min=0.1,
                          description="Exponent curvature in X direction")

    gamma_y: FloatProperty(update=update_grin_preview,
                          name="Gamma Y (γy)",
                          default=1.0, min=0.1,
                          description="Exponent curvature in Y direction")

    gamma_z: FloatProperty(update=update_grin_preview,
                          name="Gamma Z (γz)",
                          default=1.0, min=0.1,
                          description="Exponent curvature in Z direction")

    stepSize: FloatProperty(update=utils_node.force_viewport_update,
                        name='RK4 Curve Step Size',
                        default=0.01, min=0.00001,
                        description="Step Size in blender units for RK4 Path Resolution")

    stepLimit: FloatProperty(update=utils_node.force_viewport_update,
                        name='RK4 Curve Step Limit',
                        default=100, min=3,
                        description="Stepper Limit for Curved Path Integrator. Max Distance Limit RK4 Path Detector will halt to cap processing time per ray.")


    def init(self, context):
        self.add_common_inputs()
        self._preview_collection = bpy.utils.previews.new()
        self.generate_preview()

        self.outputs.new("LuxCoreSocketVolume", "Volume")


    def generate_preview(self):
        if not hasattr(self, "_preview_collection"):
            self._preview_collection = bpy.utils.previews.new()

        width = height = 64
        img_name = f"grin_preview_{self.as_pointer()}"
        if img_name in bpy.data.images:
            img = bpy.data.images[img_name]
            if img.size[0] != width or img.size[1] != height:
                img.scale(width, height)
        else:
            img = bpy.data.images.new(img_name, width=width, height=height, alpha=True)

        pixels = [0.0] * (width * height * 4)
        gamma_val = self.uniform_gamma if self.use_uniform_gamma else max(self.gamma_x, self.gamma_y, self.gamma_z)
        ior_min = min(self.n0, self.nr)
        ior_max = max(self.n0, self.nr)
        diff = ior_max - ior_min or 1e-6
        radius = max(self.radius, 1e-6)
        for i in range(width):
            r = (i / (width - 1)) * radius
            t = (r / radius) ** gamma_val
            ior = self.n0 + (self.nr - self.n0) * t
            y = int(((ior - ior_min) / diff) * (height - 1))
            idx = (height - 1 - y) * width + i
            pixels[idx * 4 : idx * 4 + 4] = [1.0, 1.0, 1.0, 1.0]

        img.pixels[:] = pixels
        filepath = os.path.join(bpy.app.tempdir, f"{img_name}.png")
        img.filepath_raw = filepath
        img.file_format = 'PNG'
        img.save()

        # refresh the preview thumbnail
        if "preview" in self._preview_collection:
            self._preview_collection.clear()
        self._preview_collection.load("preview", filepath, 'IMAGE')

    def free(self):
        super().free()
        if hasattr(self, "_preview_collection"):
            bpy.utils.previews.remove(self._preview_collection)
            self._preview_collection = None
        img_name = f"grin_preview_{self.as_pointer()}"
        if img_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[img_name])
        filepath = os.path.join(bpy.app.tempdir, f"{img_name}.png")
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass

    def draw_buttons(self, context, layout):
        self.draw_common_buttons(context, layout)
        layout.prop(self, "n0")
        layout.prop(self, "nr")
        layout.prop(self, "radius")
        layout.prop(self, "beta")
        layout.prop(self, "use_uniform_gamma")
        if self.use_uniform_gamma:
            layout.prop(self, "uniform_gamma")
        else:
            layout.prop(self, "gamma_x")
            layout.prop(self, "gamma_y")
            layout.prop(self, "gamma_z")
        if hasattr(self, "_preview_collection") and "preview" in self._preview_collection:
            layout.label(text="IOR Profile:")
            layout.label(text="", icon_value=self._preview_collection["preview"].icon_id)
        layout.prop(self, "stepSize")
        layout.prop(self, "stepLimit")


    def sub_export(self, exporter, depsgraph, props, luxcore_name=None, output_socket=None):
        gamma_vals = ([self.uniform_gamma] * 3 if self.use_uniform_gamma
                       else [self.gamma_x, self.gamma_y, self.gamma_z])
        definitions = {
            "type": "grin",
            "grin.iormin": [self.n0] * 3,
            "grin.iormax": [self.nr] * 3,
            "grin.stretch": [self.radius] * 3,
            "grin.profile": "radial",
            "grin.beta": self.beta,
            "grin.gamma": gamma_vals,
            "grin.stepsize": self.stepSize,
            "grin.numsteps": self.stepLimit,
        }
        self.export_common_inputs(exporter, depsgraph, props, definitions)
        return self.create_props(props, definitions, luxcore_name)