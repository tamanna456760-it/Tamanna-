# tamanna_advanced.py
class TamannaAdvanced:
    """Advanced features for Tamanna language"""

    def __init__(self):
        self.core = TamannaLanguage()
        self.stdlib = StandardLibrary()

    def add_native_function(self, name, function):
        """Add native Python function to Tamanna"""
        self.core.interpreter.functions[name] = function

    def import_module(self, module_name):
        """Import Python modules into Tamanna"""
        try:
            module = __import__(module_name)
            # Expose safe functions to Tamanna
            for attr_name in dir(module):
                if not attr_name.startswith("_"):
                    attr = getattr(module, attr_name)
                    if callable(attr):
                        self.add_native_function(attr_name, attr)
        except ImportError:
            raise ImportError(f"Module {module_name} not found")


class StandardLibrary:
    """Standard library for Tamanna"""

    @staticmethod
    def random_number(kam=0, zyada=100):
        return random.randint(kam, zyada)

    @staticmethod
    def list_banaye(*items):
        return list(items)

    @staticmethod
    def lambai(cheez):
        return len(cheez)

    @staticmethod
    def uppercase(text):
        return text.upper()

    @staticmethod
    def lowercase(text):
        return text.lower()
