from django.db.models import Avg, Sum
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from hello.models import Transaction, Portfolio, Stock
from hello.forms import TransactionForm

# Create your views here.
def main_page(request):
    return render(request, "index.html")

def transaction_report(request):
    portfolios = Portfolio.objects.all()
    stocks = Stock.objects.all()

    query = Transaction.objects.all()

    # Protects against SQL Injections by using the ORM methods for parameterized queries
    # Instead of using raw SQL queries like:
    # sql = f"SELECT * FROM Stock WHERE ticker = '{request.GET['ticker']}'"
    # stocks = Stock.objects.raw(sql)
    
    selected_portfolio = request.GET.get("portfolio")
    selected_stock = request.GET.get("stock")
    selected_order_type = request.GET.get("order_type")
    start = request.GET.get("start")
    end = request.GET.get("end")

    if selected_portfolio and selected_portfolio != "":
        query = query.filter(portfolio_id=selected_portfolio)

    if selected_stock and selected_stock != "":
        query = query.filter(stock_id=selected_stock)

    if selected_order_type and selected_order_type != "":
        query = query.filter(order_type = selected_order_type)

    if start:
        query = query.filter(purchase_date__gte=start)

    if end:
        query = query.filter(purchase_date__lte=end)

    stats = query.aggregate(
        avg_qty=Sum("quantity"),
        avg_price=Avg("purchase_price")
    )

    context = {
        "transactions": query,
        "portfolios": portfolios,
        "stocks": stocks,
        "stats": stats,
        "selected_portfolio": selected_portfolio,
        "selected_stock": selected_stock,
        "selected_order_type": selected_order_type,
        "start": start,
        "end": end
    }
    return render(request, "transaction/report.html", context)

def transaction_list(request):
    transaction = Transaction.objects.select_related("portfolio", "stock").all()
    return render(request, 'transaction/list.html', {'transaction': transaction})

# def transaction_create(request):
#     if request.method == 'POST':
#         form = TransactionForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('transaction_list')
#     else:
#         form = TransactionForm()
#     return render(request, 'transaction/form.html', {'form': form, 'action': 'Add'})

def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():

            # Atomic Transaction, either all or nothing
            with transaction.atomic():
                # Save transaction first
                transaction_obj = form.save(commit=False)
                portfolio = transaction_obj.portfolio
                investor = portfolio.investor

                print(f"Before adding transaction:\n\n {str(investor)}\n\n")

                # Update investor balance (Allows negative balance to imitate margin investing)
                if transaction_obj.order_type == "BUY":
                    investor.cashBalance -= (transaction_obj.quantity * transaction_obj.purchase_price)
                elif transaction_obj.order_type == "SELL":
                    investor.cashBalance += (transaction_obj.quantity * transaction_obj.purchase_price)

                print(f"After adding transaction:\n\n {str(investor)}\n\n")


                investor.save()
                transaction_obj.save()

            return redirect('transaction_list')

    else:
        form = TransactionForm()

    return render(request, 'transaction/form.html', {'form': form, 'action': 'Add'})

# def transaction_edit(request, id):
#     transaction = get_object_or_404(Transaction, transactionID=id)
#     form = TransactionForm(request.POST or None, instance=transaction)
#     if request.method == 'POST' and form.is_valid():
#         form.save()
#         return redirect('transaction_list')
#     return render(request, 'transaction/form.html', {'form': form, 'action': 'Edit'})
def transaction_edit(request, id):
    transaction_obj = get_object_or_404(Transaction, transactionID=id)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction_obj)

        if form.is_valid():
            with transaction.atomic():
                old_transaction = Transaction.objects.get(transactionID=id)
                portfolio = old_transaction.portfolio
                investor = portfolio.investor

                # Remove effect of old transaction
                old_value = old_transaction.quantity * old_transaction.purchase_price

                if old_transaction.order_type == 'BUY':
                    # Add back amount
                    investor.cashBalance += old_value
                elif old_transaction.order_type == 'SELL':
                    # Remove amount
                    investor.cashBalance -= old_value

                # Add effect of new transaction
                new_transaction = form.save(commit=False)
                new_value = new_transaction.quantity * new_transaction.purchase_price

                if new_transaction.order_type == "BUY":
                    investor.cashBalance -= new_value
                elif new_transaction.order_type == "SELL":
                    investor.cashBalance += new_value

                investor.save()
                new_transaction.save()

            return redirect('transaction_list')

    else:
        form = TransactionForm(instance=transaction_obj)

    return render(request, 'transaction/form.html', {
        'form': form,
        'action': 'Edit',
    })

# def transaction_delete(request, id):
#     transaction = get_object_or_404(Transaction, transactionID=id)
#     if request.method == 'POST':
#         transaction.delete()
#         return redirect('transaction_list')
#     return render(request, 'transaction/confirm_delete.html', {'transaction': transaction})
def transaction_delete(request, id):
    old_transaction = get_object_or_404(Transaction, transactionID=id)
    if request.method == 'POST':

        # Atomic Transaction, either all or nothing
        with transaction.atomic():
            portfolio = old_transaction.portfolio
            investor = portfolio.investor

            print(f"Before removing transaction:\n\n {str(investor)}\n\n")


            # Reverse Buy or Sell order effect on Investor cash balance
            if old_transaction.order_type == "BUY":
                investor.cashBalance += (old_transaction.quantity * old_transaction.purchase_price)
            elif old_transaction.order_type == "SELL":
                investor.cashBalance -= (old_transaction.quantity * old_transaction.purchase_price)

            print(f"After removing transaction:\n\n {str(investor)}\n\n")

            investor.save()
            old_transaction.delete()

        return redirect('transaction_list')

    return render(request, 'transaction/confirm_delete.html', {'transaction': old_transaction})
