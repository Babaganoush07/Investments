from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from PIL import ImageTk, Image
import warnings
warnings.simplefilter(action='ignore', category=RuntimeWarning)
import sqlite3, pandas, os


#Build the window
main = Tk()
main.title('Investments')
MyLeftPos = (main.winfo_screenwidth() - 1200) / 2
MyTopPos = (main.winfo_screenheight() - 820) / 2 - 20
main.geometry( "%dx%d+%d+%d" % (1200,820, MyLeftPos, MyTopPos))
main.config(bg='#0B5A81')
main.resizable(False,False)
main.iconbitmap('C:/Users/First Last/Python/Python39-32/Project_Images/lampcar.ico')

main_menu = Menu(main)
main.config(menu = main_menu)
file_menu = Menu(main_menu, tearoff = 0)
main_menu.add_cascade(label = 'File', menu = file_menu)

#Create a database or connect to one that exists
con = sqlite3.connect('investments.db')
cur = con.cursor()
# Create the Stocks Table
cur.execute('''CREATE TABLE IF NOT EXISTS stock_trades(
                    date TEXT, 
                    event TEXT,
                    name TEXT,
                    cost REAL,
                    shares REAL,
                    price REAL)''')
#Create the Crypto Table
cur.execute('''CREATE TABLE IF NOT EXISTS crypto_trades(
                    date TEXT, 
                    event TEXT,
                    name TEXT,
                    cost REAL,
                    coins REAL,
                    price REAL)''')
con.commit()
con.close()

def query_investments():
    stock_header.config(state='normal')
    crypto_header.config(state='normal')
    stock_header.delete(0, END)
    crypto_header.delete(0, END)
    con = sqlite3.connect('investments.db')
    cur = con.cursor()
    #Get Data For Trades TreeView
    cur.execute("SELECT rowid,* FROM stock_trades ORDER BY date DESC")
    records = cur.fetchall()
    global count
    count = 0
    for record in records:
        if count % 2 == 0:
            stock_tree.insert(parent='', index='end', iid=count, text='', values=(record[0],record[1], record[2], record[3], record[4], record[5], record[6]), tags=('evenrow',))
        else:
            stock_tree.insert(parent='', index='end', iid=count, text='', values=(record[0],record[1], record[2], record[3], record[4], record[5], record[6]), tags=('oddrow',))
        count += 1
    #Get Data For Records TreeView
    cur.execute("SELECT name ,round(SUM(cost),2) as total_cost, round(SUM(shares),10) as total_shares,abs(round((SUM(cost) / SUM(shares)),2)) as total_avg FROM stock_trades GROUP BY name ORDER BY total_shares DESC")
    global sum_stock_buy
    global sum_stock_sell
    global sum_stock_invest
    global hold_lst
    for row in cur:
        if row[2] == 0 and row[1] < 0:
            stock_report_tree.insert('','end', values = (row[0],row[1], row[2],row[3]), tags=('loss',))
        elif row[2] == 0 and row[1] > 0:
            stock_report_tree.insert('','end', values = (row[0],row[1], row[2],row[3]), tags=('gain',))
        else:
            stock_report_tree.insert('','end', values = (row[0],row[1], row[2],row[3]))
    cur.execute("SELECT round(SUM(cost),2) FROM stock_trades WHERE event = 'Buy' " )
    for buy in cur:
        if buy[0] == None:
            sum_stock_buy = 0
        else:
            sum_stock_buy= abs(buy[0])
    cur.execute("SELECT round(SUM(cost),2) FROM stock_trades WHERE event = 'Sell' " )
    for sell in cur:
        if sell[0] == None:
            sum_stock_sell = 0
        else:
            sum_stock_sell = abs(sell[0])
    sum_stock_invest = str(round(sum_stock_buy - sum_stock_sell,2))
    stock_header.insert(0,"TOTAL AMOUNT INVESTED : $" + sum_stock_invest)
    stock_header.config(state='disabled')

    #Get Data For CRYPTO TreeView
    cur.execute("SELECT rowid,* FROM crypto_trades ORDER BY date DESC")
    records = cur.fetchall()
    global crypto_count
    crypto_count = 0
    for record in records:
        if crypto_count % 2 == 0:
            crypto_tree.insert(parent='', index='end', iid=crypto_count, text='', values=(record[0],record[1], record[2], record[3], record[4], record[5], record[6]), tags=('evenrow',))
        else:
            crypto_tree.insert(parent='', index='end', iid=crypto_count, text='', values=(record[0],record[1], record[2], record[3], record[4], record[5], record[6]), tags=('oddrow',))
        crypto_count += 1
    #Get Data For Records TreeView
    cur.execute("SELECT name ,round(SUM(cost),2) as total_crypto_cost, round(SUM(coins),10) as total_crypto_coins,abs(round((SUM(cost) / SUM(coins)),2)) as total_crypto_avg FROM crypto_trades GROUP BY name ORDER BY total_crypto_coins DESC")
    global sum_crypto_buy
    global sum_crypto_sell
    global sum_crypto_invest
    for row in cur:
        if row[2] == 0 and row[1] < 0:
            crypto_report_tree.insert('','end', values = (row[0],row[1], row[2],row[3]), tags=('loss',))
        elif row[2] == 0 and row[1] > 0:
            crypto_report_tree.insert('','end', values = (row[0],row[1], row[2],row[3]), tags=('gain',))
        else:
            crypto_report_tree.insert('','end', values = (row[0],row[1], row[2],row[3]))
    cur.execute("SELECT round(SUM(cost),2) FROM crypto_trades WHERE event = 'Buy' " )
    for buy in cur:
        if buy[0] == None:
            sum_crypto_buy = 0
        else:
            sum_crypto_buy= abs(buy[0])
    cur.execute("SELECT round(SUM(cost),2) FROM crypto_trades WHERE event = 'Sell' " )
    for sell in cur:
        if sell[0] == None:
            sum_crypto_sell = 0
        else:
            sum_crypto_sell = abs(sell[0])
    sum_crypto_invest = str(round(sum_crypto_buy - sum_crypto_sell,2))
    crypto_header.insert(0,"TOTAL AMOUNT INVESTED : $" + sum_crypto_invest)
    crypto_header.config(state='disabled')

    con.commit()
    con.close()

