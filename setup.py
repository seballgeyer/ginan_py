from setuptools import setup
import versioneer

setup(
    name="pysat",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=[
        "pysat",
        "pysat.io",
        "pysat.io.grace",
        "pysat.io.orbex",
        "pysat.io.sinex",
        "pysat.data",
        "pysat.tests",
        "pysat.utils",
        "pysat.dbconnector",
    ],
    scripts=[
        "src/pysat/scripts/ginan_mq.py",
    ],
    package_dir={"": "src"},
    url="",
    license="",
    author="Sebastien Allgeyer",
    author_email="sebastien.allgeyer@gmail.com",
    description="analysis of ",
)
