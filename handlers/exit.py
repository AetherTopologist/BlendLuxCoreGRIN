from ..export.image import ImageExporter
from ..draw.viewport import TempfileManager
from ..nodes.volumes import grin
import pyluxcore


def handler():
    ImageExporter.cleanup()
    TempfileManager.cleanup()
    grin.cleanup_preview_images()
    
    # Workaround for a bug in LuxCore:
    # We have to uninstall the log handler to prevent a crash.
    # https://github.com/LuxCoreRender/LuxCore/issues/29
    pyluxcore.SetLogHandler(None)
