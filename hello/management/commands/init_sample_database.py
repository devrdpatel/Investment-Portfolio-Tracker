from django.core.management.base import BaseCommand
from hello.models import Investor, Stock, Portfolio, Transaction
from django.utils import timezone

class Command(BaseCommand):
    help = 'Initial database with sample data'

    def handle(self, *args, **kwargs):
        # Clear old data
        # Investor.objects.all().delete()
        # Stock.objects.all().delete()
        # Portfolio.objects.all().delete()
        # Holding.objects.all().delete()

        # Create investors
        alice = Investor.objects.create(name='Alice Johnson', email='alice@example.com', cashBalance=50000)
        bob = Investor.objects.create(name='Bob Smith', email='bob@example.com', cashBalance=75000)

        # Create stocks
        aapl = Stock.objects.create(ticker='AAPL', name='Apple', price=180.50)
        msft = Stock.objects.create(ticker='MSFT', name='Microsoft', price=350.75)
        tsla = Stock.objects.create(ticker='TSLA', name='Tesla', price=220.10)
        meta = Stock.objects.create(ticker='META', name='Meta Platforms', price=690.15)
        netflix = Stock.objects.create(ticker='NFLX', name='Netflix', price=1190.93)

        # Create portfolios
        p1 = Portfolio.objects.create(investor=alice, name='Tech Portfolio')
        p2 = Portfolio.objects.create(investor=bob, name='Growth Portfolio')

        # Create holdings
        Transaction.objects.create(portfolio=p1, stock=aapl, quantity=20, purchase_price=160, purchase_date=timezone.now(), order_type='BUY')
        Transaction.objects.create(portfolio=p1, stock=msft, quantity=15, purchase_price=310, purchase_date=timezone.now(), order_type='BUY')
        Transaction.objects.create(portfolio=p2, stock=tsla, quantity=10, purchase_price=200, purchase_date=timezone.now(), order_type='BUY')

        self.stdout.write(self.style.SUCCESS('Sample data added!'))
