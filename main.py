import tkinter as tk
from tkinter import ttk, simpledialog
import sqlite3


class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Database Application")

        self.connection = sqlite3.connect("sqlite.db")
        self.cursor = self.connection.cursor()

        self.create_gui()

    def create_gui(self):
        self.notebook = ttk.Notebook(self.root)

        tables = ["Sellers", "Buyers", "Products", "Sales", "Deliveries", "Warehouses"]
        for table_name in tables:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=table_name)
            self.create_table_view(tab, table_name)

        self.notebook.pack(expand=True, fill="both")

    def create_table_view(self, tab, table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in self.cursor.fetchall()]

        tree = ttk.Treeview(tab, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")

        self.cursor.execute(f"SELECT * FROM {table_name}")
        rows = self.cursor.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)

        tree.pack(expand=True, fill="both")

        add_button = tk.Button(tab, text="Добавить", command=lambda: self.add_data(table_name, tree))
        add_button.pack(side=tk.LEFT, padx=10)

        update_button = tk.Button(tab, text="Изменить", command=lambda: self.update_data(tree, table_name))
        update_button.pack(side=tk.LEFT, padx=10)

        delete_button = tk.Button(tab, text="Удалить", command=lambda: self.delete_data(tree, table_name))
        delete_button.pack(side=tk.LEFT, padx=10)

    def add_data(self, table_name, tree):
        data = simpledialog.askstring("Добавить данные", f"Введите данные для {table_name} через запятую")
        if data:
            data_list = data.split(',')
            self.cursor.execute(f"INSERT INTO {table_name} VALUES ({', '.join(['?']*len(data_list))})", data_list)
            self.connection.commit()
            self.update_treeview(tree, table_name)

    def update_data(self, tree, table_name):
        selected_item = tree.selection()
        if selected_item:
            selected_data = tree.item(selected_item, "values")
            new_data = simpledialog.askstring("Изменить данные", f"Введите новые данные для {table_name} через запятую",
                                              initialvalue=','.join(map(str, selected_data)))
            if new_data:
                new_data_list = new_data.split(',')
                self.cursor.execute(f"UPDATE {table_name} SET "
                                    f"{', '.join([f'{column} = ?' for column in tree['columns']])} "
                                    f"WHERE rowid=?", new_data_list + [selected_data[0]])
                self.connection.commit()
                self.update_treeview(tree, table_name)

    def delete_data(self, tree, table_name):
        selected_item = tree.selection()
        if selected_item:
            selected_data = tree.item(selected_item, "values")
            delete_query = f"DELETE FROM {table_name} WHERE {' AND '.join([f'{column}=?' for column in tree['columns']])}"
            self.cursor.execute(delete_query, selected_data)
            self.connection.commit()
            self.update_treeview(tree, table_name)

    def update_treeview(self, tree, table_name):
        for item in tree.get_children():
            tree.delete(item)
        self.cursor.execute(f"SELECT * FROM {table_name}")
        rows = self.cursor.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)


if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()
