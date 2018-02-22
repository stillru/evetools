import sqlite3
import datetime
import sys
from esipy import App
from esipy import EsiClient

goods=["Tritanium", "Pyerite", "Mexallon", "Isogen", "Nocxium", "Oxygen"]
regions=["Metropolis", "Heimatar", "Molden Heath", "Derelik", "Curse"]


# API Client initialisation

# App.create(url, strict=True)
# with url = the swagger spec URL, leave strict to default
app = App.create(url="https://esi.tech.ccp.is/latest/swagger.json?datasource=tranquility")

# basic client, for public endpoints only
client = EsiClient(
    retry_requests=True,  # set to retry on http 5xx error (default False)
    header={'User-Agent': 'Still Console Marcet Client'},
    raw_body_only=False,  # default False, set to True to never parse response and only return raw JSON string content.
)


conn = sqlite3.connect('eve.db')

today = datetime.date.today()
now = datetime.datetime.now()

c = conn.cursor()

def sql_goods(name):
	def g_id(name):
		id = app.op['get_search'](
			categories="inventory_type",
			search=name,
			language="ru",
			strict=True,
		)
		response = client.request(id)
		return response.data.inventory_type

	global c
	c.execute('CREATE TABLE if not exists goods (good_name text, good_id long, UNIQUE(good_name, good_id))')
	c.execute("SELECT * FROM goods WHERE good_name = ?", (name,))
	data=c.fetchone()
	if data is None:
		c.execute('INSERT OR IGNORE INTO goods(good_name, good_id) values (? , ?)', [str(name), str(g_id(name))])
	else:
		print name, "exist on table. Skipping..."

def sql_region(name):
	def r_id(name):
		id = app.op['get_search'](
			categories="region",
			search=name,
			language="ru",
			strict=True,
		)

		response = client.request(id)
		return response.data.region

	global c
	c.execute('CREATE TABLE if not exists regions (region_name text, region_id int, UNIQUE(region_name, region_id))')
	c.execute("SELECT * FROM regions WHERE region_name = ?", (name,))
	data=c.fetchone()
	if data is None:
		c.execute('INSERT OR IGNORE INTO regions(region_name, region_id) values (? , ?)', [str(name), str(r_id(name))])
	else:
		print name, "exist on table. Skipping..."

def orders(region,b):
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
	i=0
	while i < len(orders.data):
		c.execute('INSERT OR IGNORE INTO orders(volume_remain, type_id, order_id, issued, price, min_volume, is_buy_order, range, duration, volume_total, location_id, region_id) values (? , ? , ?, ? , ? , ? , ? , ? , ? , ? , ? , ?)', [
		orders.data[i].volume_remain,
		orders.data[i].type_id,
		orders.data[i].order_id,
		str(orders.data[i].issued),
		orders.data[i].price,
		orders.data[i].min_volume,
		orders.data[i].is_buy_order,
		orders.data[i].range,
		orders.data[i].duration,
		orders.data[i].volume_total,
		orders.data[i].location_id,
		a[0]
		])
		c.execute('UPDATE orders SET volume_remain = ?, type_id = ?, issued = ?, price = ?, min_volume = ?, is_buy_order = ?, range = ?, duration = ?, volume_total = ?, location_id = ?, region_id = ? WHERE order_id = ?', [
		orders.data[i].volume_remain,
		orders.data[i].type_id,
		str(orders.data[i].issued),
		orders.data[i].price,
		orders.data[i].min_volume,
		orders.data[i].is_buy_order,
		orders.data[i].range,
		orders.data[i].duration,
		orders.data[i].volume_total,
		orders.data[i].location_id,
		a[0],
		orders.data[i].order_id
		])
		print "Order", orders.data[i].order_id, "updated!"
		#print b[0], "Order", orders.data[i].order_id, "imported!"
		i+=1
	print i, "Orders imported!"


i=0
while i < len(regions):
	sql_region(regions[i])
	i += 1

i=0
while i < len(goods):
	sql_goods(goods[i])
	i += 1

for g in range(len(goods)):
	print goods[g], "workin!"
	for r in range(len(regions)):
		print regions[r], "workin!",
		orders(regions[r],goods[g])


conn.commit()
conn.close()