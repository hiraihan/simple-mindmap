import tkinter as tk
from tkinter import filedialog, messagebox
import networkx as nx
import matplotlib.pyplot as plt
import json

mindmap = nx.DiGraph()

topic_categories = {}  # { "Python": "Language", "Tkinter": "GUI" }
notes = {}  # Dictionary to store notes for each topic
category_colors = {
    "Language": "lightblue",
    "Framework": "lightgreen",
    "Tool": "lightcoral",
    "Lesson": "lightgoldenrodyellow",
    "Subject": "lightyellow",
    "Library": "lightpink",
    "Other": "lightgray"
}

# === FUNCTIONS ===
def add_topic():
    topic = entry_topic.get().strip()
    category = category_var.get()

    if not topic:
        messagebox.showwarning("Warning", "Topic cannot be empty.")
        return

    if " " in topic:
        messagebox.showwarning("Invalid", "Topic name should not contain spaces.")
        return

    if topic in mindmap.nodes:
        messagebox.showwarning("Duplicate", f"Topic '{topic}' already exists.")
        return

    mindmap.add_node(topic)
    topic_categories[topic] = category if category else "Other"
    messagebox.showinfo("Success", f"Topic '{topic}' added with category '{topic_categories[topic]}'.")
    entry_topic.delete(0, tk.END)
    category_var.set("Other")


def connect_topics():
    parent = entry_parent.get().strip()
    child = entry_child.get().strip()
    if not parent or not child:
        messagebox.showwarning("Input Required", "Both parent and child topics are required.")
        return
    if parent not in mindmap.nodes:
        messagebox.showerror("Topic Not Found", f"Parent topic '{parent}' does not exist.")
        return
    if child not in mindmap.nodes:
        messagebox.showerror("Topic Not Found", f"Child topic '{child}' does not exist.")
        return
    if mindmap.has_edge(child, parent):
        messagebox.showerror("Invalid Connection", f"Cannot connect '{parent}' to '{child}' because '{child}' is already connected to '{parent}'.")
        return
    if mindmap.has_edge(parent, child):
        messagebox.showinfo("Already Connected", f"'{parent}' is already connected to '{child}'.")
        return

    mindmap.add_edge(parent, child)
    messagebox.showinfo("Connected", f"Connected '{parent}' to '{child}'.")

def show_mindmap():
    plt.clf()
    
    # Layout hierarki dari parent ke child (top-down)
    pos = nx.nx_agraph.graphviz_layout(mindmap, prog="dot")
    
    # Gambar node dan edge
    categories = nx.get_node_attributes(mindmap, "category")
    colors = [mindmap.nodes[n].get("color", "lightblue") for n in mindmap.nodes]

    nx.draw(mindmap, pos, with_labels=True, node_color=colors, node_size=2000, font_size=10, font_weight='bold')

    plt.title("Mindmap View", fontsize=14)
    plt.tight_layout()
    plt.show()



def show_topic_dialog(topic):
    top = tk.Toplevel(root)
    top.title(f"Details: {topic}")

    category = topic_categories.get(topic, "Other")
    current_note = notes.get(topic, "")

    tk.Label(top, text=f"Topic: {topic}", font=("Arial", 12, "bold")).pack(pady=5)
    tk.Label(top, text=f"Category: {category}", font=("Arial", 10)).pack(pady=5)

    tk.Label(top, text="Note:").pack()
    note_text = tk.Text(top, width=40, height=5)
    note_text.pack()
    note_text.insert("1.0", current_note)

    def save_note():
        notes[topic] = note_text.get("1.0", tk.END).strip()
        messagebox.showinfo("Saved", f"Note saved for '{topic}'")
        top.destroy()

    tk.Button(top, text="Save Note", command=save_note).pack(pady=5)



def save_mindmap():
    file_path = filedialog.asksaveasfilename(defaultextension=".json")
    if file_path:
        data = {
            "nodes": list(mindmap.nodes),
            "edges": list(mindmap.edges),
            "categories": topic_categories,
            "notes": notes
        }
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo("Saved", f"Mind map saved to: {file_path}")