#Add Some Style
style = ttk.Style()
#Pick A Theme
style.theme_use('default')
#Configure the Treeview
style.configure("Treeview",
                background="#F8F8FF",
                foreground="black",
                rowheight=25,
                fieldbackground="#D3D3D3")
#Change Selected Color
style.map('Treeview',
          background=[('selected', "#347083")])

#STOCKS REPORT TREEVIEW
stock_report_frame = Frame(main)
stock_report_frame.place(x=770,y=115)
stock_report_scroll = Scrollbar(stock_report_frame)
stock_report_scroll.pack(side=RIGHT, fill=Y)
stock_report_tree = ttk.Treeview(stock_report_frame, yscrollcommand=stock_report_scroll.set, selectmode="extended")
stock_report_tree.pack()
stock_report_scroll.config(command=stock_report_tree.yview)
stock_report_tree['columns'] = ("name", "total_cost", "total_shares", "total_avg")
stock_report_tree.column("#0", width=0, stretch=NO)
stock_report_tree.column("name", anchor=CENTER, width=100)
stock_report_tree.column("total_cost", anchor=CENTER, width=100)
stock_report_tree.column("total_shares", anchor=CENTER, width=100)
stock_report_tree.column("total_avg", anchor=CENTER, width=100)
stock_report_tree.heading("#0",text="", anchor=W)
stock_report_tree.heading("name",text="STOCK", anchor=CENTER)
stock_report_tree.heading("total_cost",text="COST", anchor=CENTER)
stock_report_tree.heading("total_shares",text="SHARES", anchor=CENTER)
stock_report_tree.heading("total_avg",text="AVERAGE", anchor=CENTER)
#CRYPTO report TreeView
crypto_report_frame = Frame(main)
crypto_report_frame.place(x=770,y=510)
crypto_report_scroll = Scrollbar(crypto_report_frame)
crypto_report_scroll.pack(side=RIGHT, fill=Y)
crypto_report_tree = ttk.Treeview(crypto_report_frame, yscrollcommand=crypto_report_scroll.set, selectmode="extended")
crypto_report_tree.pack()
crypto_report_scroll.config(command=crypto_report_tree.yview)
crypto_report_tree['columns'] = ("name", "total_crypto_cost", "total_crypto_coins", "total_crypto_avg")
crypto_report_tree.column("#0", width=0, stretch=NO)
crypto_report_tree.column("name", anchor=CENTER, width=100)
crypto_report_tree.column("total_crypto_cost", anchor=CENTER, width=100)
crypto_report_tree.column("total_crypto_coins", anchor=CENTER, width=100)
crypto_report_tree.column("total_crypto_avg", anchor=CENTER, width=100)
crypto_report_tree.heading("#0",text="", anchor=W)
crypto_report_tree.heading("name",text="COIN", anchor=CENTER)
crypto_report_tree.heading("total_crypto_cost",text="COST", anchor=CENTER)
crypto_report_tree.heading("total_crypto_coins",text="COINS", anchor=CENTER)
crypto_report_tree.heading("total_crypto_avg",text="AVERAGE", anchor=CENTER)

#Create a Treeview Frames
stock_tree_frame = Frame(main)
stock_tree_frame.place(x=140,y=115)

crypto_tree_frame = Frame(main)
crypto_tree_frame.place(x=140,y=510)
#Create a Treeview Scrollbar
stock_tree_scroll = Scrollbar(stock_tree_frame)
stock_tree_scroll.pack(side=RIGHT, fill=Y)

crypto_tree_scroll = Scrollbar(crypto_tree_frame)
crypto_tree_scroll.pack(side=RIGHT, fill=Y)
#Create The Treeview
stock_tree = ttk.Treeview(stock_tree_frame, yscrollcommand=stock_tree_scroll.set, selectmode="extended")
stock_tree.pack()

crypto_tree = ttk.Treeview(crypto_tree_frame, yscrollcommand=crypto_tree_scroll.set, selectmode="extended")
crypto_tree.pack()
#Configure the Scrollbar
stock_tree_scroll.config(command=stock_tree.yview)
crypto_tree_scroll.config(command=crypto_tree.yview)
#Define Our Columns
stock_tree['columns'] = ("rowid","Date", "Event", "Stock", "Cost", "Shares", "Price")
crypto_tree['columns'] = ("rowid","Date", "Event", "Coin", "Cost", "Coins", "Price")
#Format Our Columns
stock_tree.column("#0", width=0, stretch=NO)
stock_tree.column("rowid", width=0, stretch=NO)
stock_tree.column("Date", anchor=CENTER, width=100)
stock_tree.column("Event", anchor=CENTER, width=100)
stock_tree.column("Stock", anchor=CENTER, width=100)
stock_tree.column("Cost", anchor=CENTER, width=100)
stock_tree.column("Shares", anchor=CENTER, width=100)
stock_tree.column("Price", anchor=CENTER, width=100)

