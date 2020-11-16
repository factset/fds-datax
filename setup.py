from setuptools import setup

REQUIRES = ["pandas >= 0.23.4", "pyodbc >= 4.0.23", "pyarrow >= 0.16.0"]

setup(
    name="fds.datax",
    description="""fds.datax offers instant access to define and retrieve a time-series universe of securities that is cached into a centralized
data store. Having access to a cached data store shifts the research period focused on building a universe to immediately
analyzing FactSet’s core & 3rd Party data using a consistent process.""",
    version="0.1.0",
    url="",
    author="CTS PPG",
    install_requires=REQUIRES,
    packages=["fds.datax"],
    package_data={"fds.datax": ["sql_files/*.sql"]},
    package_dir={"fds": "fds"},
    setup_requires=["pytest-runner"],
    tests_require=["pytest"]
)
