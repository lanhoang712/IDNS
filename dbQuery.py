import pandas as pd
import numpy as np
import sqlite3

def read_table(table_name, database_path='idns.db'):
  """Read an entire SQLite3 table and return as a pandas DataFrame."""
  conn = sqlite3.connect(database_path)
  c=conn.cursor()


  # Next line is potentially vulnerable to an SQL injection attack
  # Unlikely to be a problem, but ideally would replace
  data = pd.read_sql_query('SELECT * FROM ' + table_name, conn)
  # Replace None with NaN, to match how pandas reads from CSV
  data.fillna(value=np.nan, inplace=True)
  return data
def read_table_customer(customer_id, database_path='idns.db'):
  """Read an entire SQLite3 table and return as a pandas DataFrame."""
  conn = sqlite3.connect(database_path)
  c=conn.cursor()
  #t=('36248',)
  t=(customer_id,)
  print customer_id
  #table=table_name
  #import pdb
  #pdb.set_trace()
  c.execute("SELECT * FROM companies WHERE oprano=?",t)
  #c.execute('SELECT * FROM companies WHERE compno=36248')

  data=c.fetchall()
  c.close()
  return data

def read_table_pastpurchase(customer_id, database_path='idns.db'):
  """Read an entire SQLite3 table and return as a pandas DataFrame."""
  conn = sqlite3.connect(database_path)
  c=conn.cursor()
  t=(customer_id,)
  c.execute("SELECT prodref, inv_productdesc, inv_price, inv_orderqty FROM sales WHERE inv_account=?",t)
  data=c.fetchall()
  c.close()

  return data
def findItems(item, table='sales',database_path='idns.db'):
  conn = sqlite3.connect(database_path)
  c=conn.cursor()
  #c.execute("SELECT invoiceno FROM sales WHERE instr(inv_productdesc, ?) > 0",item)
  c.execute( "SELECT invoiceno, prodref FROM sales WHERE inv_productdesc like ?", ('%'+item+'%', ))
  alldat=c.fetchall()
  invoice=[unicode(row[0]) for row in alldat]
  prodref=[unicode(row[1]) for row in alldat]
  c.close()
  print "Found " +str(len(invoice))+ " related orders"
  print str(len(prodref)) +" related products"
  if len(invoice)>0 and len(prodref)>0 :
    print 'Calculate correlation'

    sales = read_table('Sales')
    companies = read_table('Companies')
    companies_cut = companies[companies.oprano.str.len() > 0].drop_duplicates('oprano').set_index('oprano')

    #==================================================================================
    #create a list of highly correlated items based on past order:
    #------------
    #Clean data
    sales = sales[sales.inv_account.isin(companies_cut.index)]
    sales=sales[
      (sales.inv_linevalue > 0) &
      (sales.inv_price > 0) &
      (~sales.inv_productdesc.str.lower().str.contains('bacs').fillna(False)) &
      (~sales.inv_extendeddesc.str.lower().str.contains('bacs').fillna(False)) &
      (~sales.inv_productdesc.str.lower().str.contains('credit').fillna(False)) &
      (~sales.inv_productdesc.str.lower().str.contains('delivery').fillna(False)) &
      (~sales.inv_extendeddesc.str.lower().str.contains('credit').fillna(False))
       ]
    
    #Score(X, Y) =  (Total Customers who purchased X and Y / Total Customers who purchased X) / 
    #       (Total Customers who did not purchase X but got Y / Total Customers who did not purchase X)
    #------------------
    # 1) Customer who purchased X:
    cust_X = sales[sales.invoiceno.isin(invoice)].drop_duplicates('inv_account').inv_account.count()
    print 'Customer who purchased X is ' 
    print cust_X
     
    #Customer who did not purchase X: 
    cust_notX=sales[~sales.invoiceno.isin(invoice)].drop_duplicates('inv_account').inv_account.count()

    print cust_notX

    #Customer did not purchase X but got Y:
    # First list items Y
    listprodY=sales[sales.invoiceno.isin(invoice) & 
    ~sales.prodref.isin(prodref)].drop_duplicates('prodref').prodref
    #Customer who purchased prod Y
    cust_Y=sales[sales.prodref.isin(listprodY) & 
    ~sales.invoiceno.isin(invoice)].groupby('prodref', as_index=False).inv_account.count()

    #Customer who purchased X and Y
    cust_XY=sales[sales.prodref.isin(listprodY) & sales.invoiceno.isin(invoice)].groupby('prodref', as_index=False).inv_account.count()
    cust_XY_dat=sales[sales.prodref.isin(listprodY) & sales.invoiceno.isin(invoice)].groupby(['prodref','inv_productdesc'], 
      as_index=False).inv_account.count()
    #Merge all relevant into a database
    All=cust_Y.merge(cust_XY_dat, how='inner', on='prodref')
       

    #Score_XY
    All['Score_XY']=(All.inv_account_y/cust_X)/(All.inv_account_x/cust_notX)
    All=All.sort_values(by='Score_XY', ascending=False)

    #Get the 15 highest ranking products
    extract_dat = All[['prodref','inv_productdesc','Score_XY']]
    Rec=extract_dat[:15]

    #import pdb
    #pdb.set_trace()

    return extract_dat

    
  

if __name__ == "__main__":
  #Unit test
  a=findItems('black print cartridge')