crypto_tree.column("#0", width=0, stretch=NO)
crypto_tree.column("rowid", width=0, stretch=NO)
crypto_tree.column("Date", anchor=CENTER, width=100)
crypto_tree.column("Event", anchor=CENTER, width=100)
crypto_tree.column("Coin", anchor=CENTER, width=100)
crypto_tree.column("Cost", anchor=CENTER, width=100)
crypto_tree.column("Coins", anchor=CENTER, width=100)
crypto_tree.column("Price", anchor=CENTER, width=100)
#Create Headings
stock_tree.heading("#0",text="", anchor=W)
stock_tree.heading("rowid",text="", anchor=W)
stock_tree.heading("Date",text="Date", anchor=CENTER)
stock_tree.heading("Event",text="Event", anchor=CENTER)
stock_tree.heading("Stock",text="Stock", anchor=CENTER)
stock_tree.heading("Cost",text="Cost", anchor=CENTER)
stock_tree.heading("Shares",text="Shares", anchor=CENTER)
stock_tree.heading("Price",text="Price", anchor=CENTER)

crypto_tree.heading("#0",text="", anchor=W)
crypto_tree.heading("rowid",text="", anchor=W)
crypto_tree.heading("Date",text="Date", anchor=CENTER)
crypto_tree.heading("Event",text="Event", anchor=CENTER)
crypto_tree.heading("Coin",text="Coin", anchor=CENTER)
crypto_tree.heading("Cost",text="Cost", anchor=CENTER)
crypto_tree.heading("Coins",text="Coins", anchor=CENTER)
crypto_tree.heading("Price",text="Price", anchor=CENTER)
#Create Striped Row Tags
stock_tree.tag_configure('oddrow', background="white")
stock_tree.tag_configure('evenrow', background="lightblue")
stock_report_tree.tag_configure('gain', background="#98FB98")
stock_report_tree.tag_configure('loss', background="#FFC0CB")

crypto_tree.tag_configure('oddrow', background="white")
crypto_tree.tag_configure('evenrow', background="lightblue")
crypto_report_tree.tag_configure('gain', background="#98FB98")
crypto_report_tree.tag_configure('loss', background="#FFC0CB")
#Add STOCK Record Entry Boxes
new_stock_frame = LabelFrame(main, text = "Stock Information")
new_stock_frame.place(x=10,y=10)

stock_date_label = Label(new_stock_frame, text="Date")
stock_date_label.grid(row=0, column=0, pady=5, padx=5)
stock_date_var = StringVar()
stock_date = DateEntry(new_stock_frame, locale='en_US', date_pattern='yyyy-MM-dd', selectmode = 'day', firstweekday='sunday', textvariable=stock_date_var)
stock_date.grid(row=1, column=0, pady=5, padx=5)

stock_event_label = Label(new_stock_frame, text="Event")
stock_event_label.grid(row=0, column=1, pady=0, padx=0)
def display_selected_stock_event(choice):
    choice = stock_event_var.get()

stock_event_level = ['Select',
               'Buy',
               'Sell',
               'Dividend']
stock_event_var = StringVar()
stock_event_var.set(stock_event_level[0])
menu_width = len(max(stock_event_level, key=len))
stock_event = OptionMenu(new_stock_frame, stock_event_var, *stock_event_level,command=display_selected_stock_event)
stock_event.config(width=menu_width)
stock_event.grid(row=1, column=1, pady=0, padx=0)

stock_name_label = Label(new_stock_frame, text="Name")
stock_name_label.grid(row=0, column=2, pady=5, padx=5)
stock_name = Entry(new_stock_frame, font=('veranda',14),width=6,justify='center')
stock_name.grid(row=1, column=2, pady=5, padx=5)

stock_cost_label = Label(new_stock_frame, text="Cost")
stock_cost_label.grid(row=0, column=3, pady=5, padx=5)
stock_cost = Entry(new_stock_frame, font=('veranda',14),width=13,justify='right')
stock_cost.grid(row=1, column=3, pady=5, padx=5)
        
stock_shares_label = Label(new_stock_frame, text="Shares")
stock_shares_label.grid(row=0, column=4, pady=5, padx=5)
stock_shares = Entry(new_stock_frame, font=('veranda',14),width=13,justify='right')
stock_shares.grid(row=1, column=4, pady=5, padx=5)

stock_price_label = Label(new_stock_frame, text="Price")
stock_price_label.grid(row=0, column=5, pady=5, padx=5)
stock_price = Entry(new_stock_frame, font=('veranda',14),width=13,justify='right')
stock_price.grid(row=1, column=5, pady=5, padx=6)

#Add CRYPTO Record Entry Boxes
new_crypto_frame = LabelFrame(main, text = "Crypto Information")
new_crypto_frame.place(x=10,y=410)

crypto_date_label = Label(new_crypto_frame, text="Date")
crypto_date_label.grid(row=0, column=0, pady=5, padx=6)
crypto_date_var = StringVar()
crypto_date = DateEntry(new_crypto_frame, locale='en_US', date_pattern='yyyy-MM-dd', selectmode = 'day', firstweekday='sunday', textvariable=crypto_date_var)
crypto_date.grid(row=1, column=0, pady=5, padx=5)

