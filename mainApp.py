from esipy import App
from esipy import EsiClient
import json
from statistics import median
#import numpy


# Statitc lists
goods=["Tritanium", "Pyerite", "Mexallon", "Isogen", "Nocxium", "Zydrine", "Megacyte", "Morphite", "Oxygen"]
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

# Functions
def append(value,key):
	goods.append(value)
	return


# API Calls

class Miniral(object):
	"""docstring for Miniral"""

	def g_id(self,name):
		id = app.op['get_search'](
			categories="inventory_type",
			search=name,
			language="ru",
			strict=True,
		)

		response = client.request(id)
		return response.data.inventory_type

	def __init__(self, *args, **kwargs):
		if len(args) == 1 and hasattr(args[0], '__iter__'):
			ist.__init__(self, args[0])
		else:
			list.__init__(self, args)
		self.__dict__.update(kwargs)

	def __getitem__(self, item):
		return getattr(self, item)

	def __new__(self, *args, **kwargs):
		return super(Mineral, self).__new__(self, args, kwargs)

class Region(object):
	"""docstring for Region"""

	def r_id(self,name):
		id = app.op['get_search'](
			categories="region",
			search=name,
			language="ru",
			strict=True,
		)

		response = client.request(id)
		return response.data.region

	def __init__(self, *args, **kwargs):
		if len(args) == 1 and hasattr(args[0], '__iter__'):
			list.__init__(self, args[0])
		else:
			list.__init__(self, args)
		self.__dict__.update(kwargs)

	def __getitem__(self, item):
		return getattr(self, item)

	def __new__(self, *args, **kwargs):
		return super(Region, self).__new__(self, args, kwargs)


def jdefault(o):
    if isinstance(o, set):
        return list(o)
    return o.__dict__

class Container(object):
	pass 

class L(list):
    """
    A subclass of list that can accept additional attributes.
    Should be able to be used just like a regular list.

    The problem:
    a = [1, 2, 4, 8]
    a.x = "Hey!" # AttributeError: 'list' object has no attribute 'x'

    The solution:
    a = L(1, 2, 4, 8)
    a.x = "Hey!"
    print a       # [1, 2, 4, 8]
    print a.x     # "Hey!"
    print len(a)  # 4

    You can also do these:
    a = L( 1, 2, 4, 8 , x="Hey!" )                 # [1, 2, 4, 8]
    a = L( 1, 2, 4, 8 )( x="Hey!" )                # [1, 2, 4, 8]
    a = L( [1, 2, 4, 8] , x="Hey!" )               # [1, 2, 4, 8]
    a = L( {1, 2, 4, 8} , x="Hey!" )               # [1, 2, 4, 8]
    a = L( [2 ** b for b in range(4)] , x="Hey!" ) # [1, 2, 4, 8]
    a = L( (2 ** b for b in range(4)) , x="Hey!" ) # [1, 2, 4, 8]
    a = L( 2 ** b for b in range(4) )( x="Hey!" )  # [1, 2, 4, 8]
    a = L( 2 )                                     # [2]
    """
    def __new__(self, *args, **kwargs):
        return super(L, self).__new__(self, args, kwargs)

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and hasattr(args[0], '__iter__'):
            list.__init__(self, args[0])
        else:
            list.__init__(self, args)
        self.__dict__.update(kwargs)

    def __call__(self, **kwargs):
        self.__dict__.update(kwargs)
        return self

goods_t = []
for i in goods:
	#m = Miniral(i)
	#print m.name , m.id #Debug
	#print(json.dumps(m, default=jdefault,indent=4))
	Miniral(i)

regions_t = []
for r in regions:
	#print r.name , r.id #Debug
	#print(json.dumps(r, default=jdefault,indent=4))
	regions_t.append(Region(r))
for ri in regions_t:
	print "==========="
	print ri.name
	for gi in goods_t:
		print gi.name, ":\t",
		p = app.op['get_markets_region_id_orders'](
			region_id=ri['id'],
			type_id=gi['id'],
			order_type='buy',
		)

		response = client.request(p)
		print "Prices in region:",
		prices=[]
		for i in response.data:
			prices.append(i.price)
			gi.region += ri.name
			gi.region.price += i.price
			print "Median is", median(prices), "ISK,\tMin/Max price is" , min(prices), max(prices)
		print_json = json.dumps(gi, default=jdefault)
		print print_json
for h in goods_t:
	print_json = json.dumps(h, default=jdefault)
	print print_json	
	