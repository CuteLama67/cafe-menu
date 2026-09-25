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

        conn.close()

        dishes = []
        for row in rows:
            dishes.append({
                "id": row["id"],
                "name": row["name"],
                "category": row["category"],
                "price": row["price"],
                "available": bool(row["available"])
            })

        return jsonify(dishes)

    #     sort = request.args.get("sorted")
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
    #             return {"error": "'sorted' parameter is wrong"}, 404

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
    if request.method == "GET":
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM dishes WHERE id = ?", (id,))
            row = cursor.fetchone()

            conn.close()

            if row is None:
                return jsonify({"error": "Dish not found"}), 404

            dish = {
                "id": row["id"],
                "name": row["name"],
                "category": row["category"],
                "price": row["price"],
                "available": bool(row["available"])
            }
            return jsonify(dish)
#     elif request.method == "PATCH":
#         patched = request.get_json()
#         if patched.get("name") is not None:
#             menu[id-1]["name"] = patched.get("name")
#         if patched.get("category") is not None:
#             menu[id-1]["category"] = patched.get("category")
#         if patched.get("price") is not None:
#             menu[id-1]["price"] = patched.get("price")
#         return f"Dish has been patched", 200
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


# @app.route("/menu/category/<name>")
# def get_category(name):
#     result = []
#     for dish in menu:
#         if dish["category"] == name:
#             result.append(dish)
#     return result

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