crypto_event_label = Label(new_crypto_frame, text="Event")
crypto_event_label.grid(row=0, column=1, pady=0, padx=0)
def display_selected_crypto_event(choice):
    choice = crypto_event_var.get()

crypto_event_level = ['Select',
               'Buy',
               'Sell',
               'Reward']
crypto_event_var = StringVar()
crypto_event_var.set(crypto_event_level[0])
menu_width = len(max(crypto_event_level, key=len))
crypto_event = OptionMenu(new_crypto_frame, crypto_event_var, *crypto_event_level,command=display_selected_crypto_event)
crypto_event.config(width=menu_width)
crypto_event.grid(row=1, column=1, pady=0, padx=5)

crypto_name_label = Label(new_crypto_frame, text="Name")
crypto_name_label.grid(row=0, column=2, pady=5, padx=5)
crypto_name = Entry(new_crypto_frame, font=('veranda',14),width=6,justify='center')
crypto_name.grid(row=1, column=2, pady=5, padx=5)

crypto_cost_label = Label(new_crypto_frame, text="Cost")
crypto_cost_label.grid(row=0, column=3, pady=5, padx=5)
crypto_cost = Entry(new_crypto_frame, font=('veranda',14),width=13,justify='right')
crypto_cost.grid(row=1, column=3, pady=5, padx=5)
        
crypto_coins_label = Label(new_crypto_frame, text="coins")
crypto_coins_label.grid(row=0, column=4, pady=5, padx=5)
crypto_coins = Entry(new_crypto_frame, font=('veranda',14),width=13,justify='right')
crypto_coins.grid(row=1, column=4, pady=5, padx=5)

crypto_price_label = Label(new_crypto_frame, text="Price")
crypto_price_label.grid(row=0, column=5, pady=5, padx=5)
crypto_price = Entry(new_crypto_frame, font=('veranda',14),width=13,justify='right')
crypto_price.grid(row=1, column=5, pady=5, padx=6)

#Delete STOCK From DataBase
def stock_delete_entry():
    selected = stock_tree.focus()
    values = stock_tree.item(selected, 'values')
    response = messagebox.askyesno("Delete Entry", "Do you want to DELETE "+ values[3]+"?")
    if response == 1:
        con = sqlite3.connect('investments.db')
        cur = con.cursor()
        cur.execute("DELETE from stock_trades WHERE oid=" +values[0])    
        con.commit()
        con.close()
        stock_clear_entries()
        stock_tree.delete(*stock_tree.get_children())
        stock_report_tree.delete(*stock_report_tree.get_children())
        crypto_tree.delete(*crypto_tree.get_children())
        crypto_report_tree.delete(*crypto_report_tree.get_children())
        query_investments()
    else:
        stock_clear_entries()
# Delete CRYPTO from Database
def crypto_delete_entry():
    selected = crypto_tree.focus()
    values = crypto_tree.item(selected, 'values')
    response = messagebox.askyesno("Delete Entry", "Do you want to DELETE "+ values[3]+"?")
    if response == 1:
        con = sqlite3.connect('investments.db')
        cur = con.cursor()
        cur.execute("DELETE from crypto_trades WHERE oid=" +values[0])    
        con.commit()
        con.close()
        crypto_clear_entries()
        stock_tree.delete(*stock_tree.get_children())
        stock_report_tree.delete(*stock_report_tree.get_children())
        crypto_tree.delete(*crypto_tree.get_children())
        crypto_report_tree.delete(*crypto_report_tree.get_children())
        query_investments()
    else:
        crypto_clear_entries()
     
#Clear STOCK Entry Boxes
def stock_clear_entries():
    stock_date = DateEntry(new_stock_frame, locale='en_US', date_pattern='yyyy-MM-dd', selectmode = 'day', firstweekday='sunday', textvariable=stock_date_var)
    stock_event_var.set(stock_event_level[0])
    stock_name.delete(0, END)
    stock_cost.delete(0, END)
    stock_shares.delete(0, END)
    stock_price.delete(0, END)
#Clear CRYPTO Entry Boxes
def crypto_clear_entries():
    crypto_date = DateEntry(new_crypto_frame, locale='en_US', date_pattern='yyyy-MM-dd', selectmode = 'day', firstweekday='sunday', textvariable=crypto_date_var)
    crypto_event_var.set(crypto_event_level[0])
    crypto_name.delete(0, END)
    crypto_cost.delete(0, END)
    crypto_coins.delete(0, END)
    crypto_price.delete(0, END)
    
#Select STOCK Record
def stock_select_record(e):
    #clear entry boxes
    stock_clear_entries()
    #Grab Record Number
    selected = stock_tree.focus()
    #Grab Record Values
    values = stock_tree.item(selected, 'values')
    #Output into entry fields
    stock_date_var.set(values[1])
    stock_event_var.set(values[2])
    stock_name.insert(0, values[3])
    stock_cost.insert(0, values[4])
    stock_shares.insert(0, values[5])
    stock_price.insert(0, values[6])
#Select CRYPTO Record
def crypto_select_record(e):
    #clear entry boxes
    crypto_clear_entries()
    #Grab Record Number
    selected = crypto_tree.focus()
    #Grab Record Values
    values = crypto_tree.item(selected, 'values')
    #Output into entry fields
    crypto_date_var.set(values[1])
    crypto_event_var.set(values[2])
    crypto_name.insert(0, values[3])
    crypto_cost.insert(0, values[4])
    crypto_coins.insert(0, values[5])
    crypto_price.insert(0, values[6])

