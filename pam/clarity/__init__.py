from . import file_selection_panel
from . import metric_settings_panel
from . import preview_settings_panel

from . import launcher_panel


__all__ = ["file_selection_panel","metric_settings_panel","preview_settings_panel", "launcher_panel"]




def register():
    file_selection_panel.register()
    metric_settings_panel.register()
    launcher_panel.register()
    
    preview_settings_panel.register()
	
	
	
	
def unregister():
    file_selection_panel.unregister()
    metric_settings_panel.unregister()
    launcher_panel.unregister()
	
    preview_settings_panel.unregister()