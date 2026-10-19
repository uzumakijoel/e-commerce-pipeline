from database import db_connection
from extract import extract
from transform import tranform
from mysql.connector import Error 
from functools import wraps
import pandas as pd
import sys
import logging

log=logging.getLogger(__name__)


def sql(database,localhost,user,password):
    #The results of extract() processing
    products,users,carts=extract()
    #the results of transform() processing
    product_lst,user_lst,cmd_lst,cmd_itms_lst,prdt_error,usr_error,cmd_error=tranform(products,users,carts)

    with db_connection(database,localhost,user,password) as conn:
        # The treatment is carried out if conn is not none
        if conn is not None:
            cur=conn.cursor()
            try:
                statut="success"
                description=None
                def the_try_except(func):
                    @wraps(func)
                    def wrapper(conn,table,table_id,*args, **kwargs):
                        cur=conn.cursor()
                        try:
                            result= func(conn,table,table_id,*args,**kwargs)
                            if table_id:
                                sql="""
                                    INSERT INTO data_quality_issues(table_name,id_record)
                                    VALUES (%s,%s)
                                    ON DUPLICATE KEY UPDATE
                                        id_record=id_record
                                """
                                cur.executemany(sql,[(table,id_) for id_ in table_id])                    
                            conn.commit()
                            return result
                        except Error as e_sql:
                            conn.rollback()
                            raise
                    return wrapper

                @the_try_except
                def func_user(conn,table,table_id,list):  
                    cur=conn.cursor()     
                    sql="""
                        INSERT INTO customers(id,frst_name,lst_name,email,birthdate)
                        VALUES (%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE
                            frst_name= VALUES(frst_name),
                            lst_name= VALUES(lst_name),
                            email= VALUES(email),
                            birthdate= VALUES(birthdate)
                    """
                    cur.executemany(sql,list)

                @the_try_except
                def func_prod(conn,table,table_id,list):
                    cur=conn.cursor()
                    sql="""
                        INSERT INTO products(id,title,price,category,rating)
                        VALUES (%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE
                            title= VALUES(title),
                            price= VALUES(price),
                            category= VALUES(category),
                            rating= VALUES(rating)
                    """
                    cur.executemany(sql,list)

                @the_try_except
                def func_order(conn,table,table_id,list):
                    cur=conn.cursor()
                    sql="""
                        INSERT INTO orders(id,user_id,total,disctotal,totalprod,qteprod)
                        VALUES (%s,%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE
                            user_id= VALUES(user_id),
                            total= VALUES(total),
                            disctotal= VALUES(disctotal),
                            totalprod= VALUES(totalprod),
                            qteprod= VALUES(qteprod)
                    """
                    cur.executemany(sql,list)  

                @the_try_except
                def func_order_items(conn,table,table_id,list):
                    cur=conn.cursor()
                    sql="""
                        INSERT INTO orders_items(order_id,prod_id,qte,price,disctotal)
                        VALUES (%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE
                            qte= VALUES(qte),
                            price= VALUES(price),
                            disctotal= VALUES(disctotal)
                    """
                    cur.executemany(sql,list)

                func_user(conn,"customers",usr_error,user_lst)
                func_prod(conn,"products",prdt_error,product_lst)
                func_order(conn,"orders",cmd_error,cmd_lst)
                func_order_items(conn,"orders_items",None,cmd_itms_lst)

            except Exception as e:
                log.warning(type(e).__name__)
                description=f"{type(e).__name__}:{e}"
                statut="Failed"
                print(e)
                log.warning("End of the pipeline")
                sys.exit(1)
            finally:
                cur.execute("""
                    SELECT COUNT(*) FROM customers
                """)
                utili=cur.fetchone()[0]
                cur.execute("""
                    SELECT COUNT(*) FROM products
                """)
                products=cur.fetchone()[0]
                cur.execute("""
                    SELECT COUNT(*) FROM orders
                """)
                orders=cur.fetchone()[0]
                cur.execute("""
                    SELECT COUNT(*) FROM orders_items
                """)
                orders_items=cur.fetchone()[0]
                sql="""
                    INSERT INTO pipeline_run(statut,users,products,orders,orders_items,description)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """
                cur.execute(sql,(statut,utili,products,orders,orders_items,description))
                conn.commit()


            #============= QUESTIONS ==============

            cur.execute("""
                SELECT oi.prod_id,p.title,COUNT(*) AS nb
                FROM orders_items oi
                INNER JOIN products p
                ON oi.prod_id = p.id
                GROUP BY oi.prod_id
                ORDER BY COUNT(*) DESC
                LIMIT 10;
            """)
            best_10_prod=pd.DataFrame(
                cur.fetchall(),
                columns=[desc[0] for desc in cur.description]
            )

            cur.execute("""
                SELECT p.category,SUM(oi.disctotal) as total
                FROM orders_items oi
                INNER JOIN products p
                ON oi.prod_id = p.id
                GROUP BY p.category
                ORDER BY SUM(oi.disctotal) DESC
                LIMIT 10;
            """)
            best_10_cat=pd.DataFrame(
                cur.fetchall(),
                columns=[desc[0] for desc in cur.description]
            )
            cur.execute("""
                SELECT o.user_id, c.frst_name, SUM(o.disctotal) as total
                FROM orders o
                INNER JOIN customers c
                ON o.user_id = c.id 
                GROUP BY o.user_id
                ORDER BY SUM(o.disctotal) DESC
                LIMIT 10;
            """)
            best_10_usr=pd.DataFrame(
                cur.fetchall(),
                columns=[desc[0] for desc in cur.description]
            )
            cur.execute("""
                SELECT SUM(total) as total_av,SUM(disctotal) as total_ap, AVG(disctotal) as val_moy
                FROM orders;
            """)
            tot_av_ap=pd.Series(
                cur.fetchone(),
                index=[desc[0] for desc in cur.description]
            )
            cur.execute("""
                SELECT oi.prod_id, p.rating, COUNT(oi.prod_id) as nb_vente
                FROM orders_items oi
                INNER JOIN products p
                ON oi.prod_id = p.id 
                WHERE p.rating >= 4.5
                GROUP BY oi.prod_id
                ORDER BY nb_vente ASC
                LIMIT 10;
            """)
            fav=pd.DataFrame(
                cur.fetchall(),
                columns=[desc[0] for desc in cur.description]
            )
            cur.execute("""
                SELECT id, description, date_add
                FROM pipeline_run
                WHERE statut = "Failed";
            """)
            failed=pd.DataFrame(
                cur.fetchall(),
                columns=[desc[0] for desc in cur.description]
            )
            cur.execute("""
                SELECT id,
                users - COALESCE(LAG(users) OVER (ORDER BY id),0) as users,
                products - COALESCE(LAG(products) OVER (ORDER BY id),0) as products,
                orders - COALESCE(LAG(orders) OVER (ORDER BY id),0) as orders,
                orders_items - COALESCE(LAG(orders_items) OVER (ORDER BY id),0) as orders_items
                FROM pipeline_run
                WHERE statut = "success";
            """)
            sucess=pd.DataFrame(
                cur.fetchall(),
                columns=[desc[0] for desc in cur.description]
            )
            cur.execute("""
                SELECT *
                FROM pipeline_run;
            """)
            jo=pd.DataFrame(
                cur.fetchall(),
                columns=[desc[0] for desc in cur.description]
            )
            #============ TEST ==========
            print(best_10_prod.head(10))
            print(best_10_cat.head(10))
            print(best_10_usr.head(10))
            print(fav.head(10))
            print(failed.head(10))
            print(sucess.head(10))
            print(tot_av_ap)
            print(jo)