#Update STOCK Record
def stock_update_record():
    #Grab the Record
    selected = stock_tree.focus()
    values = stock_tree.item(selected, 'values')
    #Update
    check_counter=0
    if stock_price.get() == "":
        warn = "Enter Pricee"
    elif stock_price.get().isalpha():
        warn= "Fix Price per Share: \nNumbers Only"
    else:
        check_counter += 1

    if stock_shares.get() == "":
        warn = "Enter Number of Shares"
    elif stock_shares.get().isalpha():
        warn= "Fix Sahres: \nNumbers Only"
    else:
        check_counter += 1

    if stock_cost.get() == "":
        warn = "Enter Cost"
    elif stock_cost.get().isalpha():
        warn= "Fix Cost: \nNumbers Only"
    else:
        check_counter += 1

    if stock_name.get() == "":
        warn = "Enter Stock Ticker"
    else:
        check_counter += 1

    if stock_event_var.get() == "Select":
        warn = "Select Buy / Sell / Dividend"
    else:
        check_counter += 1

    if stock_date_var.get() == "":
        warn = "Enter Date"
    else:
        check_counter += 1
    if check_counter == 6:
        try:
            con = sqlite3.connect('investments.db')
            cur = con.cursor()
            cur.execute("""UPDATE stock_trades SET
                date= :date,
                event= :event,
                name= :name,
                cost= :cost,
                shares= :shares,
                price= :price
                WHERE oid = :oid""",
                {
                    'date': stock_date_var.get(),
                    'event': stock_event_var.get(),
                    'name': stock_name.get(),
                    'cost': stock_cost.get(),
                    'shares': stock_shares.get(),
                    'price': stock_price.get(),
                    'oid': values[0]
                    })
            con.commit()
            con.close()
            messagebox.showinfo('confirmation', str(stock_name.get()) +" "  + str(stock_event_var.get()) + '\nUpdate Saved')
            #clear entry boxes
            stock_clear_entries()
            stock_tree.delete(*stock_tree.get_children())
            stock_report_tree.delete(*stock_report_tree.get_children())
            crypto_tree.delete(*crypto_tree.get_children())
            crypto_report_tree.delete(*crypto_report_tree.get_children())
            query_investments()
        except Exception as ep:
            messagebox.showerror('', ep) 
    else:
        messagebox.showerror('Error', warn)
#Update CRYPTO Record
def crypto_update_record():
    #Grab the Record
    selected = crypto_tree.focus()
    values = crypto_tree.item(selected, 'values')
    #Update
    check_counter=0
    if crypto_price.get() == "":
        warn = "Enter Price"
    elif crypto_price.get().isalpha():
        warn= "Fix Price per Coin: \nNumbers Only"
    else:
        check_counter += 1

    if crypto_coins.get() == "":
        warn = "Enter Number of Coins"
    elif crypto_coins.get().isalpha():
        warn= "Fix Coins: \nNumbers Only"
    else:
        check_counter += 1

    if crypto_cost.get() == "":
        warn = "Enter Cost"
    elif crypto_cost.get().isalpha():
        warn= "Fix Cost: \nNumbers Only"
    else:
        check_counter += 1

    if crypto_name.get() == "":
        warn = "Enter Coin (BTC, ETH)"
    else:
        check_counter += 1

    if crypto_event_var.get() == "Select":
        warn = "Select Buy / Sell / Reward"
    else:
        check_counter += 1

    if crypto_date_var.get() == "":
        warn = "Enter Date"
    else:
        check_counter += 1
    if crypto_event_var.get() =='Buy':
        crypto_cost_var = ('-'+crypto_cost.get())
    else:
        crypto_cost_var = crypto_cost.get()
    if crypto_event_var.get() =='Sell':
        crypto_coins_var = ('-'+crypto_coins.get())
    else:
        crypto_coins_var = crypto_coins.get()
    if check_counter == 6:
        try:
            con = sqlite3.connect('investments.db')
            cur = con.cursor()
            cur.execute("""UPDATE crypto_trades SET
                date= :date,
                event= :event,
                name= :name,
                cost= :cost,
                coins= :coins,
                price= :price
                WHERE oid = :oid""",
                {
                    'date': crypto_date_var.get(),
                    'event': crypto_event_var.get(),
                    'name': crypto_name.get(),
                    'cost': crypto_cost.get(),
                    'coins': crypto_coins.get(),
                    'price': crypto_price.get(),
                    'oid': values[0]
                    })
            con.commit()
            con.close()
            messagebox.showinfo('confirmation', str(crypto_name.get()) +" "  + str(crypto_event_var.get()) + '\nUpdate Saved')
            #clear entry boxes
            crypto_clear_entries()
            stock_tree.delete(*stock_tree.get_children())
            stock_report_tree.delete(*stock_report_tree.get_children())
            crypto_tree.delete(*crypto_tree.get_children())
            crypto_report_tree.delete(*crypto_report_tree.get_children())
            query_investments()
        except Exception as ep:
            messagebox.showerror('', ep) 
    else:
        messagebox.showerror('Error', warn)
    
