from detect_sandwich.detectors.detect_sandwich import StaticSandwichDetector


def make_plugin():
    plugin_detectors = [StaticSandwichDetector]
    plugin_printers = []

    return plugin_detectors, plugin_printers
