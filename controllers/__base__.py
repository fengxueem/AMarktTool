from abc import ABC

class Mediator(ABC):
    """
    中介者用于不同 controller 之间进行通信
    """

    def notify(self, sender: object, event: str, msg: str) -> None:
        pass

class BaseController:
    """
    所有 controller 需要继承的基类，功能点如下
    1. 每种 controller 都拥有一个中介者成员变量
    """
    def __init__(self, mediator: Mediator = None, id: str = None) -> None:
        self._mediator = mediator

    @property
    def mediator(self) -> Mediator:
        return self._mediator

    @mediator.setter
    def mediator(self, mediator: Mediator) -> None:
        self._mediator = mediator