# Add a new STOCK
def stock_add_record():
    check_counter=0
    if stock_price.get() == "":
        warn = "Enter Price"
    elif stock_price.get().isalpha():
        warn= "Fix Price per Share: \nNumbers Only"
    else:
        check_counter += 1

    if stock_shares.get() == "":
        warn = "Enter Number of Shares"
    elif stock_shares.get().isalpha():
        warn= "Fix Sahres: \nNumbers Only"
    else:
        check_counter += 1

    if stock_cost.get() == "":
        warn = "Enter Cost"
    elif stock_cost.get().isalpha():
        warn= "Fix Cost: \nNumbers Only"
    else:
        check_counter += 1

    if stock_name.get() == "":
        warn = "Enter Stock Ticker"
    else:
        check_counter += 1

    if stock_event_var.get() == "Select":
        warn = "Select Buy / Sell / Dividend"
    else:
        check_counter += 1

    if stock_date_var.get() == "":
        warn = "Enter Date"
    else:
        check_counter += 1
    if stock_event_var.get() =='Buy':
        stock_cost_var = ('-'+stock_cost.get())
    else:
        stock_cost_var = stock_cost.get()
    if stock_event_var.get() =='Sell':
        stock_shares_var = ('-'+stock_shares.get())
    else:
        stock_shares_var = stock_shares.get()
    if check_counter == 6:
        try:
            con = sqlite3.connect('investments.db')
            cur = con.cursor()
            cur.execute("INSERT INTO stock_trades VALUES ( :date, :event, :name, :cost, :shares, :price)",
                        {'date': stock_date_var.get(),
                        'event': stock_event_var.get(),
                        'name': stock_name.get(),
                        'cost': stock_cost_var,
                        'shares': stock_shares_var,
                        'price': stock_price.get()})
            con.commit()
            con.close()
            messagebox.showinfo('confirmation', str(stock_name.get()) +" "  + str(stock_event_var.get()) + '\nRecord Saved')
            #clear entry boxes
            stock_clear_entries()
            #clear treeviews
            stock_tree.delete(*stock_tree.get_children())
            stock_report_tree.delete(*stock_report_tree.get_children())
            crypto_tree.delete(*crypto_tree.get_children())
            crypto_report_tree.delete(*crypto_report_tree.get_children())
            query_investments()
        except Exception as ep:
            messagebox.showerror('', ep) 
    else:
        messagebox.showerror('Error', warn)
#Add New CRYPTO
def crypto_add_record():
    check_counter=0
    if crypto_price.get() == "":
        warn = "Enter Price"
    elif crypto_price.get().isalpha():
        warn= "Fix Price per Coin: \nNumbers Only"
    else:
        check_counter += 1

    if crypto_coins.get() == "":
        warn = "Enter Number of Coins"
    elif crypto_coins.get().isalpha():
        warn= "Fix Coins: \nNumbers Only"
    else:
        check_counter += 1

    if crypto_cost.get() == "":
        warn = "Enter Cost"
    elif crypto_cost.get().isalpha():
        warn= "Fix Cost: \nNumbers Only"
    else:
        check_counter += 1

    if crypto_name.get() == "":
        warn = "Enter Coin (BTC, ETH)"
    else:
        check_counter += 1

    if crypto_event_var.get() == "Select":
        warn = "Select Buy / Sell / Reward"
    else:
        check_counter += 1

    if crypto_date_var.get() == "":
        warn = "Enter Date"
    else:
        check_counter += 1
    if crypto_event_var.get() =='Buy':
        crypto_cost_var = ('-'+crypto_cost.get())
    else:
        crypto_cost_var = crypto_cost.get()
    if crypto_event_var.get() =='Sell':
        crypto_coins_var = ('-'+crypto_coins.get())
    else:
        crypto_coins_var = crypto_coins.get()
    if check_counter == 6:
        try:
            con = sqlite3.connect('investments.db')
            cur = con.cursor()
            cur.execute("INSERT INTO crypto_trades VALUES ( :date, :event, :name, :cost, :coins, :price)",
                        {'date': crypto_date_var.get(),
                        'event': crypto_event_var.get(),
                        'name': crypto_name.get(),
                        'cost': crypto_cost_var,
                        'coins': crypto_coins_var,
                        'price': crypto_price.get()})
            con.commit()
            con.close()
            messagebox.showinfo('confirmation', str(crypto_name.get()) +" "  + str(crypto_event_var.get()) + '\nRecord Saved')
            #clear entry boxes
            crypto_clear_entries()
            #clear treeview
            stock_tree.delete(*stock_tree.get_children())
            stock_report_tree.delete(*stock_report_tree.get_children())
            crypto_tree.delete(*crypto_tree.get_children())
            crypto_report_tree.delete(*crypto_report_tree.get_children())
            query_investments()
        except Exception as ep:
            messagebox.showerror('', ep) 
    else:
        messagebox.showerror('Error', warn)

