from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI()

class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    item_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)
    delivery_address: str = Field(..., min_length=10)
    delivery_slot: str = 'Morning'
    bulk_order: bool = False
    
class NewItem(BaseModel):
    name: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    unit: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    in_stock: bool = True
    
class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)
    delivery_slot: str = 'Morning'

@app.get('/')
def home():
    return {'message': 'Welcome to FreshMart Grocery'}

# DATA
items = [
    {'id': 1, 'name': 'Tomato', 'price': 30, 'unit': 'kg', 'category': 'Vegetable', 'in_stock': True},
    {'id': 2, 'name': 'Milk', 'price': 50, 'unit': 'litre', 'category': 'Dairy', 'in_stock': True},
    {'id': 3, 'name': 'Rice', 'price': 60, 'unit': 'kg', 'category': 'Grain', 'in_stock': True},
    {'id': 4, 'name': 'Apple', 'price': 120, 'unit': 'kg', 'category': 'Fruit', 'in_stock': False},
    {'id': 5, 'name': 'Eggs', 'price': 70, 'unit': 'dozen', 'category': 'Dairy', 'in_stock': True},
    {'id': 6, 'name': 'Potato', 'price': 25, 'unit': 'kg', 'category': 'Vegetable', 'in_stock': True},
]

@app.get('/items')
def get_items():
    in_stock_count = sum(1 for i in items if i['in_stock'])
    return {
        'items': items,
        'total': len(items),
        'in_stock_count': in_stock_count
    }
    
@app.get('/items/summary')
def items_summary():
    categories = {}
    in_stock = 0
    out_stock = 0

    for i in items:
        categories[i['category']] = categories.get(i['category'], 0) + 1
        if i['in_stock']:
            in_stock += 1
        else:
            out_stock += 1

    return {
        'total_items': len(items),
        'in_stock': in_stock,
        'out_of_stock': out_stock,
        'category_breakdown': categories
    }
    
def find_item(item_id: int):
    for i in items:
        if i['id'] == item_id:
            return i
    return None

def calculate_order_total(price: int, quantity: int, delivery_slot: str, bulk: bool):
    total = price * quantity
    original = total

    # Bulk discount
    if bulk and quantity >= 10:
        total = int(total * 0.92)  # 8% discount

    # Delivery charges
    if delivery_slot == 'Morning':
        total += 40
    elif delivery_slot == 'Evening':
        total += 60
    elif delivery_slot == 'Self':
        total += 0

    return original, total

def filter_items_logic(category=None, max_price=None, unit=None, in_stock=None):
    result = items

    if category is not None:
        result = [i for i in result if i['category'].lower() == category.lower()]

    if max_price is not None:
        result = [i for i in result if i['price'] <= max_price]

    if unit is not None:
        result = [i for i in result if i['unit'] == unit]

    if in_stock is not None:
        result = [i for i in result if i['in_stock'] == in_stock]

    return result

@app.get('/items/filter')
def filter_items(
    category: str = Query(None),
    max_price: int = Query(None),
    unit: str = Query(None),
    in_stock: bool = Query(None)
):
    result = filter_items_logic(category, max_price, unit, in_stock)

    return {
        'filtered_items': result,
        'count': len(result)
    }

@app.post('/items')
def add_item(new_item: NewItem, response: Response):

    # check duplicate name
    for i in items:
        if i['name'].lower() == new_item.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'error': 'Item already exists'}

    new_id = max(i['id'] for i in items) + 1

    item = {
        'id': new_id,
        'name': new_item.name,
        'price': new_item.price,
        'unit': new_item.unit,
        'category': new_item.category,
        'in_stock': new_item.in_stock
    }

    items.append(item)

    response.status_code = status.HTTP_201_CREATED
    return {'message': 'Item added', 'item': item}

@app.get('/items/search')
def search_items(keyword: str = Query(...)):
    results = [
        i for i in items
        if keyword.lower() in i['name'].lower()
        or keyword.lower() in i['category'].lower()
    ]

    return {
        'keyword': keyword,
        'total_found': len(results),
        'results': results
    }
    
@app.get('/items/sort')
def sort_items(
    sort_by: str = Query('price'),
    order: str = Query('asc')
):
    if sort_by not in ['price', 'name', 'category']:
        return {'error': 'Invalid sort_by'}

    if order not in ['asc', 'desc']:
        return {'error': 'Invalid order'}

    sorted_items = sorted(
        items,
        key=lambda x: x[sort_by],
        reverse=(order == 'desc')
    )

    return {
        'sort_by': sort_by,
        'order': order,
        'items': sorted_items
    }
    