def load_mindmap():
    global mindmap, topic_categories, notes
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, "r") as f:
            data = json.load(f)

        mindmap = nx.DiGraph()
        mindmap.add_nodes_from(data.get("nodes", []))
        mindmap.add_edges_from(data.get("edges", []))

        topic_categories = data.get("categories", {})
        notes = data.get("notes", {})

        messagebox.showinfo("Loaded", f"Mind map loaded from: {file_path}")



def rename_topic():
    old_name = entry_old_name.get().strip()
    new_name = entry_new_name.get().strip()

    if not old_name or not new_name:
        messagebox.showwarning("Warning", "Both old and new topic names are required.")
        return

    if old_name not in mindmap.nodes:
        messagebox.showwarning("Not Found", f"Topic '{old_name}' does not exist.")
        return

    if new_name in mindmap.nodes:
        messagebox.showwarning("Duplicate", f"Topic '{new_name}' already exists.")
        return

    if " " in new_name:
        messagebox.showwarning("Invalid", "New topic name should not contain spaces.")
        return

    # Salin edge dari topik lama
    neighbors = list(mindmap.successors(old_name))
    predecessors = list(mindmap.predecessors(old_name))

    # Hapus dan tambah node
    mindmap.remove_node(old_name)
    mindmap.add_node(new_name)

    # Tambahkan kembali edge
    for n in neighbors:
        mindmap.add_edge(new_name, n)
    for p in predecessors:
        mindmap.add_edge(p, new_name)

    # Salin kategori
    topic_categories[new_name] = topic_categories.pop(old_name, "Other")

    messagebox.showinfo("Renamed", f"Topic '{old_name}' renamed to '{new_name}'.")
    entry_old_name.delete(0, tk.END)
    entry_new_name.delete(0, tk.END)

def delete_topic():
    name = entry_delete.get().strip()
    if name in mindmap.nodes:
        mindmap.remove_node(name)
        messagebox.showinfo("Deleted", f"Topic '{name}' deleted.")
        entry_delete.delete(0, tk.END)
    else:
        messagebox.showwarning("Warning", "Topic not found.")


def export_to_png():
    if len(mindmap.nodes) == 0:
        messagebox.showinfo("Info", "Mind map is empty.")
        return

    pos = nx.spring_layout(mindmap)

    node_colors = []
    for node in mindmap.nodes:
        category = topic_categories.get(node, "Other")
        color = category_colors.get(category, "lightgray")
        node_colors.append(color)

    plt.figure(figsize=(10, 7))
    nx.draw(mindmap, pos, with_labels=True, node_color=node_colors,
            node_size=2000, font_size=10, font_weight='bold', arrows=True)
    plt.title("Mind Map")

    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        plt.savefig(file_path, bbox_inches='tight')
        messagebox.showinfo("Saved", f"Mind map exported as image:\n{file_path}")
    plt.close()


def search_topic():
    keyword = entry_search.get().strip()
    if keyword not in mindmap.nodes:
        messagebox.showinfo("Not Found", f"Topic '{keyword}' not found.")
        return

    pos = nx.spring_layout(mindmap, seed=42)
    node_colors = []

    for node in mindmap.nodes:
        if node == keyword:
            node_colors.append("yellow")  # Highlight
        else:
            category = topic_categories.get(node, "Other")
            color = category_colors.get(category, "lightgray")
            node_colors.append(color)

    fig, ax = plt.subplots(figsize=(10, 7))
    nx.draw(mindmap, pos, with_labels=True, node_color=node_colors,
            node_size=2000, font_size=10, font_weight='bold', arrows=True, ax=ax)
    plt.title(f"Search Result for '{keyword}'")

    # Buat mapping posisi
    node_positions = {node: pos[node] for node in mindmap.nodes}

    def on_click(event):
        if event.inaxes:
            x_click, y_click = event.xdata, event.ydata
            for node, (x, y) in node_positions.items():
                # Radius klik sekitar node
                if (x - x_click)**2 + (y - y_click)**2 < 0.05:
                    show_topic_dialog(node)
                    break

    fig.canvas.mpl_connect("button_press_event", on_click)
    plt.show()





