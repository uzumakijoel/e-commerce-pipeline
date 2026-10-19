import requests
import sys
import time
import logging

log=logging.getLogger(__name__)

def extract():
    #Initialization of data variables
    products=[]

    max_tentative=5
    url=["https://dummyjson.com/products","https://dummyjson.com/users","https://dummyjson.com/carts"]

        
    def extraction(url,key):
        products=[]   
        skip=0
        limit=30
        #Check for duplicated line or id
        id_unique= set()
        while True:
            #try url connection
            response=requests.get(url, params={
                "skip":skip,
                "limit":limit
            } ,timeout=10)
            response.raise_for_status()
            #Receive data in json format
            donnee=response.json()
            #if products value don't exist raise valueError
            if key not in donnee or not donnee[key]:
                raise ValueError(
                    f"missing {key} data"
                )
                    
            #for every line in products
            for element in donnee[key]:
                #if id is in id_unique
                if element["id"] in id_unique:
                    continue
                    #ignore this line and go to the next
                    
                #now add the new id in in_unique
                id_unique.add(element["id"])
                #and add the line in products variable
                products.append(element)

            skip+=limit
            if skip>=donnee["total"]:
                #check total of data, the skip and the limit
                print(f"url {key} total: {donnee["total"]}, skip: {donnee["skip"]}, limit: {donnee["limit"]}")
                print(f"After duplicate processing: {len(products)}")
                print(f"successful {key} extraction\n")
                return products
            
    #For 5(max_tentative) attempts
    for tentative in range(1, max_tentative+1):
        try:
            products=extraction(url[0],"products")
            users=extraction(url[1],"users")
            carts=extraction(url[2],"carts")
            break

        except (ValueError, requests.exceptions.RequestException) as e:
            print(f"URL processing error: {e}")
            print(f"Number of attempts: {tentative}/{max_tentative}")
            products=[]
            users=[]
            carts=[]
            if tentative == max_tentative:
                log.error(type(e).__name__)
                log.warning("Cancellation of extraction")
                log.warning("End of the pipeline")
                sys.exit(1)
            time.sleep(2**tentative)


    return products,users,carts