from collections import defaultdict

class PluginRegistry:
    def __init__(self):
        self._registry = defaultdict(
            lambda: defaultdict(list)
        )

    def register(self, module, action, plugin):
        self._registry[module][action].append(plugin)

    def get_plugins(self, module, action, request=None, data=None):
        plugins = self._registry.get(module, {}).get(action, [])
        return [
            p for p in plugins
            if p.is_active(request) and p.is_valid(request, data)
        ]
    
    def count_all(self):
        """Total de plugins registrados (sin filtros)"""
        return sum(
            len(plugins)
            for actions in self._registry.values()
            for plugins in actions.values()
        )
    def count_all(self):
        """Total de plugins registrados (sin filtros)"""
        return sum(
            len(plugins)
            for actions in self._registry.values()
            for plugins in actions.values()
        )
plugins = PluginRegistry()