import re
import requests


def read_packages(pypi_server: str):
    res = requests.get('{}/simple/'.format(pypi_server))

    package_names = re.findall(r'<a href=\"[a-zA-Z-/]+\">([a-zA-Z-]+)</a>', res.text)

    packages = []

    for package_name in package_names:
        res = requests.get('{}/simple/{}'.format(pypi_server, package_name))
        versions = re.findall(r'<a href=\"\/packages\/[a-zA-Z-/]+([0-9]+\.[0-9]+\.[0-9]+)\.tar\.gz', res.text)
        package = {package_name: versions}
        packages.append(package)