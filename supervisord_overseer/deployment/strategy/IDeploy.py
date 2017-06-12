"""
Interface for deployment strategies
"""

from abc import ABCMeta, abstractmethod


class IDeploy(metaclass=ABCMeta):
    @abstractmethod
    def pre_deploy(self):
        pass

    @abstractmethod
    def deploy(self):
        pass

    @abstractmethod
    def post_deploy(self):
        pass