@app.get('/items/page')
def paginate_items(
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1)
):
    start = (page - 1) * limit
    end = start + limit

    total = len(items)

    return {
        'page': page,
        'limit': limit,
        'total': total,
        'total_pages': -(-total // limit),
        'items': items[start:end]
    }

@app.get('/items/browse')
def browse_items(
    keyword: str = Query(None),
    category: str = Query(None),
    in_stock: bool = Query(None),
    sort_by: str = Query('price'),
    order: str = Query('asc'),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1)
):
    result = items

    # 1. Search
    if keyword:
        result = [
            i for i in result
            if keyword.lower() in i['name'].lower()
            or keyword.lower() in i['category'].lower()
        ]

    # 2. Category filter
    if category:
        result = [i for i in result if i['category'].lower() == category.lower()]

    # 3. Stock filter
    if in_stock is not None:
        result = [i for i in result if i['in_stock'] == in_stock]

    # 4. Sort
    if sort_by in ['price', 'name', 'category']:
        result = sorted(
            result,
            key=lambda x: x[sort_by],
            reverse=(order == 'desc')
        )

    # 5. Pagination
    total = len(result)
    start = (page - 1) * limit

    return {
        'keyword': keyword,
        'category': category,
        'in_stock': in_stock,
        'sort_by': sort_by,
        'order': order,
        'page': page,
        'limit': limit,
        'total_found': total,
        'total_pages': -(-total // limit),
        'items': result[start:start + limit]
    }

@app.get('/items/{item_id}')
def get_item(item_id: int):
    item = find_item(item_id)
    if not item:
        return {'error': 'Item not found'}
    return {'item': item}

@app.put('/items/{item_id}')
def update_item(
    item_id: int,
    response: Response,
    price: int = Query(None),
    in_stock: bool = Query(None)
):
    item = find_item(item_id)

    if not item:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Item not found'}

    if price is not None:
        item['price'] = price

    if in_stock is not None:
        item['in_stock'] = in_stock

    return {'message': 'Item updated', 'item': item}

@app.delete('/items/{item_id}')
def delete_item(item_id: int, response: Response):

    item = find_item(item_id)

    if not item:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Item not found'}

    # check if item is used in orders
    for o in orders:
        if o['item'] == item['name']:
            return {'error': 'Item has active orders, cannot delete'}

    items.remove(item)

    return {'message': f"{item['name']} deleted successfully"}

orders = []
order_counter = 1

@app.get('/orders')
def get_orders():
    return {
        'orders': orders,
        'total': len(orders)
    }    
    
@app.post('/orders')
def place_order(order: OrderRequest):
    global order_counter

    item = find_item(order.item_id)

    if not item:
        return {'error': 'Item not found'}

    if not item['in_stock']:
        return {'error': f"{item['name']} is out of stock"}

    original, total = calculate_order_total(
        item['price'],
        order.quantity,
        order.delivery_slot,
        order.bulk_order
    )

    new_order = {
        'order_id': order_counter,
        'customer_name': order.customer_name,
        'item': item['name'],
        'quantity': order.quantity,
        'unit': item['unit'],
        'delivery_slot': order.delivery_slot,
        'original_price': original,
        'total_cost': total,
        'status': 'confirmed'
    }

    orders.append(new_order)
    order_counter += 1

    return {
        'message': 'Order placed successfully',
        'order': new_order
    }    
    
@app.get('/orders/search')
def search_orders(customer_name: str = Query(...)):
    results = [
        o for o in orders
        if customer_name.lower() in o['customer_name'].lower()
    ]

    return {
        'customer_name': customer_name,
        'total_found': len(results),
        'orders': results
    }
    
@app.get('/orders/sort')
def sort_orders(order: str = Query('asc')):

    if order not in ['asc', 'desc']:
        return {'error': 'Invalid order'}

    sorted_orders = sorted(
        orders,
        key=lambda x: x['total_cost'],
        reverse=(order == 'desc')
    )

    return {
        'order': order,
        'orders': sorted_orders
    }
    
@app.get('/orders/page')
def paginate_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1)
):
    start = (page - 1) * limit
    total = len(orders)

    return {
        'page': page,
        'limit': limit,
        'total': total,
        'total_pages': -(-total // limit),
        'orders': orders[start:start + limit]
    }
    
cart = []

@app.post('/cart/add')
def add_to_cart(
    item_id: int = Query(...),
    quantity: int = Query(1)
):
    item = find_item(item_id)

    if not item:
        return {'error': 'Item not found'}

    if not item['in_stock']:
        return {'error': 'Item out of stock'}

    # check if already in cart
    for c in cart:
        if c['item_id'] == item_id:
            c['quantity'] += quantity
            c['subtotal'] = c['quantity'] * item['price']
            return {'message': 'Cart updated', 'cart_item': c}

    cart_item = {
        'item_id': item_id,
        'name': item['name'],
        'quantity': quantity,
        'price': item['price'],
        'subtotal': item['price'] * quantity
    }

    cart.append(cart_item)

    return {'message': 'Added to cart', 'cart_item': cart_item}

@app.get('/cart')
def view_cart():

    if not cart:
        return {'message': 'Cart is empty', 'items': [], 'grand_total': 0}

    total = sum(c['subtotal'] for c in cart)

    return {
        'items': cart,
        'total_items': len(cart),
        'grand_total': total
    }
    
@app.delete('/cart/{item_id}')
def remove_cart_item(item_id: int, response: Response):

    for c in cart:
        if c['item_id'] == item_id:
            cart.remove(c)
            return {'message': 'Item removed from cart'}

    response.status_code = status.HTTP_404_NOT_FOUND
    return {'error': 'Item not in cart'}

@app.post('/cart/checkout')
def checkout(data: CheckoutRequest, response: Response):

    global order_counter

    if not cart:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Cart is empty'}

    placed_orders = []
    grand_total = 0

    for c in cart:
        order = {
            'order_id': order_counter,
            'customer_name': data.customer_name,
            'item': c['name'],
            'quantity': c['quantity'],
            'delivery_address': data.delivery_address,
            'delivery_slot': data.delivery_slot,
            'total_cost': c['subtotal'],
            'status': 'confirmed'
        }

        orders.append(order)
        placed_orders.append(order)
        grand_total += c['subtotal']
        order_counter += 1

    cart.clear()

    response.status_code = status.HTTP_201_CREATED

    return {
        'message': 'Checkout successful',
        'orders': placed_orders,
        'grand_total': grand_total
    }