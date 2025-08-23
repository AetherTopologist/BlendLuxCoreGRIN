import bpy


class LuxCoreGRINProps(bpy.types.PropertyGroup):
    rk4_step_init: bpy.props.FloatProperty(
        name="RK4 Step Init",
        default=0.01,
        min=1e-06, max=0.1,
        description="Initial RK4 step size for curved rays.",
    )

    rk4_step_min: bpy.props.FloatProperty(
        name="RK4 Step Min",
        default=0.00001,
        min=1e-07, max=0.01,
        description="Smallest allowed RK4 step after adaptation.",
    )

    rk4_step_max: bpy.props.FloatProperty(
        name="RK4 Step Max",
        default=0.05,
        min=0.0001, max=1.0,
        description="Largest allowed RK4 step after adaptation.",
    )

    rk4_step_curv_k: bpy.props.FloatProperty(
        name="RK4 Curvature K",
        default=0.25,
        min=0.0, max=1.0,
        description="How strongly local curvature reduces step size.",
    )

    rk4_max_steps: bpy.props.IntProperty(
        name="RK4 Max Steps",
        default=64,
        min=1, max=1024,
        description="Hard cap on RK4 steps per segment.",
    )

    rk4_max_arc_len: bpy.props.FloatProperty(
        name="RK4 Max Arc Len",
        default=0.5,
        min=0.01, max=10.0,
        description="Abort curved integration after this path length.",
    )

    deflect_eps: bpy.props.FloatProperty(
        name="Deflect Eps",
        default=0.0001,
        min=1e-06, max=0.01,
        description="Treat segment as linear if accumulated bend stays below this.",
    )

    linearize_threshold: bpy.props.FloatProperty(
        name="Linearize Threshold",
        default=0.001,
        min=1e-06, max=0.1,
        description="Skip RK4 when INSIGHT plane distance is larger than this.",
    )

    max_linearize_depth: bpy.props.IntProperty(
        name="Max Linearize Depth",
        default=3,
        min=0, max=10,
        description="Maximum recursion depth for linear fallback.",
    )

    adaptive_enable: bpy.props.BoolProperty(
        name="Adaptive Enable",
        default=False,
        description="Enable adaptive subdivision of curved segments.",
    )

    adaptive_plane_trigger_factor: bpy.props.FloatProperty(
        name="Plane Trigger Factor",
        default=1.0,
        min=0.0, max=10.0,
        description="Multiplier for linearization plane trigger.",
    )

    adaptive_curvature_trigger: bpy.props.FloatProperty(
        name="Curvature Trigger",
        default=0.1,
        min=0.0, max=1.0,
        description="Curvature threshold to start subdivision.",
    )

    adaptive_max_subdiv: bpy.props.IntProperty(
        name="Max Subdiv",
        default=4,
        min=0, max=10,
        description="Maximum subdivision depth.",
    )

    adaptive_bisect_iters: bpy.props.IntProperty(
        name="Bisect Iters",
        default=5,
        min=0, max=20,
        description="Bisection iterations per subdivision.",
    )

    adaptive_min_step: bpy.props.FloatProperty(
        name="Adaptive Min Step",
        default=0.00001,
        min=1e-07, max=0.1,
        description="Smallest step size during adaptation.",
    )

    adaptive_insight_accept_margin: bpy.props.FloatProperty(
        name="INSIGHT Accept Margin",
        default=0.01,
        min=0.0, max=1.0,
        description="Margin for INSIGHT plane acceptance.",
    )

    fast_math: bpy.props.BoolProperty(
        name="Fast Math",
        default=False,
        description="Use fast exponent approximations (minor precision loss, faster).",
    )

    uv_bary_debug: bpy.props.BoolProperty(
        name="UV Bary Debug",
        default=False,
        description="Debug UV barycentric calculations.",
    )

    stitch_plane_factor: bpy.props.FloatProperty(
        name="Plane Factor",
        default=2.0,
        min=0.5, max=5.0,
        soft_min=0.8, soft_max=3.0,
        step=0.1, precision=3,
        description="Multiplier for the near-plane test used by stitching",
    )

    stitch_bary_margin: bpy.props.FloatProperty(
        name="Bary Margin",
        default=0.02,
        min=0.0, max=0.50,
        soft_min=0.0, soft_max=0.1,
        step=0.01, precision=4,
        description="Extra barycentric tolerance for near-edge acceptance",
    )

    stitch_max_probes: bpy.props.IntProperty(
        name="Max Probes",
        default=3, min=0, max=8,
        description="How many neighbor triangles to try when stitching",
    )

    stitch_edge_jitter_count: bpy.props.IntProperty(
        name="Edge Jitter Count",
        default=2, min=0, max=4,
        description="Extra nudged rays per neighbor along the shared edge",
    )

    stitch_edge_jitter_scale: bpy.props.FloatProperty(
        name="Edge Jitter Scale",
        default=0.0001,
        min=0.000001, max=0.0002,
        soft_min=0.00002, soft_max=0.00015,
        step=0.000005, precision=6,
        description="Fraction of edge length to offset the ray origin for jitter",
    )

    stitch_use_vertex_neighbors: bpy.props.BoolProperty(
        name="Use Vertex Neighbors",
        default=False,
        description="Also probe vertex-adjacent triangles (slower; rarely needed)",
    )

    stitch_debug: bpy.props.BoolProperty(
        name="Stitch Debug",
        default=False,
        description="Verbose logging for stitch decisions",
    )

    uv_seam_tolerance: bpy.props.FloatProperty(
        name="UV Seam Tolerance",
        default=0.00001,                # 1e-5
        min=0.00000001, max=0.01,       # 1e-8 .. 1e-2
        soft_min=0.0000005, soft_max=0.001,  # 5e-7 .. 1e-3
        step=0.00002, precision=8,
        description="Tolerance for accepting barycentrics outside triangle at seams.",
    )

    uv_cross_island_policy: bpy.props.EnumProperty(
        name="UV Cross-Island",
        items=[
            ("REJECT", "Reject", "Reject hits near an edge if they would cross UV islands"),
            ("EDGE_PROJECT", "Edge Project", "Project near-edge hits onto the closest edge before sampling UVs"),
        ],
        default="REJECT",
        description="Strategy for cross-island UV hits.",
    )

    insight_curvature_threshold: bpy.props.FloatProperty(
        name="INSIGHT Curvature",
        default=0.000001,                 # 1e-6
        min=0.00000001, max=0.01,        # 1e-8 .. 1e-2
        soft_min=0.0000001, soft_max=0.01,  # 1e-7 .. 1e-5
        step=0.00001, precision=8,
        description="Guard against division-by-near-zero in symbolic plane solve",
    )

    barycentric_epsilon: bpy.props.FloatProperty(
        name="Barycentric Epsilon",
        default=0.05,
        min=0.0001, max=0.20,
        soft_min=0.005, soft_max=0.10,
        step=0.01, precision=5,
        description="Robustness tolerance for barycentric inside-triangle checks",
    )

    rk4_plane_threshold: bpy.props.FloatProperty(
        name="RK4 Plane Threshold",
        default=0.00001,                   # 1e-5
        min=0.0000001, max=0.01,           # 1e-7 .. 1e-2
        soft_min=0.000001, soft_max=0.001, # 1e-6 .. 1e-3
        step=0.0002, precision=8,
        description="Near-plane threshold used during RK4 marching to trigger a bary test",
    )

    @classmethod
    def register(cls):
        bpy.types.Scene.luxcore_grin = bpy.props.PointerProperty(type=cls)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.luxcore_grin


__all__ = ["LuxCoreGRINProps"]
