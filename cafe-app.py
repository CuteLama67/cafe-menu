import sqlite3
from flask import Flask, request, jsonify
import random

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("menu.db")
    conn.row_factory = sqlite3.Row
    return conn



@app.route("/menu", methods = ["GET", "POST"])
def get_menu():
    if request.method == "GET":
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM dishes")
        rows = cursor.fetchall()
        query_param = "SELECT * FROM dishes"
        connections = []
        parameters = []

        category = request.args.get("category")    
        if category:
            connections.append("category = ?")
            parameters.append(category)

        max_price = request.args.get("max_price")
        if max_price:
            connections.append("price <= ?")
            parameters.append(max_price)

        available = request.args.get("available")
        if available:
            connections.append("available = ?")
            parameters.append(available)

        if connections:
            query_param += " WHERE " + " AND ".join(connections)
            cursor.execute(query_param, tuple(parameters))
            rows = cursor.fetchall()

        dishes = []
        for row in rows:
            dishes.append({
                        "id": row["id"],
                        "name": row["name"],
                        "category": row["category"],
                        "price": row["price"],
                        "available": bool(row["available"])
                        })

        conn.close()
        return jsonify(dishes)


    else:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        name = data.get("name")
        category = data.get("category")
        price = data.get("price")
        available = data.get("available", True)

        if not name or not category or price is None:
            return jsonify({"error": "Fields name, category, price are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO dishes (name, category, price, available) VALUES (?, ?, ?, ?)",
            (name, category, price, 1 if available else 0)
        )

        new_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            "id": new_id,
            "name": name,
            "category": category,
            "price": price,
            "available": available
        }), 201


@app.route("/menu/<int:id>", methods = ["GET", "PATCH", "DELETE"])
def get_menu_by_id(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dishes WHERE id = ?", (id,))
    dish = {}
    row = cursor.fetchone()
    if row is None:
        return jsonify({"error": "Dish not found"}), 404
    if request.method == "GET":
            conn.close()

            dish = {
                "id": row["id"],
                "name": row["name"],
                "category": row["category"],
                "price": row["price"],
                "available": bool(row["available"])
            }
            return jsonify(dish)
    
    elif request.method == "PATCH":
        query_param = "UPDATE dishes SET "
        data = request.get_json()
        connections = []
        parameters = []
        if "name" in data:
            connections.append("name = ?")
            parameters.append(data["name"])
        
        if "category" in data:
            connections.append("category = ?")
            parameters.append(data["category"])
        
        if "price" in data:
            connections.append("price = ?")
            parameters.append(data["price"])
        
        if "available" in data:
            connections.append("available = ?")
            parameters.append(data["available"])
        parameters.append(id)
        if connections:
            query_param += " , ".join(connections) + " WHERE id = ? "
            cursor.execute(query_param, tuple(parameters))
            conn.commit()
            conn.close()
        return f"Dish has been patched"

    else:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM dishes WHERE id = ?", (id,))

        conn.commit()

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Dish not found"}), 404
        else:
            conn.close()
            return jsonify({"status": "deleted", "id": id})




# @app.route("/menu/stats")
# def get_stats():
#     statistics = {"total": len(menu),
#                   "available": 0,
#                   "unavailable": 0,
#                   "avg_price": 0
#                   }
#     categories = {}
#     total_price = 0
#     for dish in menu:
#         if dish["available"] == True:
#             statistics["available"] += 1
#         else: statistics["unavailable"] += 1
#         if dish["category"] not in categories:
#             categories[dish["category"]] = 1
#         else: categories[dish["category"]] += 1
#         total_price += dish["price"]
#     statistics["avg_price"] = total_price/len(menu)
#     statistics["categories"] = categories
#     return jsonify(statistics)


# @app.route("/menu/<int:id>/toggle", methods = ["POST"])
# def toggle(id):
#     for dish in menu:
#         if dish["id"] == id:
#             menu[id-1]["available"] = not dish["available"]
#         else:
#             return {"error": "Блюдо с таким id не найдено"}, 404

# @app.route("/menu/sorted")
# def sorted_menu():
#     sort = request.args.get("show")
#     if sort is not None:
#         if sort == "cheapest":
#             max = 1000000
#             dish_cheap = {}
#             for dish in menu:
#                 if max >= dish["price"]:
#                     max = dish["price"]
#                     dish_cheap = dish
#             return dish_cheap
#         elif sort == "expensive":
#             min = 0
#             dish_exp = {}
#             for dish in menu:
#                 if min <= dish["price"]:
#                     min = dish["price"]
#                     dish_exp = dish
#             return dish_exp
#         elif sort == "random":
#             rand = random.raьdint(0, len(menu)-1)
#             return menu[rand]
#         else:
#             return {"error": "'show' parameter is wrong"}, 404


if __name__ == "__main__":
    app.run(debug=True)