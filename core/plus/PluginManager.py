from HookRegistry import HookRegistry
from ServiceRegistry import ServiceRegistry
from Context import Context


class PluginManager:

    @staticmethod
    def execute(action, **kwargs):

        ctx = Context(**kwargs)

        # BEFORE
        for hook in HookRegistry.before.get(action, []):
            hook(ctx)

        # Service major
        service = ServiceRegistry.get(action)

        ctx.result = service(**ctx.__dict__)

        # AFTER
        for hook in HookRegistry.after.get(action, []):
            hook(ctx)

        return ctx.result