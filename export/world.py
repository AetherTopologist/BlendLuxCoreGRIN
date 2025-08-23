import pyluxcore
from pyluxcore import Property, Properties
from .. import utils
from ..nodes.output import get_active_output
from . import light
from ..utils.errorlog import LuxCoreErrorLog

# TODO: currently it is not possible to remove the world volume during viewport render

DEBUG_GRIN = False


def export_grin_props(scene, props: Properties):
    g = getattr(scene, "luxcore_grin", None)
    if g is None:
        return

    export_dict = {}

    def clamp(val, mn, mx):
        return max(mn, min(mx, val))

    def set_if_non_default(key, val, default, mn=None, mx=None):
        if mn is not None and mx is not None:
            val = clamp(val, mn, mx)
        if val != default:
            props.Set(Property(key, val))
            export_dict[key] = val

    # Stitching
    set_if_non_default("grin.stitch_plane_factor", g.stitch_plane_factor, 2.0)
    set_if_non_default("grin.stitch_bary_margin", g.stitch_bary_margin, 0.02)
    set_if_non_default("grin.stitch_max_probes", g.stitch_max_probes, 3)
    set_if_non_default("grin.stitch_edge_jitter_count", g.stitch_edge_jitter_count, 2)
    set_if_non_default("grin.stitch_edge_jitter_scale", g.stitch_edge_jitter_scale, 0.0001)
    set_if_non_default("grin.stitch_use_vertex_neighbors", bool(g.stitch_use_vertex_neighbors), False)
    set_if_non_default("grin.stitch_debug", bool(g.stitch_debug), False)

    # Stepping / caps
    set_if_non_default("grin.rk4_step_init", g.rk4_step_init, 0.01, 1e-06, 0.1)
    set_if_non_default("grin.rk4_step_min", g.rk4_step_min, 0.00001, 1e-07, 0.01)
    set_if_non_default("grin.rk4_step_max", g.rk4_step_max, 0.05, 0.0001, 1.0)
    set_if_non_default("grin.rk4_step_curv_k", g.rk4_step_curv_k, 0.25, 0.0, 1.0)
    set_if_non_default("grin.rk4_max_steps", g.rk4_max_steps, 64, 1, 1024)
    set_if_non_default("grin.rk4_max_arc_len", g.rk4_max_arc_len, 0.5, 0.01, 10.0)

    # Linearization
    set_if_non_default("grin.deflect_eps", g.deflect_eps, 0.0001, 1e-06, 0.01)
    set_if_non_default("grin.linearize_threshold", g.linearize_threshold, 0.001, 1e-06, 0.1)
    set_if_non_default("grin.max_linearize_depth", g.max_linearize_depth, 3, 0, 10)

    # Adaptive
    set_if_non_default("grin.adaptive.enable", bool(g.adaptive_enable), False)
    set_if_non_default("grin.adaptive.plane_trigger_factor", g.adaptive_plane_trigger_factor, 1.0)
    set_if_non_default("grin.adaptive.curvature_trigger", g.adaptive_curvature_trigger, 0.1)
    set_if_non_default("grin.adaptive.max_subdiv", g.adaptive_max_subdiv, 4)
    set_if_non_default("grin.adaptive.bisect_iters", g.adaptive_bisect_iters, 5)
    set_if_non_default("grin.adaptive.min_step", g.adaptive_min_step, 0.00001)
    set_if_non_default("grin.adaptive.insight_accept_margin", g.adaptive_insight_accept_margin, 0.01)

    # Edges / seams
    set_if_non_default("grin.uv_seam_tolerance", g.uv_seam_tolerance, 0.00001)
    policy_map = {"REJECT": "reject", "EDGE_PROJECT": "edge_project"}
    policy = policy_map.get(g.uv_cross_island_policy, "reject")
    set_if_non_default("grin.uv_cross_island_policy", policy, "reject")

    # Expert
    set_if_non_default("grin.fast_math", bool(g.fast_math), False)
    set_if_non_default("grin.uv_bary_debug", bool(g.uv_bary_debug), False)

    # Robustness
    set_if_non_default("grin.insight_curvature_threshold", g.insight_curvature_threshold, 0.000001)
    set_if_non_default("grin.barycentric_epsilon", g.barycentric_epsilon, 0.05)
    set_if_non_default("grin.rk4_plane_threshold", g.rk4_plane_threshold, 0.00001)

    if DEBUG_GRIN and export_dict:
        print("[BLC] GRIN props:", export_dict)


def convert(exporter, depsgraph, scene, is_viewport_render):
    props = pyluxcore.Properties()
    world = scene.world

    if not world:
        return props

    # World light (this is a BlendLuxCore concept)
    world_light_props = light.convert_world(exporter, world, scene, is_viewport_render)
    if world_light_props:
        props.Set(world_light_props)

    export_grin_props(scene, props)
  
    # World volume
    volume_node_tree = world.luxcore.volume

    if volume_node_tree:
        luxcore_name = utils.get_luxcore_name(volume_node_tree)
        active_output = get_active_output(volume_node_tree)
        try:
            active_output.export(exporter, depsgraph, props, luxcore_name)
            props.Set(pyluxcore.Property("scene.world.volume.default", luxcore_name))
        except Exception as error:
            msg = 'World "%s": %s' % (world.name, error)
            LuxCoreErrorLog.add_warning(msg)

    return props
