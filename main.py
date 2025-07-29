import tkinter as tk
from tkinter import filedialog, messagebox
import networkx as nx
import matplotlib.pyplot as plt
import json

# Global variables
mindmap = nx.DiGraph()
topic_categories = {}
notes = {}

# Color scheme for different categories
category_colors = {
    "Language": "#87CEEB",        # SkyBlue - untuk bahasa pemrograman
    "Framework": "#98FB98",       # PaleGreen - untuk framework
    "Tool": "#F08080",            # LightCoral - untuk tools
    "Lesson": "#FFE4B5",          # Moccasin - untuk pembelajaran
    "Subject": "#FFFFE0",         # LightYellow - untuk mata pelajaran
    "Library": "#FFB6C1",         # LightPink - untuk library
    "Project": "#E0FFFF",         # LightCyan - untuk project
    "Concept": "#20B2AA",         # LightSeaGreen - untuk konsep
    "Method": "#DDA0DD",          # Plum - untuk method
    "Database": "#B0C4DE",        # LightSteelBlue - untuk database
    "Database Type": "#D2B48C",   # Tan - untuk tipe database
    "Idea Hub": "#CD5C5C",        # IndianRed - untuk hub ide
    "Query Language": "#9370DB",  # MediumPurple - untuk query language
    "Area": "#FFA500",            # Orange - untuk area/bidang
    "Technology": "#8A2BE2",      # BlueViolet - untuk teknologi
    "Process": "#C0C0C0",         # Silver - untuk proses
    "Protocol": "#DAA520",        # GoldenRod - untuk protocol
    "Component": "#CD853F",       # Peru - untuk komponen
    "Field": "#708090",           # SlateGray - untuk field
    "Other": "#D3D3D3"            # LightGray - untuk lainnya
}



def add_topic():
    topic = entry_topic.get().strip()
    category = category_var.get()

    # Validation
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
        messagebox.showerror("Invalid Connection", 
                           f"Cannot connect '{parent}' to '{child}' because '{child}' is already connected to '{parent}'.")
        return
    
    if mindmap.has_edge(parent, child):
        messagebox.showinfo("Already Connected", f"'{parent}' is already connected to '{child}'.")
        return

    mindmap.add_edge(parent, child)
    messagebox.showinfo("Connected", f"Connected '{parent}' to '{child}'.")


def show_mindmap():
    if len(mindmap.nodes) == 0:
        messagebox.showinfo("Info", "Mind map is empty.")
        return
    
    try:
        pos = nx.nx_agraph.graphviz_layout(mindmap, prog="dot")
    except:
        pos = nx.spring_layout(mindmap, seed=42)
    
    colors = [category_colors.get(topic_categories.get(n, "Other"), "#D3D3D3") for n in mindmap.nodes]

    plt.close('all')
    fig, ax = plt.subplots(figsize=(12, 8))
    
    nx.draw(mindmap, pos, with_labels=True, node_color=colors, node_size=2000, 
            font_size=10, font_weight='bold', arrows=True, ax=ax)

    setup_click_handler(fig, ax, pos, "Mind Map View")
    
    plt.tight_layout()
    plt.show()


def setup_click_handler(fig, ax, pos, title="Mind Map"):
    node_positions = {node: pos[node] for node in mindmap.nodes}
    
    def on_click(event):
        if event.inaxes == ax and event.xdata is not None and event.ydata is not None:
            x_click, y_click = event.xdata, event.ydata
            min_distance = float('inf')
            closest_node = None
            
            # Find the closest node to click position
            for node, (x, y) in node_positions.items():
                distance = (x - x_click)**2 + (y - y_click)**2
                if distance < min_distance:
                    min_distance = distance
                    closest_node = node
            
            # Calculate dynamic threshold based on coordinate range
            if node_positions:
                x_coords = [pos[0] for pos in node_positions.values()]
                y_coords = [pos[1] for pos in node_positions.values()]
                x_range = max(x_coords) - min(x_coords) if len(x_coords) > 1 else 100
                y_range = max(y_coords) - min(y_coords) if len(y_coords) > 1 else 100
                
                threshold = max(x_range, y_range) * 0.05  # 5% of coordinate range
                threshold_squared = threshold ** 2
                
                if closest_node and min_distance < threshold_squared:
                    show_topic_dialog(closest_node)
    
    # Connect the event handler
    cid = fig.canvas.mpl_connect("button_press_event", on_click)
    ax.set_title(f"{title} - Click on nodes to see details", fontsize=14)
    
    return cid


