from setuptools import setup, find_packages

setup(
    name="static-sandwich-detector",
    description="MEV Sandwich Opportunity detector.",
    author="LESC",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=["slither-analyzer==0.11.5"],
    entry_points={
        "slither_analyzer.plugin": "slither my-plugin=detect_sandwich:make_plugin",
    },
)