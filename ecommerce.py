import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns

products={
    'id':[1,2,3,4,5,6],
    'category':['Electronics','Electronics','Electronics',
                'Makeup','Makeup','Makeup'],
    
    'Product':['Mobile Phones','Television','Laptops',
               'Lipstick','Foundation','Nail Paints'],
    'Prices':[90000,100000,200000,7000,3000,200]
}

df=pd.DataFrame(products)

purchase = []
def buy_product(name,id,quantity,df):
    name = name.strip()
    if not name:
        raise ValueError("Customer name cannot be empty.")
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    prod=df[df["id"]==id]
    if prod.empty:
        raise ValueError("Product ID was not found.")
    pname=prod["Product"].iloc[0]
    price=prod["Prices"].iloc[0]
    category = prod["category"].iloc[0]

    purchase.append({
        "User":name,
        "Product":pname,
        "Category": category,
        "Quantity":quantity,
        "Amount":price*quantity
    })
    print(name, pname)
def show_purchases():
    return pd.DataFrame(purchase)

try:
   users=int(input("Enter users:"))
   if users < 0:
      raise ValueError("Number of users cannot be negative.")
except ValueError as error:
   raise SystemExit(f"Invalid number of users: {error}") from error

for i in range(users):
   try:
      name=input("Enter name of User: ")
      prodid= int(input("Enter prod id: "))
      quantity= int(input("Enter quantity for the product: "))
      buy_product(name , prodid, quantity, df)
   except ValueError as error:
      print(f"Purchase not recorded: {error}")

sales= show_purchases()
print(sales)

demand= sales.groupby("Product")["Quantity"].sum()
print(demand)

revenue=np.sum(sales["Amount"])
sns.barplot(
    x=demand.index,
    y=demand.values
)

plt.xlabel("Products")
plt.ylabel("Quantity sold")
plt.tight_layout()
plt.show()