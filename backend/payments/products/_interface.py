from abc import abstractmethod

from utils import BaseModel


class ProductInterface(BaseModel):
    @abstractmethod
    def handle_successful_payment(self): ...
