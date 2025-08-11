import bpy

class LuxCoreGRINProps(bpy.types.PropertyGroup):
    stitch_plane_factor: bpy.props.FloatProperty(
        name="Plane Factor",
        default=2.0,
        min=0.5, max=5.0,
        soft_min=0.8, soft_max=3.0,
        step=0.1, precision=3,
        description="Multiplier for the near-plane test used by stitching"
    )

    stitch_bary_margin: bpy.props.FloatProperty(
        name="Bary Margin",
        default=0.02,
        min=0.0, max=0.50,
        soft_min=0.0, soft_max=0.1,
        step=0.01, precision=4,
        description="Extra barycentric tolerance for near-edge acceptance"
    )

    stitch_max_probes: bpy.props.IntProperty(
        name="Max Probes",
        default=3, min=0, max=8,
        description="How many neighbor triangles to try when stitching"
    )

    stitch_edge_jitter_count: bpy.props.IntProperty(
        name="Edge Jitter Count",
        default=2, min=0, max=4,
        description="Extra nudged rays per neighbor along the shared edge"
    )

    stitch_edge_jitter_scale: bpy.props.FloatProperty(
        name="Edge Jitter Scale",
        default=0.0001,
        min=0.000001, max=0.0002,
        soft_min=0.00002, soft_max=0.00015,
        step=0.000005, precision=6,
        description="Fraction of edge length to offset the ray origin for jitter"
    )

    stitch_use_vertex_neighbors: bpy.props.BoolProperty(
        name="Use Vertex Neighbors",
        default=False,
        description="Also probe vertex-adjacent triangles (slower; rarely needed)"
    )

    stitch_debug: bpy.props.BoolProperty(
        name="Debug", default=False,
        description="Verbose logging for stitch decisions"
    )

    uv_seam_tolerance: bpy.props.FloatProperty(
        name="UV Seam Tolerance",
        default=0.00001,                # 1e-6
        min=0.00000001, max=0.01,       # 1e-8 .. 1e-3
        soft_min=0.0000005, soft_max=0.001,  # 5e-7 .. 5e-6
        step=0.00002, precision=8,
        description="Distance to triangle edges (in plane) considered a seam proximity"
    )

    uv_cross_island_policy: bpy.props.EnumProperty(
        name="UV Cross-Island",
        items=[
            ("reject", "Reject", "Reject hits near an edge if they would cross UV islands"),
            ("edge_project", "Edge Project", "Project near-edge hits onto the closest edge before sampling UVs"),
        ],
        default="reject",
    )

    insight_curvature_threshold: bpy.props.FloatProperty(
        name="INSIGHT Curvature",
        default=0.000001,                 # 1e-6
        min=0.00000001, max=0.01,        # 1e-8 .. 1e-3
        soft_min=0.0000001, soft_max=0.01,  # 1e-7 .. 1e-5
        step=0.00001, precision=8,
        description="Guard against division-by-near-zero in symbolic plane solve"
    )

    barycentric_epsilon: bpy.props.FloatProperty(
        name="Barycentric Epsilon",
        default=0.05,
        min=0.0001, max=0.20,
        soft_min=0.005, soft_max=0.10,
        step=0.01, precision=5,
        description="Robustness tolerance for barycentric inside-triangle checks"
    )

    rk4_plane_threshold: bpy.props.FloatProperty(
        name="RK4 Plane Threshold",
        default=0.00001,                   # 1e-4
        min=0.0000001, max=0.01,           # 1e-6 .. 1e-2
        soft_min=0.000001, soft_max=0.001, # 1e-5 .. 1e-3
        step=0.0002, precision=8,
        description="Near-plane threshold used during RK4 marching to trigger a bary test"
    )

    @classmethod
    def register(cls):
        bpy.types.Scene.luxcore_grin = bpy.props.PointerProperty(type=cls)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.luxcore_grin


__all__ = ["LuxCoreGRINProps"]
