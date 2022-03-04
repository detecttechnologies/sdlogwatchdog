import pathlib
import subprocess as sp
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from shutil import copy


class CustomDevelop(develop):
    def run(self):
        develop.run(self)
        # custom stuff here
        copy("./sdlogwatchdog@.service","/etc/systemd/system")
        sp.call("systemctl daemon-reload".split())

class CustomInstall(install):
    def run(self):
        install.run(self)
        # custom stuff here
        copy("./sdlogwatchdog@.service","/etc/systemd/system")
        sp.call("systemctl daemon-reload".split())

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="sdlogwatchdog",
    version="0.0.1",
    description="Staleness-based watchdog for systemd services. Staleness is assessed based on recency of log messages",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/DetectTechnologies/sdlogwatchdog",
    author="Detect Technologies Pvt Ltd",
    author_email="support@detecttechnologies.com",
    license="MIT",
    packages=find_packages(),
    install_requires=["python-dateutil>=2"],
    cmdclass = {"develop":CustomDevelop, "install":CustomInstall}
)

