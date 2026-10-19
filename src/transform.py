
import pandas as pd

def tranform(products,users,carts):
    product= pd.DataFrame(products)
    user=pd.DataFrame(users)
    cmd=pd.DataFrame(carts)

    #rename some of columns
    cmd= cmd.rename(columns={"id":"card_id","total":"TOT","discountedTotal":"DiscTot"})

    #Create a df items that will contain card_id with each line of products that corresponds to it
    items=cmd[["card_id","products"]].explode("products").reset_index(drop=True)
    #transform each element of products as a pandas series
    prod=pd.json_normalize(
        items.pop("products")
    ).rename(columns={"id":"prod_id"})
    #Concatenate items(at left) and prod(at right)
    items=pd.concat([items,prod],axis=1)

    #Oders df by id (ascending)
    product=product.sort_values(by="id")
    user=user.sort_values(by="id")
    cmd=cmd.sort_values(by="card_id")
    items=items.sort_values(by="prod_id")
    
    print("All null")
    print(f"products: \n{product.isnull().sum()}")
    print(f"users: \n{user.isnull().sum()}")
    print(f"orders: \n{cmd.isnull().sum()}")

    print("\n The negative and zeros number")
    print(f"product price: {(product["price"]<=0).sum()}")
    print(f"product stock: {(product["stock"]<0).sum()}")
    print(f"user age: {(user["age"]<=0).sum()}")
    print(f"total price order: {(cmd["TOT"]<=0).sum()}")
    print(f"discounted total: {(cmd["DiscTot"]<=0).sum()}")
    print(f"total products of an order: {(cmd["totalProducts"]<=0).sum()}")
    print(f"total quantity of an order: {(cmd["totalQuantity"]<=0).sum()}")

    print("\n relation order and user")
    print(f"order user id not in user id: {(~cmd["userId"].isin(user["id"])).sum()}")
    cmd=cmd[cmd["userId"].isin(user["id"])]
    print(f"oder products id not in user id: {(~items["prod_id"].isin(product["id"])).sum()}")
    items=items[items["prod_id"].isin(product["id"])]

    #Calculate these elements after processing
    cmd["totalProducts"]=cmd["card_id"].map(items.groupby("card_id").size())
    cmd["totalQuantity"]=cmd["card_id"].map(items.groupby("card_id")["quantity"].sum())
    cmd["TOT"]=cmd["card_id"].map(items.groupby("card_id")["total"].sum())
    cmd["DiscTot"]=cmd["card_id"].map(items.groupby("card_id")["discountedTotal"].sum())

    # record anomalies that can create problems
    prdt_error=product[(product[["title","price","category","rating"]].isnull().any(axis=1))|(product["price"]<=0)|(product["stock"]<0)]
    usr_error=user[user["email"].isnull()]
    cmd_error=cmd[(cmd[["TOT","DiscTot","totalProducts","totalQuantity"]]<=0).any(axis=1)|(cmd[["TOT","DiscTot","totalProducts","totalQuantity"]].isnull().any(axis=1))]   

    # Transform every df or series in list
    user_lst=list(user[["id","firstName","lastName","email","birthDate"]].itertuples(index=False,name=None))
    product_lst=list(product[["id","title","price","category","rating"]].itertuples(index=False,name=None))
    cmd_lst=list(cmd[["card_id","userId","TOT","DiscTot","totalProducts","totalQuantity"]].itertuples(index=False,name=None))
    items_list=list(items[["card_id","prod_id","quantity","price","discountedTotal"]].itertuples(index=False,name=None ))
    prdt_error=list(prdt_error["id"])
    usr_error=list(usr_error["id"])
    cmd_error=list(cmd_error["card_id"])

    return product_lst,user_lst,cmd_lst,items_list,prdt_error,usr_error,cmd_error