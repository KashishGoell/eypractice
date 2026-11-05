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
    'Prices':[90000,100000,200000,7000,3000,200],
    'Stock':[20,12,8,50,35,100]
}

df=pd.DataFrame(products)

purchase = []
def buy_product(name,id,quantity,df):
    prod=df[df["id"]==id]
    if prod.empty:
        raise ValueError("Product ID was not found.")
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")
    if quantity > prod["Stock"].iloc[0]:
        raise ValueError("Not enough stock available.")

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
    df.loc[prod.index[0], "Stock"] -= quantity
    print(name, pname)
def show_purchases():
    return pd.DataFrame(purchase)

users=int(input("Enter users:"))

for i in range(users):
   name=input("Enter name of User: ")
   prodid= int(input("Enter prod id: "))
   quantity= int(input("Enter quantity for the product: "))

   buy_product(name , prodid, quantity, df)

sales= show_purchases()
print(sales)
print("\nRemaining inventory:")
print(df[["Product", "Stock"]].to_string(index=False))

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