def show_topic_dialog(topic):
    top = tk.Toplevel(root)
    top.title(f"Details: {topic}")
    top.geometry("400x300")

    category = topic_categories.get(topic, "Other")
    current_note = notes.get(topic, "")

    header_frame = tk.Frame(top, bg=category_colors.get(category, "#D3D3D3"))
    header_frame.pack(fill="x", padx=5, pady=5)
    
    tk.Label(header_frame, text=f"Topic: {topic}", font=("Arial", 14, "bold"), 
             bg=category_colors.get(category, "#D3D3D3")).pack(pady=5)
    tk.Label(header_frame, text=f"Category: {category}", font=("Arial", 11), 
             bg=category_colors.get(category, "#D3D3D3")).pack(pady=2)

    tk.Label(top, text="Notes:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
    note_text = tk.Text(top, width=45, height=8, wrap=tk.WORD)
    note_text.pack(padx=10, pady=5, fill="both", expand=True)
    note_text.insert("1.0", current_note)

    button_frame = tk.Frame(top)
    button_frame.pack(pady=10)
    
    def save_note():
        notes[topic] = note_text.get("1.0", tk.END).strip()
        messagebox.showinfo("Saved", f"Note saved for '{topic}'")
        top.destroy()

    def delete_from_dialog():
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{topic}'?"):
            mindmap.remove_node(topic)
            if topic in topic_categories:
                del topic_categories[topic]
            if topic in notes:
                del notes[topic]
            messagebox.showinfo("Deleted", f"Topic '{topic}' deleted.")
            top.destroy()

    tk.Button(button_frame, text="Save Note", command=save_note, bg="#4CAF50", fg="white").pack(side="left", padx=5)
    tk.Button(button_frame, text="Delete Topic", command=delete_from_dialog, bg="#f44336", fg="white").pack(side="left", padx=5)
    tk.Button(button_frame, text="Close", command=top.destroy, bg="#2196F3", fg="white").pack(side="left", padx=5)


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

    neighbors = list(mindmap.successors(old_name))
    predecessors = list(mindmap.predecessors(old_name))

    mindmap.remove_node(old_name)
    mindmap.add_node(new_name)

    for n in neighbors:
        mindmap.add_edge(new_name, n)
    for p in predecessors:
        mindmap.add_edge(p, new_name)

    topic_categories[new_name] = topic_categories.pop(old_name, "Other")
    if old_name in notes:
        notes[new_name] = notes.pop(old_name)

    messagebox.showinfo("Renamed", f"Topic '{old_name}' renamed to '{new_name}'.")
    entry_old_name.delete(0, tk.END)
    entry_new_name.delete(0, tk.END)


def delete_topic():
    name = entry_delete.get().strip()
    if name in mindmap.nodes:
        mindmap.remove_node(name)
        if name in topic_categories:
            del topic_categories[name]
        if name in notes:
            del notes[name]
        messagebox.showinfo("Deleted", f"Topic '{name}' deleted.")
        entry_delete.delete(0, tk.END)
    else:
        messagebox.showwarning("Warning", "Topic not found.")


def export_to_png():
    if len(mindmap.nodes) == 0:
        messagebox.showinfo("Info", "Mind map is empty.")
        return

    pos = nx.spring_layout(mindmap, seed=42)

    node_colors = []
    for node in mindmap.nodes:
        category = topic_categories.get(node, "Other")
        color = category_colors.get(category, "#D3D3D3")
        node_colors.append(color)

    plt.figure(figsize=(12, 8))
    nx.draw(mindmap, pos, with_labels=True, node_color=node_colors,
            node_size=2000, font_size=10, font_weight='bold', arrows=True)
    plt.title("Mind Map Export")

    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        plt.savefig(file_path, bbox_inches='tight', dpi=300)
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
            node_colors.append("#FFD700")  # Gold highlight
        else:
            category = topic_categories.get(node, "Other")
            color = category_colors.get(category, "#D3D3D3")
            node_colors.append(color)

    fig, ax = plt.subplots(figsize=(12, 8))
    nx.draw(mindmap, pos, with_labels=True, node_color=node_colors,
            node_size=2000, font_size=10, font_weight='bold', arrows=True, ax=ax)

    setup_click_handler(fig, ax, pos, f"Search Result for '{keyword}'")
    plt.tight_layout()
    plt.show()


def show_category_view():
    if len(mindmap.nodes) == 0:
        messagebox.showinfo("Info", "Mind map is empty.")
        return
    
    pos = nx.spring_layout(mindmap, seed=42)
    colors = [category_colors.get(topic_categories.get(n, "Other"), "#D3D3D3") for n in mindmap.nodes]

    fig, ax = plt.subplots(figsize=(14, 10))
    nx.draw(mindmap, pos, with_labels=True, node_color=colors, node_size=2500, 
            font_size=9, font_weight='bold', arrows=True, ax=ax)

    from matplotlib.patches import Patch
    legend_elements = []
    used_categories = set(topic_categories.values())
    for category in sorted(used_categories):
        color = category_colors.get(category, "#D3D3D3")
        legend_elements.append(Patch(facecolor=color, label=category))
    
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
    
    setup_click_handler(fig, ax, pos, "Category View")
    plt.tight_layout()
    plt.show()


def reset_mindmap():
    global mindmap, topic_categories, notes
    mindmap.clear()
    topic_categories.clear()
    notes.clear()
    messagebox.showinfo("Reset", "Mind map cleared.")


# GUI

root = tk.Tk()
root.title("Mind Map Project")
root.geometry("900x650")

# Main frame layout
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10, fill="both", expand=True)

