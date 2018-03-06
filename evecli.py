# -*- coding: utf-8 -*-
"""Script for capturing data from ESI API (EVE Online)
Example:
    	::
        $ python evecli.py
Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension
"""
import sqlite3
import datetime
from esipy import App
from esipy import EsiClient

goods = ["Tritanium", "Pyerite", "Mexallon", "Isogen", "Nocxium", "Oxygen"]
"""list: List of trading goods.
"""
regions = ["Metropolis", "Heimatar", "Molden Heath", "Derelik", "Curse"]
"""list: List of regions.
"""
app = App.create(url="https://esi.tech.ccp.is/latest/swagger.json?datasource=tranquility")
client = EsiClient(
    retry_requests=True,
    header={'User-Agent': 'Still Console Marcet Client'},
    raw_body_only=False,
)
conn = sqlite3.connect('eve.db')
today = datetime.date.today()
now = datetime.datetime.now()
c = conn.cursor()
def g_id(name):
    """ Internal function. Returns a response from ESI API with an inventory_type value.
    Args:
        name (str): Region name.

    Returns:
        Data with goods type id.
    """
    gid = app.op['get_search'](
        categories="inventory_type",
        search=name,
        language="ru",
        strict=True,
        )
    response = client.request(gid)
    return response.data.inventory_type
def sql_goods(name):
    """ The function of searching inventory_type for each item of the goods list.
    The internal function ``g_id(name)`` is called, which returns a response from ESI API with an inventory_type value.
    Writes this value to sqlite. If there is such a record in the database - ignore.
    Args:
        name (str): Goods name.
    """
    c.execute('CREATE TABLE if not exists goods (good_name text, good_id long, UNIQUE(good_name, good_id))')
    c.execute("SELECT * FROM goods WHERE good_name = ?", (name,))
    data = c.fetchone()
    if data is None:
        c.execute('INSERT OR IGNORE INTO goods(good_name, good_id) values (? , ?)', [str(name), str(g_id(name))])
    else:
        pass
def r_id(name):
    """ Internal function. Returns a response from ESI API with an region value.

    Args:
        name (str): Region name.

    Returns:
        Data with region id.
        """
    rid = app.op['get_search'](
        categories="region",
        search=name,
        language="ru",
        strict=True,
        )
    response = client.request(rid)
    return response.data.region
def sql_region(name):
    """ The function of searching region for each item of the regions list.
    The internal function ``r_id(name)`` is called, which returns a response from ESI API with an region value.
    Writes this value to sqlite. If there is such a record in the database - ignore.
    Args:
        name (str): Region name.
    """
    c.execute('CREATE TABLE if not exists regions (region_name text, region_id int, UNIQUE(region_name, region_id))')
    c.execute("SELECT * FROM regions WHERE region_name = ?", (name,))
    data = c.fetchone()
    if data is None:
        c.execute('INSERT OR IGNORE INTO regions(region_name, region_id) values (? , ?)', [str(name), str(r_id(name))])
    else:
        pass
def orders(region, good):
    """ Orgers pickup from ESI API
    All orders are placed to SQL DB for later usage.

    Args:
        region (str): Region id.
        good (str): Goods id.
    """
    c.execute('CREATE TABLE if not exists orders(volume_remain long,type_id long,order_id int,issued datetime,price int,min_volume int,is_buy_order text,range int,duration int,volume_total int,location_id text, region_id int, UNIQUE(order_id))')
    c.execute('SELECT region_id FROM regions WHERE region_name = ?', (region,))
    a = c.fetchone()
    c.execute('SELECT good_id FROM goods WHERE good_name = ?', (good,))
    b = c.fetchone()
    p = app.op['get_markets_region_id_orders'](
        region_id=a[0],
        type_id=b[0],
    )
    orders = client.request(p)
    i = 0
    while i < len(orders.data): 
        c.execute('INSERT OR IGNORE INTO orders(volume_remain, type_id, order_id, issued, price, min_volume, is_buy_order, range, duration, volume_total, location_id, region_id) values (? , ? , ?, ? , ? , ? , ? , ? , ? , ? , ? , ?)', [orders.data[i].volume_remain, orders.data[i].type_id, orders.data[i].order_id, str(orders.data[i].issued), orders.data[i].price, orders.data[i].min_volume, orders.data[i].is_buy_order, orders.data[i].range, orders.data[i].duration, orders.data[i].volume_total, orders.data[i].location_id, a[0]])
        c.execute('UPDATE orders SET volume_remain = ?, type_id = ?, issued = ?, price = ?, min_volume = ?, is_buy_order = ?, range = ?, duration = ?, volume_total = ?, location_id = ?, region_id = ? WHERE order_id = ?', [orders.data[i].volume_remain, orders.data[i].type_id, str(orders.data[i].issued), orders.data[i].price, orders.data[i].min_volume, orders.data[i].is_buy_order, orders.data[i].range, orders.data[i].duration, orders.data[i].volume_total, orders.data[i].location_id, a[0], orders.data[i].order_id])
        i += 1
i = 0
while i < len(regions):
    sql_region(regions[i])
    i += 1
i = 0
while i < len(goods):
    sql_goods(goods[i])
    i += 1
for g in range(len(goods)):
    print goods[g], "workin!"
    for r in range(len(regions)):
        orders(regions[r], goods[g])
conn.commit()
conn.close()
