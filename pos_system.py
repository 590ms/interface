from app import POSApp
from screens.pos import POSMixin
from screens.stock import StockMixin
from screens.clients import ClientsMixin
from screens.loyalty import LoyaltyMixin


class POSSystem(POSMixin, StockMixin, ClientsMixin, LoyaltyMixin, POSApp):

    pass