# === GUI ===
root = tk.Tk()
root.title("Mind Map Generator")
root.geometry("800x600")

# === FRAME UTAMA ===
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10, fill="both", expand=True)

left_frame = tk.Frame(main_frame)
left_frame.grid(row=0, column=0, sticky="n")

right_frame = tk.Frame(main_frame)
right_frame.grid(row=0, column=1, sticky="n", padx=20)

# === ADD TOPIC SECTION ===
tk.Label(left_frame, text="Add Topic").grid(row=0, column=0, columnspan=2, pady=(0, 5))

tk.Label(left_frame, text="Topic:").grid(row=1, column=0, sticky="e")
entry_topic = tk.Entry(left_frame, width=25)
entry_topic.grid(row=1, column=1)

tk.Label(left_frame, text="Category:").grid(row=2, column=0, sticky="e")
category_var = tk.StringVar()
category_var.set("Other")
category_menu = tk.OptionMenu(left_frame, category_var, *category_colors.keys())
category_menu.config(width=20)
category_menu.grid(row=2, column=1)

tk.Button(left_frame, text="Add Topic", command=add_topic).grid(row=3, column=0, columnspan=2, pady=5)


# === CONNECT TOPIC SECTION ===
tk.Label(left_frame, text="Connect Topics").grid(row=4, column=0, columnspan=2, pady=(15, 5))

entry_parent = tk.Entry(left_frame, width=25)
entry_parent.insert(0, "Parent Topic")
entry_parent.grid(row=5, column=0, columnspan=2)

entry_child = tk.Entry(left_frame, width=25)
entry_child.insert(0, "Child Topic")
entry_child.grid(row=6, column=0, columnspan=2)

tk.Button(left_frame, text="Connect", command=connect_topics).grid(row=7, column=0, columnspan=2, pady=5)


# === RENAME TOPIC SECTION ===
tk.Label(left_frame, text="Rename Topic").grid(row=8, column=0, columnspan=2, pady=(15, 5))

entry_old_name = tk.Entry(left_frame, width=25)
entry_old_name.insert(0, "Old Name")
entry_old_name.grid(row=9, column=0, columnspan=2)

entry_new_name = tk.Entry(left_frame, width=25)
entry_new_name.insert(0, "New Name")
entry_new_name.grid(row=10, column=0, columnspan=2)

tk.Button(left_frame, text="Rename", command=rename_topic).grid(row=11, column=0, columnspan=2, pady=5)


# === DELETE TOPIC SECTION ===
tk.Label(left_frame, text="Delete Topic").grid(row=12, column=0, columnspan=2, pady=(15, 5))

entry_delete = tk.Entry(left_frame, width=25)
entry_delete.insert(0, "Topic to Delete")
entry_delete.grid(row=13, column=0, columnspan=2)

tk.Button(left_frame, text="Delete", command=delete_topic).grid(row=14, column=0, columnspan=2, pady=5)


# === ACTION BUTTONS (KANAN) ===
tk.Label(right_frame, text="Actions").pack()

tk.Button(right_frame, text="Show Mind Map", width=20, command=show_mindmap).pack(pady=5)
tk.Button(right_frame, text="Save Mind Map", width=20, command=save_mindmap).pack(pady=5)
tk.Button(right_frame, text="Load Mind Map", width=20, command=load_mindmap).pack(pady=5)
tk.Button(right_frame, text="Export as PNG", width=20, command=export_to_png).pack(pady=5)

# Tambahan opsional: tombol reset
def reset_mindmap():
    global mindmap, topic_categories
    mindmap.clear()
    topic_categories.clear()
    messagebox.showinfo("Reset", "Mind map cleared.")

tk.Button(right_frame, text="Reset Mind Map", width=20, command=reset_mindmap).pack(pady=5)


# === Search ===
tk.Label(right_frame, text="Search Topic").pack(pady=(10, 0))
entry_search = tk.Entry(right_frame, width=20)
entry_search.pack()
tk.Button(right_frame, text="Search", width=20, command=search_topic).pack(pady=5)



root.mainloop()
