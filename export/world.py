import pyluxcore
from pyluxcore import Property, Properties
from .. import utils
from ..nodes.output import get_active_output
from . import light
from ..utils.errorlog import LuxCoreErrorLog

# TODO: currently it is not possible to remove the world volume during viewport render


def export_grin_stitch(scene, props: Properties):
    g = getattr(scene, "luxcore_grin", None)
    if g is None:
        return

    props.Set(Property("grin.stitch_plane_factor")(g.stitch_plane_factor))
    props.Set(Property("grin.stitch_bary_margin")(g.stitch_bary_margin))
    props.Set(Property("grin.stitch_max_probes")(g.stitch_max_probes))
    props.Set(Property("grin.stitch_edge_jitter_count")(g.stitch_edge_jitter_count))
    props.Set(Property("grin.stitch_edge_jitter_scale")(g.stitch_edge_jitter_scale))
    props.Set(Property("grin.stitch_use_vertex_neighbors")(bool(g.stitch_use_vertex_neighbors)))
    props.Set(Property("grin.stitch_debug")(bool(g.stitch_debug)))

    props.Set(Property("grin.uv_seam_tolerance")(g.uv_seam_tolerance))
    props.Set(Property("grin.uv_cross_island_policy")(g.uv_cross_island_policy))

    props.Set(Property("grin.insight_curvature_threshold")(g.insight_curvature_threshold))
    props.Set(Property("grin.barycentric_epsilon")(g.barycentric_epsilon))
    props.Set(Property("grin.rk4_plane_threshold")(g.rk4_plane_threshold))


def convert(exporter, depsgraph, scene, is_viewport_render):
    props = pyluxcore.Properties()
    world = scene.world

    if not world:
        return props

    # World light (this is a BlendLuxCore concept)
    world_light_props = light.convert_world(exporter, world, scene, is_viewport_render)
    if world_light_props:
        props.Set(world_light_props)

    export_grin_stitch(scene, props)

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
