"""Setup for pypi package"""

import os
import codecs
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = os.getenv("LIB_VERSION")
DESCRIPTION = "NUT Base Server"

# Setting up
setup(
    name="nut-base-server",
    version=VERSION,
    author="Patrick762",
    author_email="<pip-nut-base-server@hosting-rt.de>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/Patrick762/nut-base-server",
    packages=find_packages(),
    install_requires=[
        "asyncio",
        "nut-definitions==0.0.2",
    ],
    keywords=[],
    entry_points={},
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
)
