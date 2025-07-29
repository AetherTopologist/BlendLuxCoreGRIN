from bpy.utils import register_class, unregister_class
from . import clear, heterogeneous, homogeneous, grin, output, tree
import nodeitems_utils
from .tree import luxcore_node_categories_volume

classes = (
    clear.LuxCoreNodeVolClear,
    heterogeneous.LuxCoreNodeVolHeterogeneous,
    homogeneous.LuxCoreNodeVolHomogeneous,
    grin.LuxCoreNodeVolGRIN,
    output.LuxCoreNodeVolOutput,
    tree.LuxCoreVolumeNodeTree,
)

def register():
    nodeitems_utils.register_node_categories("LUXCORE_VOLUME_TREE", luxcore_node_categories_volume)

    for cls in classes:
        register_class(cls)
    grin.register()


def unregister():
    nodeitems_utils.unregister_node_categories("LUXCORE_VOLUME_TREE")

    for cls in classes:
        unregister_class(cls)
    grin.unregister()