left_frame = tk.Frame(main_frame)
left_frame.grid(row=0, column=0, sticky="n")

right_frame = tk.Frame(main_frame)
right_frame.grid(row=0, column=1, sticky="n", padx=20)

#Topic Management Section

# Add Topic Section
tk.Label(left_frame, text="Add Topic", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 5))

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

# Connect Topics Section
tk.Label(left_frame, text="Connect Topics", font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=2, pady=(15, 5))

entry_parent = tk.Entry(left_frame, width=25)
entry_parent.insert(0, "Parent Topic")
entry_parent.grid(row=5, column=0, columnspan=2)

entry_child = tk.Entry(left_frame, width=25)
entry_child.insert(0, "Child Topic")
entry_child.grid(row=6, column=0, columnspan=2)

tk.Button(left_frame, text="Connect", command=connect_topics).grid(row=7, column=0, columnspan=2, pady=5)

# Rename Topic Section
tk.Label(left_frame, text="Rename Topic", font=("Arial", 12, "bold")).grid(row=8, column=0, columnspan=2, pady=(15, 5))

entry_old_name = tk.Entry(left_frame, width=25)
entry_old_name.insert(0, "Old Name")
entry_old_name.grid(row=9, column=0, columnspan=2)

entry_new_name = tk.Entry(left_frame, width=25)
entry_new_name.insert(0, "New Name")
entry_new_name.grid(row=10, column=0, columnspan=2)

tk.Button(left_frame, text="Rename", command=rename_topic).grid(row=11, column=0, columnspan=2, pady=5)

# Delete Topic Section
tk.Label(left_frame, text="Delete Topic", font=("Arial", 12, "bold")).grid(row=12, column=0, columnspan=2, pady=(15, 5))

entry_delete = tk.Entry(left_frame, width=25)
entry_delete.insert(0, "Topic to Delete")
entry_delete.grid(row=13, column=0, columnspan=2)

tk.Button(left_frame, text="Delete", command=delete_topic).grid(row=14, column=0, columnspan=2, pady=5)

#Actions Section & Visualization

tk.Label(right_frame, text="Actions", font=("Arial", 12, "bold")).pack()

# Visualization buttons
tk.Button(right_frame, text="Show Mind Map", width=20, command=show_mindmap).pack(pady=5)
tk.Button(right_frame, text="Category View", width=20, command=show_category_view).pack(pady=5)

# File operations
tk.Button(right_frame, text="Save Mind Map", width=20, command=save_mindmap).pack(pady=5)
tk.Button(right_frame, text="Load Mind Map", width=20, command=load_mindmap).pack(pady=5)
tk.Button(right_frame, text="Export as PNG", width=20, command=export_to_png).pack(pady=5)

# Utility operations
tk.Button(right_frame, text="Reset Mind Map", width=20, command=reset_mindmap).pack(pady=5)

# Search Section
tk.Label(right_frame, text="Search Topic", font=("Arial", 12, "bold")).pack(pady=(15, 0))
entry_search = tk.Entry(right_frame, width=20)
entry_search.pack()
tk.Button(right_frame, text="Search", width=20, command=search_topic).pack(pady=5)

# Information label
info_label = tk.Label(right_frame, text="💡 Click on any node to see details!", 
                     font=("Arial", 9), fg="blue", wraplength=150)
info_label.pack(pady=(20, 5))

# Start the application
if __name__ == "__main__":
    root.mainloop()