# Prevent Pandas from limiting printed rowa
pandas.set_option('display.max_rows', None)
def create_csv_reports():
    con = sqlite3.connect('investments.db')
    cur = con.cursor()

    stock_report_dataframe = (pandas.read_sql_query("SELECT name as Name, round(SUM(cost),2) as Cost, round(SUM(shares),10) as Shares,abs(round((SUM(cost) / SUM(shares)),2)) as Average FROM stock_trades GROUP BY name ORDER BY Shares DESC",con))
    stock_report_dataframe.to_csv('C:/Users/First Last/Python/Python39-32/Project_Investments/stock_report.csv', index=False)

    stock_trades_dataframe = (pandas.read_sql_query("SELECT * FROM stock_trades ORDER BY date DESC",con))
    stock_trades_dataframe.to_csv('C:/Users/First Last/Python/Python39-32/Project_Investments/stock_trades.csv', index=False)

    crypto_report_dataframe = (pandas.read_sql_query("SELECT name as Name, round(SUM(cost),2) as Cost, round(SUM(coins),10) as Coins,abs(round((SUM(cost) / SUM(coins)),2)) as Average FROM crypto_trades GROUP BY name ORDER BY Coins DESC",con))
    crypto_report_dataframe.to_csv('C:/Users/First Last/Python/Python39-32/Project_Investments/crypto_report.csv', index=False)

    crypto_trades_dataframe = (pandas.read_sql_query("SELECT * FROM crypto_trades ORDER BY date DESC",con))
    crypto_trades_dataframe.to_csv('C:/Users/First Last/Python/Python39-32/Project_Investments/crypto_trades.csv', index=False)

    con.commit()
    con.close()

def delete_csv_reports():
    stock_report = 'C:/Users/First Last/Python/Python39-32/Project_Investments/stock_report.csv'
    stock_trades = 'C:/Users/First Last/Python/Python39-32/Project_Investments/stock_trades.csv'
    crypto_report = 'C:/Users/First Last/Python/Python39-32/Project_Investments/crypto_report.csv'
    crypto_trades = 'C:/Users/First Last/Python/Python39-32/Project_Investments/crypto_trades.csv'

    os.remove(stock_report)
    os.remove(stock_trades)
    os.remove(crypto_report)
    os.remove(crypto_trades)

def pdf_full_report():
    create_csv_reports()
    import csv
    from fpdf import FPDF
    import datetime
    # Create the PDF
    pdf = FPDF()
    pdf.add_page()
    page_width = pdf.w - 2 * pdf.l_margin
    # Create the Title
    pdf.set_font('Times','B',14)
    pdf.cell(page_width, 0.0, 'Investments Report', align='C')
    pdf.ln(5)
    pdf.set_font('Times','',10.0) 
    pdf.cell(page_width, 0.0, str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), align='C')
    pdf.ln(10)
    # Add STOCK REPORT table
    pdf.set_font('Times','B',14)
    pdf.cell(page_width, 0.0, 'Stock Report', align='C')
    pdf.ln(5)
    pdf.set_font('Times','',14)
    pdf.cell(page_width, 0.0, 'Total stock buy amount: -'+ str(sum_stock_buy), align='L')
    pdf.ln(5)
    pdf.cell(page_width, 0.0, 'Total stock sell amount: +'+ str(sum_stock_sell), align='L')
    pdf.ln(5)
    pdf.cell(page_width, 0.0, 'Total stock investments: '+ str(sum_stock_invest), align='L')
    pdf.ln(5)
    pdf.set_font('Courier', '', 12)
    col_width = page_width/4
    th = pdf.font_size
    stock_report=open('stock_report.csv', newline='')
    stock_report_reader = csv.reader(stock_report)
    
    for row in stock_report_reader:
                 pdf.cell(col_width, th, row[0], border=1)
                 pdf.cell(col_width, th, row[1], border=1)
                 pdf.cell(col_width, th, row[2], border=1)
                 pdf.cell(col_width, th, row[3], border=1)
                 pdf.ln(th)
    pdf.ln(10)

    # Add CRYPTO REPORT table on a new page
    pdf.add_page()
    page_width = pdf.w - 2 * pdf.l_margin
    pdf.set_font('Times','B',14)
    pdf.cell(page_width, 0.0, 'Crypto Report', align='C')
    pdf.ln(5)
    pdf.set_font('Times','',14)
    pdf.cell(page_width, 0.0, 'Total crypto buy amount: -'+ str(sum_crypto_buy), align='L')
    pdf.ln(5)
    pdf.cell(page_width, 0.0, 'Total crypto sell amount: +'+ str(sum_crypto_sell), align='L')
    pdf.ln(5)
    pdf.cell(page_width, 0.0, 'Total crypto investments: '+ str(sum_crypto_invest), align='L')
    pdf.ln(5)

    pdf.set_font('Courier', '', 12)
    col_width = page_width/4
    th = pdf.font_size
    crypto_report=open('crypto_report.csv', newline='')
    crypto_report_reader = csv.reader(crypto_report)
    
    for row in crypto_report_reader:
                 pdf.cell(col_width, th, row[0], border=1)
                 pdf.cell(col_width, th, row[1], border=1)
                 pdf.cell(col_width, th, row[2], border=1)
                 pdf.cell(col_width, th, row[3], border=1)
                 pdf.ln(th)
    pdf.ln(10)

    # Add STOCK TRADES table on a new page
    pdf.add_page()
    page_width = pdf.w - 2 * pdf.l_margin
    pdf.set_font('Times','B',14)
    pdf.cell(page_width, 0.0, 'Stock Trades', align='C')
    pdf.ln(5)

    pdf.set_font('Courier', '', 12)
    col_width = page_width/6
    th = pdf.font_size
    stock_trades=open('stock_trades.csv', newline='')
    stock_trades_reader = csv.reader(stock_trades)
    
    for row in stock_trades_reader:
                 pdf.cell(col_width, th, row[0], border=1)
                 pdf.cell(col_width, th, row[1], border=1)
                 pdf.cell(col_width, th, row[2], border=1)
                 pdf.cell(col_width, th, row[3], border=1)
                 pdf.cell(col_width, th, row[4], border=1)
                 pdf.cell(col_width, th, row[5], border=1)
                 pdf.ln(th)
    pdf.ln(10)

    # Add CRYPTO TRADES table on a new page
    pdf.add_page()
    page_width = pdf.w - 2 * pdf.l_margin
    pdf.set_font('Times','B',14)
    pdf.cell(page_width, 0.0, 'Crypto Trades', align='C')
    pdf.ln(5)

    pdf.set_font('Courier', '', 12)
    col_width = page_width/6
    th = pdf.font_size
    crypto_trades=open('crypto_trades.csv', newline='')
    crypto_trades_reader = csv.reader(crypto_trades)
    
    for row in crypto_trades_reader:
                 pdf.cell(col_width, th, row[0], border=1)
                 pdf.cell(col_width, th, row[1], border=1)
                 pdf.cell(col_width, th, row[2], border=1)
                 pdf.cell(col_width, th, row[3], border=1)
                 pdf.cell(col_width, th, row[4], border=1)
                 pdf.cell(col_width, th, row[5], border=1)
                 pdf.ln(th)
    pdf.ln(10)

    # Create Footer
    pdf.set_font('Times','',10.0) 
    pdf.cell(page_width, 0.0, '- end of report -', align='C')
    # Generate PDF
    report_name = (str(datetime.datetime.now().strftime('%m-%Y_'))+'investments_report.pdf')
    pdf.output(report_name, 'F')

    stock_report.close()
    stock_trades.close()
    crypto_report.close()
    crypto_trades.close()

    delete_csv_reports()
    
    messagebox.showinfo('confirmation', 'Full Report PDF generated')
    os.startfile('C:/Users/First Last/Python/Python39-32/Project_Investments/'+report_name)


