import os
import importlib.util
class Plus:
    functions_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../functions')
    )

    @staticmethod
    def _load_module(module_name):
        module_file = os.path.join(Plus.functions_path, f"{module_name}.py")
        spec = importlib.util.spec_from_file_location(module_name, module_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @staticmethod
    def convert_to_utc(date_str, timezone_str):
        module = Plus._load_module('converDate')
        return module.convert_to_utc(date_str, timezone_str)

    @staticmethod
    def convert_from_utc(utc_datetime, timezone_str):
        module = Plus._load_module('converDate')
        return module.convert_from_utc(utc_datetime, timezone_str)
