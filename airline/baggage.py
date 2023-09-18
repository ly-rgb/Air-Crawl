from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import List, Set, Any, TypeVar, Tuple, Optional

from robot.model import BaggageMessageDO, AddOnResult

T = TypeVar('T')


class BaggageSelectException(Exception):
    pass


@dataclass
class Baggage:
    """
    :cvar weight 重量(KG)
    :cvar price 价格(CNY)
    :cvar basic 自定义数据
    """
    weight: int
    price: float
    basic: T = field(default=None)
    base_price: Optional[float] = field(default=None)
    base_currency: Optional[str] = field(default=None)
    type: Optional[int] = field(default=11)


@dataclass
class SelectCase(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def get_baggage(baggages_selector: 'BaggageSelector') -> Tuple[Baggage, bool]:
        pass


class SelectCaseWithPreciseWeight(SelectCase):
    """
    选择等于当前任务行李额的行李，
    如果没有则抛出 BaggageSelectException
    """

    @staticmethod
    def get_baggage(baggages_selector: 'BaggageSelector') -> Tuple[Baggage, bool]:
        baggages = list(filter(lambda x: x.weight == baggages_selector.target_baggage.baggageWeight, baggages_selector.baggages))
        if baggages:
            return baggages[0], True
        else:
            raise BaggageSelectException(f"{baggages_selector.target_baggage.baggageWeight}KG 无匹配行李额")


class SelectCaseWithUpWeight(SelectCase):
    """
    选择大于等于当前任务行李额的行李，
    如果没有则选当前最高档
    """

    @staticmethod
    def get_baggage(baggages_selector: 'BaggageSelector') -> Tuple[Baggage, bool]:
        baggages = list(filter(lambda x: x.weight == baggages_selector.target_baggage.baggageWeight, baggages_selector.baggages))
        if baggages:
            return baggages[0], True

        baggages = list(filter(lambda x: x.weight >= baggages_selector.target_baggage.baggageWeight, baggages_selector.baggages))
        if baggages:
            return baggages[0], baggages[0].weight == baggages_selector.target_baggage.baggageWeight
        else:
            return baggages_selector.baggages[-1], False


class SelectCaseWithLowerWeight(SelectCase):
    """
    选择小于等于当前任务行李额中最大行李额,
    如果没有则选中最低重量行李
    """

    @staticmethod
    def get_baggage(baggages_selector: 'BaggageSelector') -> Tuple[Baggage, bool]:
        baggages = list(
            filter(lambda x: x.weight == baggages_selector.target_baggage.baggageWeight, baggages_selector.baggages))
        if baggages:
            return baggages[0], True

        baggages = list(filter(lambda x: x.weight <= baggages_selector.target_baggage.baggageWeight, baggages_selector.baggages))
        if baggages:
            return baggages[-1], baggages[-1].weight == baggages_selector.target_baggage.baggageWeight
        else:
            return baggages_selector.baggages[0], baggages_selector.baggages[0].weight >= baggages_selector.target_baggage.baggageWeight


class SelectCaseWithLikeWeight(SelectCase):
    """
    最相近的行李公斤
    """

    @staticmethod
    def get_baggage(baggages_selector: 'BaggageSelector') -> Tuple[Baggage, bool]:
        select_bag = min(baggages_selector.baggages, key=lambda x: (baggages_selector.target_baggage.baggageWeight - x.weight) ** 2)
        return select_bag, False


class SelectCaseWithPriceUpBag(SelectCase):
    """
    选择目标金额内，优先能满足行李额的，如果无法满足行李额则选择金额内最高档,
    如果目标金额内无法购买任何行李则选中最相近的行李公斤
    """

    @staticmethod
    def get_baggage(baggages_selector: 'BaggageSelector') -> Tuple[Baggage, bool]:
        baggages = list(filter(lambda x: x.weight == baggages_selector.target_baggage.baggageWeight, baggages_selector.baggages))
        if baggages:
            return baggages[0], True

        baggages = list(filter(lambda x: baggages_selector.target_baggage.baggagePirce >= x.price, baggages_selector.baggages))
        if not baggages:
            return SelectCaseWithLikeWeight.get_baggage(baggages_selector)
        else:
            ge_baggages = list(filter(lambda x: x.weight >= baggages_selector.target_baggage.baggageWeight, baggages))
            if ge_baggages:
                select_bag = ge_baggages[0]
            else:
                select_bag = baggages[-1]
            return select_bag, select_bag.weight >= baggages_selector.target_baggage.baggageWeight


class SelectCaseWithPriceLowerBag(SelectCase):
    """
    选择目标价格内，小于等于目标重量中最大行李额，无小于等于目标重量选择最低重量行李
    如果目标金额内无法购买任何行李则选中最相近的行李公斤
    """

    @staticmethod
    def get_baggage(baggages_selector: 'BaggageSelector') -> Tuple[Baggage, bool]:
        baggages = list(
            filter(lambda x: x.weight == baggages_selector.target_baggage.baggageWeight, baggages_selector.baggages))
        if baggages:
            return baggages[0], True

        baggages = list(filter(lambda x: baggages_selector.target_baggage.baggagePirce >= x.price, baggages_selector.baggages))
        if not baggages:
            return SelectCaseWithLikeWeight.get_baggage(baggages_selector)
        else:
            le_tag_weigh_baggages = list(filter(lambda x: x.weight <= baggages_selector.target_baggage.baggageWeight, baggages))
            if le_tag_weigh_baggages:
                return le_tag_weigh_baggages[-1], le_tag_weigh_baggages[-1].weight == baggages_selector.target_baggage.baggageWeight
            else:
                return baggages[0], baggages[0].weight == baggages_selector.target_baggage.baggageWeight


@dataclass
class BaggageSelector:
    baggages: List[Baggage]
    target_baggage: BaggageMessageDO
    order_code: str
    airline: str
    task_tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.baggages = list(sorted(self.baggages, key=lambda x: x.weight))

    def matching(self, ota_names: List[str], tags: List[str]):
        ota_match = False
        for ota_name in ota_names:
            if ota_name in self.order_code:
                ota_match = True
        tag_match = True
        for tag in tags:
            if tag not in self.task_tags:
                tag_match = False
        return ota_match and tag_match

    def get_baggage(self) -> Tuple[Baggage, bool]:
        """
        BaggageOrder 行李订单
        20KGBaggage 行李套餐
        """
        if self.matching(['DRCP', 'CTR'], ['20KGBaggage']):
            return SelectCaseWithUpWeight.get_baggage(self)
        elif self.matching(['DRCP', 'CTR'], ['BaggageOrder']):
            return SelectCaseWithPriceUpBag.get_baggage(self)
        elif self.matching(['DRCP', 'CTR'], ['BaggageOrder', '20KGBaggage']):
            return SelectCaseWithPriceLowerBag.get_baggage(self)
        else:
            return SelectCaseWithPreciseWeight.get_baggage(self)