#Add STOCK Buttons to screen
stock_button_frame=LabelFrame(main, text = "Commands")
stock_button_frame.place(x=10,y=115)

stock_save_button = Button(stock_button_frame, text="   Save New   ", command=stock_add_record)
stock_save_button.grid(row=0, column=0, pady=10, padx=10)

stock_edit_button = Button(stock_button_frame, text="Update Record", command=stock_update_record)
stock_edit_button.grid(row=1, column=0, pady=10, padx=10)

stock_delete_button = Button(stock_button_frame, text="Delete Selected", command = stock_delete_entry)
stock_delete_button.grid(row=2, column=0, pady=10, padx=10)

stock_clear_button = Button(stock_button_frame, text="   Clear Entry   ", command = stock_clear_entries)
stock_clear_button.grid(row=3, column=0, pady=10, padx=10)

#Add CRYPTO Buttons to screen
crypto_button_frame=LabelFrame(main, text = "Commands")
crypto_button_frame.place(x=10,y=510)

crypto_save_button = Button(crypto_button_frame, text="   Save New   ", command=crypto_add_record)
crypto_save_button.grid(row=0, column=0, pady=10, padx=10)

crypto_edit_button = Button(crypto_button_frame, text="Update Record", command=crypto_update_record)
crypto_edit_button.grid(row=1, column=0, pady=10, padx=10)

crypto_delete_button = Button(crypto_button_frame, text="Delete Selected", command = crypto_delete_entry)
crypto_delete_button.grid(row=2, column=0, pady=10, padx=10)

crypto_clear_button = Button(crypto_button_frame, text="   Clear Entry   ", command = crypto_clear_entries)
crypto_clear_button.grid(row=3, column=0, pady=10, padx=10)

#Bind the Treeview
stock_tree.bind("<ButtonRelease-1>", stock_select_record)
crypto_tree.bind("<ButtonRelease-1>", crypto_select_record)
# Headers
robbinhood_pic = Image.open('C:/Users/First Last/Python/Python39-32/Project_Images/robinhoodlogo.png')
robbinhood_resize = robbinhood_pic.resize((50, 50), Image.ANTIALIAS)
robbinhood_pic = ImageTk.PhotoImage(robbinhood_resize)
Label( main, image=robbinhood_pic,height=50,width=50,).place(x=780, y=10)
Label(main, text="Robinhood",font =('MaisonNeue', 30, 'bold'),bg='#0B5A81', fg='#21ce99').place(x=840, y=10)
# Ammount invested Entry
stock_header = Entry(main, font=('veranda' ,15, 'bold'),width=35,justify='center')
stock_header.place(x=780, y=70)

coinbase_pic = Image.open('C:/Users/First Last/Python/Python39-32/Project_Images/coinbaselogo.png')
coinbase_resize = coinbase_pic.resize((50, 50), Image.ANTIALIAS)
coinbase_pic = ImageTk.PhotoImage(coinbase_resize)
Label( main, image=coinbase_pic,height=50,width=50,).place(x=780, y=410)
Label(main, text="Coinbase",font =('FF Daxline', 30, 'bold'),bg='#0B5A81', fg='#1652f0').place(x=840, y=410)
# Ammount invested Entry
crypto_header = Entry(main, font=('veranda' ,15, 'bold'),width=35,justify='center')
crypto_header.place(x=780, y=470)
# Separate the two views
separator = ttk.Separator(main, orient='horizontal')
separator.place(x=0, y=395,relwidth=1.0)

# Menu funtions
file_menu.add_command(label = 'Full Report PDF', command = pdf_full_report)
file_menu.add_separator()
file_menu.add_command(label = 'Exit', command = main.quit)

query_investments()

main.mainloop()
