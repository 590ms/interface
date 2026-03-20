from app import POSApp
from screens.pos import POSMixin
from screens.stock import StockMixin
from screens.clients import ClientsMixin
from screens.loyalty import LoyaltyMixin
from screens.history import HistoryMixin



class POSSystem(POSMixin, StockMixin, ClientsMixin, LoyaltyMixin, HistoryMixin, POSApp):

    pass
