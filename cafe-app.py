from flask import Flask, request, jsonify

app = Flask(__name__)



menu = [
    {"id": 1, "name": "Плов",      "category": "main",  "price": 40, "available": True},
    {"id": 2, "name": "Шурпа",     "category": "soup",  "price": 30, "available": True},
    {"id": 3, "name": "Самса",     "category": "snack", "price": 10, "available": True},
    {"id": 4, "name": "Чай",       "category": "drink", "price": 5,  "available": True},
    {"id": 5, "name": "Кофе",      "category": "drink", "price": 15, "available": False},
]


@app.route("/menu", methods = ["GET", "POST"])
def get_menu():
    if request.method == "GET":
        result = menu

        available = request.args.get("available")
        if available is not None:
            if available == "true":
                result = [dish for dish in result if dish["available"] == True]
            if available == "false":
                result = [dish for dish in result if dish["available"] == False]


        max_price = request.args.get("max_price")
        if max_price is not None:
            max_price = int(max_price)
            result = [dish for dish in result if dish["price"] <= max_price]

        return jsonify(result)
    else:
        new_dish = request.get_json()
        if new_dish.get("name") is None:
            return {"error": "Field 'name' is required"}, 400
        elif new_dish.get("category") is None:
            return {"error": "Field 'category' is required"}, 400
        elif new_dish.get("price") is None:
            return {"error": "Field 'price' is required"}, 400
        else:
            if new_dish.get("available") is None:
                new_dish["available"] = True
            new_dish["id"] = len(menu)+1
            menu.append(new_dish)
            return f"New dish has been added to the menu", 200


@app.route("/menu/<int:id>", methods = ["GET", "PATCH", "DELETE"])
def get_menu_by_id(id):
    if request.method == "GET":
        dish = 0
        if id <= len(menu):
            dish = 0
            while dish <= len(menu):
                if menu[dish]["id"] == id:
                    return menu[dish]
                    break
                else: dish+=1
        else:
            return {"error": "Dish not found"}, 404
    elif request.method == "PATCH":
        patched = request.get_json()
        if patched.get("name") is not None:
            menu[id-1]["name"] = patched.get("name")
        if patched.get("category") is not None:
            menu[id-1]["category"] = patched.get("category")
        if patched.get("price") is not None:
            menu[id-1]["price"] = patched.get("price")
        return f"Dish has been patched", 200
    else:
        if id <= len(menu):
            del menu[id-1]
            return {"status": "deleted", "id": id}
        else:
            return 404


@app.route("/menu/category/<name>")
def get_category(name):
    result = []
    for dish in menu:
        if dish["category"] == name:
            result.append(dish)
    return result

@app.route("/menu/stats")
def get_stats():
    statistics = {"total": len(menu),
                  "available": 0,
                  "unavailable": 0,
                  "avg_price": 0
                  }
    categories = {}
    total_price = 0
    for dish in menu:
        if dish["available"] == True:
            statistics["available"] += 1
        else: statistics["unavailable"] += 1
        if dish["category"] not in categories:
            categories[dish["category"]] = 1
        else: categories[dish["category"]] += 1
        total_price += dish["price"]
    statistics["avg_price"] = total_price/len(menu)
    statistics["categories"] = categories
    return jsonify(statistics)


@app.route("/menu/<int:id>/toggle", methods = ["POST"])
def toggle(id):
    for dish in menu:
        if dish["id"] == id:
            menu[id-1]["available"] = not dish["available"]
        else:
            return {"error": "Блюдо с таким id не найдено"}, 404


if __name__ == "__main__":
    app.run(debug=True)