+248
-45

import bpy
from bpy.props import (
    IntProperty,
    FloatProperty,
    StringProperty,
    BoolProperty,
    PointerProperty,
    EnumProperty,
)

from .. import COLORDEPTH_DESC
from ..base import LuxCoreNodeVolume
from ...utils import node as utils_node
from ...utils.light_descriptions import LIGHTGROUP_DESC

# keep track of preview image datablocks for cleanup
_preview_images = set()

PROFILE_ITEMS = [
    ("POWER", "Power", "Power profile"),
    ("LOG10", "Log10", "Log10 profile"),
    ("LOGE", "LogE", "Natural Log profile"),
    ("EXPONENTIAL", "Exponential", "Exponential profile"),
]

VOLUME_PRIORITY_DESC = (
    "In areas where two or more volumes overlap, the volume with the highest "
    "priority number will be chosen and completely replace all other volumes"
)


def update_grin_preview(self, context):
    if self.use_advanced_mode:
        if self.use_uniform_gamma:
            # propagate uniform gamma to individual axes without triggering updates
            self["gamma_x"] = self.uniform_gamma
            self["gamma_y"] = self.uniform_gamma
            self["gamma_z"] = self.uniform_gamma
    else:
        # Simple mode uses fixed beta/gamma values
        self["beta"] = 2.0
        self["uniform_gamma"] = 1.0
        self["gamma_x"] = 1.0
        self["gamma_y"] = 1.0
        self["gamma_z"] = 1.0

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

    use_advanced_mode: BoolProperty(
        name="Advanced GRIN Control",
        default=False,
        description=(
            "Enable manual gamma/beta control instead of automatic IOR-radius mapping"
        ),
        update=update_grin_preview,
    )

    ior_inner: FloatProperty(
        update=update_grin_preview,
        name="IOR Inner",
        default=1.0,
        min=0.1,
        description="Refractive index at r_inner",
    )

    ior_outer: FloatProperty(
        update=update_grin_preview,
        name="IOR Outer",
        default=1.0,
        min=0.1,
        description="Refractive index at r_outer",
    )

    r_inner: FloatProperty(
        update=update_grin_preview,
        name="r_inner",
        default=0.0,
        min=0.0,
        description="Inner radius where GRIN effect starts",
    )

    r_outer: FloatProperty(
        update=update_grin_preview,
        name="r_outer",
        default=10.0,
        min=0.001,
        description="Outer radius where GRIN effect ends",
    )

    profile_type: EnumProperty(
        name="Profile Type",
        items=PROFILE_ITEMS,
        default="POWER",
        update=update_grin_preview,
    )

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

    preview_image: PointerProperty(type=bpy.types.Image)

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
        self._preview_image = None
        self.generate_preview()

        self.outputs.new("LuxCoreSocketVolume", "Volume")

    def generate_preview(self):
        width = height = 64
        img_name = f"grin_preview_{self.as_pointer()}"
        if not hasattr(self, "_preview_image") or self._preview_image is None:
            if img_name in bpy.data.images:
                img = bpy.data.images[img_name]
                if img.size[0] != width or img.size[1] != height:
                    img.scale(width, height)
            else:
                img = bpy.data.images.new(img_name, width=width, height=height, alpha=True)
            self._preview_image = img
            _preview_images.add(img_name)
        else:
            img = self._preview_image

        pixels = [0.0] * (width * height * 4)
        if self.use_advanced_mode:
            gamma_val = (
                self.uniform_gamma
                if self.use_uniform_gamma
                else max(self.gamma_x, self.gamma_y, self.gamma_z)
            )
        else:
            gamma_val = 1.0
        ior_min = min(self.ior_inner, self.ior_outer)
        ior_max = max(self.ior_inner, self.ior_outer)
        diff = ior_max - ior_min or 1e-6
        r0 = max(self.r_inner, 0.0)
        r1 = max(self.r_outer, r0 + 1e-6)
        for i in range(width):
            r = (i / (width - 1)) * r1
            if r < r0:
                ior = self.ior_inner
            else:
                t = ((r - r0) / (r1 - r0)) ** gamma_val
                ior = self.ior_inner + (self.ior_outer - self.ior_inner) * t
            y = int(((ior - ior_min) / diff) * (height - 1))
            idx = (height - 1 - y) * width + i
            pixels[idx * 4 : idx * 4 + 4] = [1.0, 1.0, 1.0, 1.0]

        img.pixels[:] = pixels
        img.update()
        try:
            img.preview_ensure()
        except AttributeError:
            pass
        self.preview_image = img

    def free(self):
        super().free()
        img_name = f"grin_preview_{self.as_pointer()}"
        if hasattr(self, "_preview_image") and self._preview_image:
            if img_name in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[img_name])
            _preview_images.discard(img_name)
        self._preview_image = None
        self.preview_image = None

    def draw_buttons(self, context, layout):
        self.draw_common_buttons(context, layout)
        layout.prop(self, "use_advanced_mode")
        if self.use_advanced_mode:
            layout.prop(self, "beta")
            layout.prop(self, "use_uniform_gamma")
            if self.use_uniform_gamma:
                layout.prop(self, "uniform_gamma")
            else:
                layout.prop(self, "gamma_x")
                layout.prop(self, "gamma_y")
                layout.prop(self, "gamma_z")
            layout.prop(self, "stepSize")
            layout.prop(self, "stepLimit")
        else:
            layout.prop(self, "ior_inner")
            layout.prop(self, "ior_outer")
            layout.prop(self, "r_inner")
            layout.prop(self, "r_outer")
        layout.prop(self, "profile_type")
        if self.preview_image:
            layout.label(text="IOR Profile:")
            layout.template_preview(self.preview_image, show_buttons=False)


    def sub_export(self, exporter, depsgraph, props, luxcore_name=None, output_socket=None):
        if self.use_advanced_mode:
            gamma_vals = (
                [self.uniform_gamma] * 3
                if self.use_uniform_gamma
                else [self.gamma_x, self.gamma_y, self.gamma_z]
            )
            beta_val = self.beta
        else:
            gamma_vals = [1.0, 1.0, 1.0]
            beta_val = 2.0

        stepsize = self.stepSize
        numsteps = self.stepLimit

        definitions = {
            "type": "grin",
            "grin.iormin": [self.ior_inner] * 3,
            "grin.iormax": [self.ior_outer] * 3,
            "grin.rmin": self.r_inner,
            "grin.rmax": self.r_outer,
            "grin.profile": self.profile_type.lower(),
            "grin.beta": beta_val,
            "grin.gamma": gamma_vals,
            "grin.stepsize": stepsize,
            "grin.numsteps": numsteps,
        }
        self.export_common_inputs(exporter, depsgraph, props, definitions)
        return self.create_props(props, definitions, luxcore_name)


class NODE_PT_grin_preview(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Node"
    bl_label = "GRIN Preview"

    @classmethod
    def poll(cls, context):
        node = getattr(context, "active_node", None)
        return isinstance(node, LuxCoreNodeVolGRIN) and node.preview_image is not None

    def draw(self, context):
        node = context.active_node
        if node.preview_image:
            self.layout.template_preview(node.preview_image, show_buttons=False)


def cleanup_preview_images():
    for name in list(_preview_images):
        if name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[name])
    _preview_images.clear()


def register():
    bpy.utils.register_class(NODE_PT_grin_preview)


def unregister():
    bpy.utils.unregister_class(NODE_PT_grin_preview)
    cleanup_preview_images()