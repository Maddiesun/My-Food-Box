import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import json
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.pyplot import connect


def load_ingredients():
    if os.path.exists("ingredients.json"):
        with open("ingredients.json", "r") as file:
            return json.load(file)
    return []


def save_ingredients():
    with open("ingredients.json", "w") as file:
        json.dump(ingredients, file)


def add_ingredient():
    name = name_entry.get()
    purchase_date = purchase_date_entry.get()
    shelf_life_days = shelf_life_entry.get()
    ingredient_type = type_var.get()
    shelf_life_unit = unit_var.get()

    if not name or not purchase_date or not shelf_life_days or ingredient_type == "Select Type":
        messagebox.showerror("Error", "Please fill in all fields and select a type")
        return

    try:
        purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d")
        shelf_life_days = int(shelf_life_days)
        if shelf_life_unit == "Months":
            shelf_life_days *= 30
        elif shelf_life_unit == "Weeks":   
            shelf_life_days *= 7
    except ValueError:
        messagebox.showerror("Error", "Invalid date or shelf life")
        return

    expiration_date = purchase_date + timedelta(days=shelf_life_days)
    countdown_days = (expiration_date - datetime.now()).days

    if countdown_days < 0:
        countdown_days = 0

    ingredient = {
        "name": name,
        "purchase_date": purchase_date.strftime("%Y-%m-%d"),
        "shelf_life_days": shelf_life_days,
        "expiration_date": expiration_date.strftime("%Y-%m-%d"),
        "type": ingredient_type
    }

    ingredients.append(ingredient)
    save_ingredients()
    update_ingredients_list()
    update_data_visualization()


def update_ingredients_list():
    ingredients_list.delete(0, tk.END)
    
    for ingredient in ingredients:
        name = ingredient["name"]
        expiration_date = ingredient["expiration_date"]
        ingredient_type = ingredient["type"]
        
        countdown_days = (datetime.strptime(expiration_date, "%Y-%m-%d") - datetime.now()).days

        display_text = f"{name} ({ingredient_type}): {countdown_days} days left"
        if countdown_days == 1:
            display_text += " *"

        if countdown_days < 0:
            countdown_days = 0

        ingredients_list.insert(tk.END, display_text)
       
        current_index = ingredients_list.size() - 1
        ingredients_list.itemconfig(
            current_index, 
            {'bg': type_colors[ingredient_type]}
        )


def update_data_visualization():
    
    for widget in chart_frame.winfo_children():
        widget.destroy()

    
    category_counts = {category: 0 for category in type_colors.keys()}
    for ingredient in ingredients:
        category_counts[ingredient["type"]] += 1
    
    
    category_counts = {k: v for k, v in category_counts.items() if v > 0}

    
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    wedges, texts, autotexts = ax.pie(category_counts.values(), 
                                     labels=category_counts.keys(),
                                     colors=[type_colors[cat] for cat in category_counts.keys()],
                                     autopct='%1.1f%%',
                                     startangle=90)
    ax.set_title("Ingredients Distribution by Category")

    
    ax.axis('equal')

    
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()


def delete_selected():
    selection = ingredients_list.curselection()
    if not selection:
        messagebox.showinfo("Info", "Please select an ingredient to delete")
        return
    
    index = selection[0]
    ingredients.pop(index)
    save_ingredients()
    update_ingredients_list()
    update_data_visualization()

    
def delete_expired():
    global ingredients
    today = datetime.now()
    expired_count = 0
    
    
    active_ingredients = []
    for ingredient in ingredients:
        expiration_date = datetime.strptime(ingredient["expiration_date"], "%Y-%m-%d")
        if expiration_date >= today:
            active_ingredients.append(ingredient)
        else:
            expired_count += 1
    
    if expired_count > 0:
        ingredients = active_ingredients
        save_ingredients()
        update_ingredients_list()
        update_data_visualization()
        messagebox.showinfo("Cleanup Complete", f"Removed {expired_count} expired ingredient(s)")
    else:
        messagebox.showinfo("Cleanup Complete", "No expired ingredients found")

def clear_entries():
    name_entry.delete(0, tk.END)
    purchase_date_entry.delete(0, tk.END)
    shelf_life_entry.delete(0, tk.END)
    type_var.set("Select Type")
    unit_var.set("Days")

def insert_today_date():
    today = datetime.now().strftime("%Y-%m-%d")
    purchase_date_entry.delete(0, tk.END)
    purchase_date_entry.insert(0, today)
    


root = tk.Tk()
root.title("My Food Box")
root.configure(bg="#f0f0f0")
root.geometry("700x900")  


type_colors = {
    "Vegetables": "#6af76d",
    "Fruits": "#fc793d",
    "Meat": "#f595ac",
    "Eggs and Milk": "#95e2f5",
    "Seafood": "#1a62d6",
    "Drinks": "#f7f694",
    "Other": "#ba8970"
}


type_options = ["Select Type", "Vegetables", "Fruits", "Meat", "Eggs and Milk", "Seafood", "Drinks", "Other"]


ingredients = load_ingredients()


tk.Label(root, text="Ingredient Name:", bg="#f0f0f0").grid(row=0, column=0, sticky="w", padx=10, pady=5)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Purchase Date (YYYY-MM-DD):", bg="#f0f0f0").grid(row=1, column=0, sticky="w", padx=10, pady=5)
purchase_date_entry = tk.Entry(root)
purchase_date_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Shelf Life (days):", bg="#f0f0f0").grid(row=2, column=0, sticky="w", padx=10, pady=5)
shelf_life_entry = tk.Entry(root)
shelf_life_entry.grid(row=2, column=1, padx=10, pady=5)


tk.Label(root, text="Shelf Life Unit:", bg="#f0f0f0").grid(row=2, column=2, sticky="w", padx=10, pady=5)
unit_var = tk.StringVar(value="Days")
unit_menu = tk.OptionMenu(root, unit_var, "Days", "Weeks", "Months")  
unit_menu.grid(row=2, column=3, padx=10, pady=5)

tk.Label(root, text="Ingredient Type:", bg="#f0f0f0").grid(row=3, column=0, sticky="w", padx=10, pady=5)
type_var = tk.StringVar(value="Select Type")
type_menu = tk.OptionMenu(root, type_var, *type_options)
type_menu.grid(row=3, column=1, padx=10, pady=5)


add_button = tk.Button(root, text="Add Ingredient", command=add_ingredient, bg="#87CEEB")
add_button.grid(row=4, column=0, columnspan=2, pady=10)


delete_button = tk.Button(root, text="Delete Selected", command=delete_selected, bg="#ff9999")
delete_button.grid(row=4, column=2, pady=10)


cleanup_button = tk.Button(root, text="Remove Expired", command=delete_expired, bg="#ffd700")
cleanup_button.grid(row=4, column=3, pady=10)


ingredients_list = tk.Listbox(root, width=70, height=15)
ingredients_list.grid(row=5, column=0, columnspan=4, padx=10, pady=5, sticky="w")


chart_frame = tk.Frame(root, bg="#deb887")
chart_frame.grid(row=6, column=0, columnspan=4, pady=20)


update_ingredients_list()
update_data_visualization()


root.mainloop()