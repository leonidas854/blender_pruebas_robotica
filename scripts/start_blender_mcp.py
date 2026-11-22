"""Start the installed Blender MCP bridge locally, without changing preferences."""
import sys
from pathlib import Path
import bpy

addon = Path.home() / '.config/blender/5.2/scripts/addons'
sys.path.insert(0, str(addon))
import blender_mcp

if not hasattr(bpy.types.Scene, 'blendermcp_port'):
    blender_mcp.register()
bpy.context.scene.blendermcp_port = 9876
bpy.context.scene.blendermcp_auto_start_server = True
blender_mcp._blendermcp_schedule_auto_start(0.5)
print('VIAJERO_MCP_START_REQUESTED localhost:9876', flush=True)
