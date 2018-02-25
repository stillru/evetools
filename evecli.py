# -*- coding: utf-8 -*-
"""Example Google style docstrings.
This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.
Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::
        $ python example_google.py
Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.
Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.
        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.
Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension
.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html
"""
import sqlite3
import datetime
from esipy import App
from esipy import EsiClient
goods = ["Tritanium", "Pyerite", "Mexallon", "Isogen", "Nocxium", "Oxygen"]
regions = ["Metropolis", "Heimatar", "Molden Heath", "Derelik", "Curse"]
# API Client initialisation
# App.create(url, strict=True)
# with url = the swagger spec URL, leave strict to default
app = App.create(url="https://esi.tech.ccp.is/latest/swagger.json?datasource=tranquility")
# basic client, for public endpoints only
client = EsiClient(
    retry_requests=True,
    header={'User-Agent': 'Still Console Marcet Client'},
    raw_body_only=False,
    )
conn = sqlite3.connect('eve.db')
today = datetime.date.today()
now = datetime.datetime.now()
c = conn.cursor()
def sql_goods(name):
    """Example function with types documented in the docstring.
    `PEP 484`_ type annotations are supported. If attribute, parameter, and
    return types are annotated according to `PEP 484`_, they do not need to be
    included in the docstring:
    Args:
        name (str): The first parameter.
    Returns:
        None
    .. _PEP 484:
        https://www.python.org/dev/peps/pep-0484/
    """
    def g_id(name):
        """Example function with types documented in the docstring.
        `PEP 484`_ type annotations are supported. If attribute, parameter, and
        return types are annotated according to `PEP 484`_, they do not need to be
        included in the docstring:
        Args:
            name (str): The first parameter.
        Returns:
            None
        .. _PEP 484:
            https://www.python.org/dev/peps/pep-0484/
        """
        cli = app.op['get_search'](
            categories="inventory_type",
            search=name,
            language="ru",
            strict=True,
        )
        response = client.request(cli)
        return response.data.inventory_type
    c.execute('CREATE TABLE if not exists goods (good_name text, good_id long, UNIQUE(good_name, good_id))')
    c.execute("SELECT * FROM goods WHERE good_name = ?", (name,))
    data = c.fetchone()
    if data is None:
        c.execute('INSERT OR IGNORE INTO goods(good_name, good_id) values (? , ?)', [str(name), str(g_id(name))])
    else:
        print name, "exist on table. Skipping..."
def sql_region(name):
    """ Docstring
    """
    def r_id(name):
        """ Docstring
        """
        rid = app.op['get_search'](
            categories="region",
            search=name,
            language="ru",
            strict=True,
        )
        response = client.request(rid)
        return response.data.region
    c.execute('CREATE TABLE if not exists regions (region_name text, region_id int, UNIQUE(region_name, region_id))')
    c.execute("SELECT * FROM regions WHERE region_name = ?", (name,))
    data = c.fetchone()
    if data is None:
        c.execute('INSERT OR IGNORE INTO regions(region_name, region_id) values (? , ?)', [str(name), str(r_id(name))])
    else:
        print name, "exist on table. Skipping..."
def orders(region, b):
    """ Docstring
    """
    c.execute('CREATE TABLE if not exists orders(volume_remain long,type_id long,order_id int,issued datetime,price int,min_volume int,is_buy_order text,range int,duration int,volume_total int,location_id text, region_id int, UNIQUE(order_id))')
    c.execute('SELECT region_id FROM regions WHERE region_name = ?', (region,))
    a = c.fetchone()
    c.execute('SELECT good_id FROM goods WHERE good_name = ?', (b,))
    b = c.fetchone()
    p = app.op['get_markets_region_id_orders'](
        region_id=a[0],
        type_id=b[0],
    )
    orders = client.request(p)
    i = 0
    while i < len(orders.data):
        c.execute('INSERT OR IGNORE INTO orders(volume_remain, type_id, order_id, issued, price, min_volume, is_buy_order, range, duration, volume_total, location_id, region_id) values (? , ? , ?, ? , ? , ? , ? , ? , ? , ? , ? , ?)', [orders.data[i].volume_remain, orders.data[i].type_id, str(orders.data[i].issued), orders.data[i].price, orders.data[i].min_volume, orders.data[i].is_buy_order, orders.data[i].range, orders.data[i].duration, orders.data[i].volume_total, orders.data[i].location_id, a[0], orders.data[i].order_id])
        c.execute('UPDATE orders SET volume_remain = ?, type_id = ?, issued = ?, price = ?, min_volume = ?, is_buy_order = ?, range = ?, duration = ?, volume_total = ?, location_id = ?, region_id = ? WHERE order_id = ?', [orders.data[i].volume_remain, orders.data[i].type_id, str(orders.data[i].issued), orders.data[i].price, orders.data[i].min_volume, orders.data[i].is_buy_order, orders.data[i].range, orders.data[i].duration, orders.data[i].volume_total, orders.data[i].location_id, a[0], orders.data[i].order_id])
        print "Order", orders.data[i].order_id, "updated!"
        #print b[0], "Order", orders.data[i].order_id, "imported!"
        i += 1
    print i, "Orders imported!"
i = 0
while i < len(regions):
    sql_region(regions[i])
    i += 1
i = 0
while i < len(goods):
    sql_goods(goods[i])
    i += 1
go = 0
re = 0
while go < len(goods):
    print goods[go], "workin!"
    while re < len(regions):
        print regions[re], "workin!",
        orders(regions[re], goods[go])
        re += 1
    go += 1
conn.commit()
conn.close()
