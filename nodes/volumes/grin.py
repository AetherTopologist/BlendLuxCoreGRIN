import bpy
from bpy.props import IntProperty, FloatProperty, StringProperty
from .. import COLORDEPTH_DESC
from ..base import LuxCoreNodeVolume
from ...utils import node as utils_node
from ...utils.light_descriptions import LIGHTGROUP_DESC

VOLUME_PRIORITY_DESC = (
    "In areas where two or more volumes overlap, the volume with the highest "
    "priority number will be chosen and completely replace all other volumes"
)


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
    beta: FloatProperty(update=utils_node.force_viewport_update,
                        name="Beta (β) – Curve Strength",
                        default=2.0, min=0.0,
                        description="Controls strength of curvature along ray")

    gamma_x: FloatProperty(update=utils_node.force_viewport_update,
                        name="Gamma X (γx)",
                        default=1.0, min=0.1,
                        description="Exponent curvature in X direction")

    gamma_y: FloatProperty(update=utils_node.force_viewport_update,
                        name="Gamma Y (γy)",
                        default=1.0, min=0.1,
                        description="Exponent curvature in Y direction")

    gamma_z: FloatProperty(update=utils_node.force_viewport_update,
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

        self.outputs.new("LuxCoreSocketVolume", "Volume")

    def draw_buttons(self, context, layout):
        self.draw_common_buttons(context, layout)
        layout.prop(self, "n0")
        layout.prop(self, "nr")
        layout.prop(self, "radius")
        layout.prop(self, "beta")
        layout.prop(self, "gamma_x")
        layout.prop(self, "gamma_y")
        layout.prop(self, "gamma_z")
        layout.prop(self, "stepSize")
        layout.prop(self, "stepLimit")


    def sub_export(self, exporter, depsgraph, props, luxcore_name=None, output_socket=None):
        definitions = {
            "type": "grin",
            "grin.iormin": [self.n0] * 3,
            "grin.iormax": [self.nr] * 3,
            "grin.stretch": [self.radius] * 3,
            "grin.profile": "radial",
            "grin.beta": self.beta,
            "grin.gamma": [self.gamma_x, self.gamma_y, self.gamma_z],
            "grin.stepsize": self.stepSize,
            "grin.numsteps": self.stepLimit,
        }
        self.export_common_inputs(exporter, depsgraph, props, definitions)
        return self.create_props(props, definitions, luxcore_name)
