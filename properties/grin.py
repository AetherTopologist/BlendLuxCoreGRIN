import bpy

class LuxCoreGRINProps(bpy.types.PropertyGroup):
    stitch_plane_factor: bpy.props.FloatProperty(
        name="Plane Factor",
        default=2.0,
        min=0.25,
        max=6.0,
        step=5,
        precision=3,
        description="Multiplier on plane-threshold for near-plane neighbor adoption",
    )
    stitch_bary_margin: bpy.props.FloatProperty(
        name="Bary Margin",
        default=0.02,
        min=0.0,
        max=0.1,
        step=1,
        precision=3,
        description="Extra barycentric margin for near-bary neighbors",
    )
    stitch_max_probes: bpy.props.IntProperty(
        name="Max Probes",
        default=6,
        min=0,
        max=24,
        description="How many neighbors to try",
    )
    stitch_edge_jitter_count: bpy.props.IntProperty(
        name="Edge Jitter Count",
        default=2,
        min=0,
        max=16,
        description="Extra nudged rays per neighbor",
    )
    stitch_edge_jitter_scale: bpy.props.FloatProperty(
        name="Edge Jitter Scale",
        default=0.0001,
        min=0.000001,
        max=0.01,
        step=1,
        precision=6,
        description="Fraction of edge length for origin nudge",
    )
    stitch_use_vertex_neighbors: bpy.props.BoolProperty(
        name="Use Vertex Neighbors",
        default=False,
    )
    stitch_debug: bpy.props.BoolProperty(
        name="Debug",
        default=False,
    )

    uv_seam_tolerance: bpy.props.FloatProperty(
        name="UV Seam Tolerance",
        default=0.0001,
        min=0.0,
        max=0.01,
        step=1,
        precision=6,
        description="How far outside (in bary) we still clamp back",
    )
    uv_cross_island_policy: bpy.props.EnumProperty(
        name="UV Cross-Island",
        items=[
            ("reject", "Reject", "Ignore neighbor if outside tri"),
            ("edge_project", "Edge Project", "Project hit to nearest edge"),
        ],
        default="reject",
    )

    insight_curvature_threshold: bpy.props.FloatProperty(
        name="INSIGHT Curvature",
        default=1e-6,
        min=1e-8,
        max=1e-3,
        precision=8,
    )
    barycentric_epsilon: bpy.props.FloatProperty(
        name="Barycentric Epsilon",
        default=0.03,
        min=0.0001,
        max=0.10,
        precision=5,
    )
    rk4_plane_threshold: bpy.props.FloatProperty(
        name="RK4 Plane Threshold",
        default=1e-4,
        min=1e-6,
        max=1e-2,
        precision=8,
    )

    @classmethod
    def register(cls):
        bpy.types.Scene.luxcore_grin = bpy.props.PointerProperty(type=cls)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.luxcore_grin


__all__ = ["LuxCoreGRINProps"]