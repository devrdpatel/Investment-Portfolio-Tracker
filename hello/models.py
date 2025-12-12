from django.db import models

"""
Database Design

Investor(investorID, name, email, cashBalance)
Primary key: investorID

Stock(stockID, ticker, name, price)
Primary key: stockID

Portfolio(portfolioID, investor, name)
Primary key: portfolioID
Foreign key: investor fk to Investor

Transaction(transactionID, portfolio, stock, quantity, purchase_price, purchase_date, order_type)
Primary key: transactionID
Foreign keys: portfolio fk to Portfolio, stock fk to Stock
"""

class Investor(models.Model):
    """ Lists basic information for each investor """
    investorID = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    cashBalance = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name}: ({self.email}, ${self.cashBalance})"
    
class Stock(models.Model):
    """ Holds all relevant asset information for each supported stock """
    stockID = models.BigAutoField(primary_key=True)             # Primary Key
    ticker = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.ticker}: ({self.name}, ${self.price})"
    
class Portfolio(models.Model):
    """ An investor can have 0 or more portfolios of actively invested stocks """
    portfolioID = models.BigAutoField(primary_key=True)                 
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)    # Foreign Key
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}: ({self.investor.name})"
    
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    """ Each stock in an investor's portfolio will have a transaction history """
    transactionID = models.BigAutoField(primary_key=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, db_index=True)    # Foreign Key
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, db_index=True)            # Foreign Key
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(db_index=True)
    order_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)

    def __str__(self):
        return f"{self.order_type} {self.stock.ticker}: ({self.quantity} shares @ {abs(self.purchase_price)} on {self.purchase_date})"