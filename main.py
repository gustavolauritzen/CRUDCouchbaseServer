# DENSENVOLVIDO POR: Gustavo Baron Lauritzen, Matheus Baron Lauritzen e Gabriel Bósio
from datetime import timedelta
from tkinter import *
from tkinter import messagebox, ttk

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions

# Update this to your cluster
username = "Administrator"
password = "password"
bucket_name = "testeCRUD"
scope_name = "escopoCRUD"
collection_name = "colecaoCRUD"

# Connect options - authentication
auth = PasswordAuthenticator(username, password)

# Get a reference to our cluster
cluster = Cluster('couchbase://localhost', ClusterOptions(auth))
cluster.wait_until_ready(timedelta(seconds=5))

# Get a reference to our bucket, scope, and collection
cb = cluster.bucket(bucket_name)
cb_coll = cb.scope(scope_name).collection(collection_name)


def create_document_window():
    def create_document():
        try:
            doc = {
                "type": type_entry.get(),
                "id": int(id_entry.get()),
                "name": name_entry.get()
            }
            key = str(doc["id"])
            result = cb_coll.upsert(key, doc)
            display_documents()
            messagebox.showinfo("Success", f"Document created with CAS: {result.cas}")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    window = Toplevel(root)
    window.title("Create Document")

    Label(window, text="Type").grid(row=0, column=0, padx=10, pady=10)
    type_entry = Entry(window)
    type_entry.grid(row=0, column=1, padx=10, pady=10)

    Label(window, text="ID").grid(row=1, column=0, padx=10, pady=10)
    id_entry = Entry(window)
    id_entry.grid(row=1, column=1, padx=10, pady=10)

    Label(window, text="Name").grid(row=2, column=0, padx=10, pady=10)
    name_entry = Entry(window)
    name_entry.grid(row=2, column=1, padx=10, pady=10)

    Button(window, text="Create Document", command=create_document).grid(row=3, column=0, columnspan=2, padx=10,
                                                                         pady=10)


def update_document_window():
    def update_document():
        try:
            key = id_entry.get()
            # Verificar se o documento existe
            try:
                result = cb_coll.get(key)
            except Exception as e:
                messagebox.showerror("Error", "Document does not exist and cannot be updated")
                return

            # Se o documento existe, atualizar o documento
            doc = {
                "type": type_entry.get(),
                "id": int(id_entry.get()),
                "name": name_entry.get()
            }
            result = cb_coll.upsert(key, doc)
            display_documents()
            messagebox.showinfo("Success", f"Document updated with CAS: {result.cas}")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    window = Toplevel(root)
    window.title("Update Document")

    Label(window, text="ID").grid(row=0, column=0, padx=10, pady=10)
    id_entry = Entry(window)
    id_entry.grid(row=0, column=1, padx=10, pady=10)

    Label(window, text="Type").grid(row=1, column=0, padx=10, pady=10)
    type_entry = Entry(window)
    type_entry.grid(row=1, column=1, padx=10, pady=10)

    Label(window, text="Name").grid(row=2, column=0, padx=10, pady=10)
    name_entry = Entry(window)
    name_entry.grid(row=2, column=1, padx=10, pady=10)

    Button(window, text="Update Document", command=update_document).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

def delete_document_window():
    def delete_document():
        try:
            key = id_entry.get()
            result = cb_coll.remove(key)
            display_documents()
            messagebox.showinfo("Success", f"Document deleted with CAS: {result.cas}")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    window = Toplevel(root)
    window.title("Delete Document")

    Label(window, text="ID").grid(row=0, column=0, padx=10, pady=10)
    id_entry = Entry(window)
    id_entry.grid(row=0, column=1, padx=10, pady=10)

    Button(window, text="Delete Document", command=delete_document).grid(row=1, column=0, columnspan=2, padx=10,
                                                                         pady=10)


# Function to list documents using N1QL and display in Treeview
def display_documents():
    try:
        query = f'SELECT * FROM `{bucket_name}`.`{scope_name}`.`{collection_name}`'
        result = cluster.query(query)

        # Clear existing rows in the Treeview
        for row in tree.get_children():
            tree.delete(row)

        # Insert new rows
        for row in result:
            doc_id = row[collection_name]['id']
            doc_type = row[collection_name]['type']
            doc_name = row[collection_name]['name']
            tree.insert("", "end", values=(doc_id, doc_type, doc_name))

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Tkinter setup
root = Tk()
root.title("CRUD Couchbase")

# Treeview setup
columns = ("ID", "Type", "Name")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.heading("ID", text="ID")
tree.heading("Type", text="Type")
tree.heading("Name", text="Name")
tree.pack(expand=True, fill=BOTH, padx=20, pady=20)

# Refresh button
refresh_button = Button(root, text="Refresh Documents", command=display_documents)
refresh_button.pack(pady=10)

# Frame for the Create, Update, and Delete buttons
button_frame = Frame(root)
button_frame.pack(pady=10)

create_button = Button(button_frame, text="Create Document", command=create_document_window)
create_button.grid(row=0, column=0, padx=5)

update_button = Button(button_frame, text="Update Document", command=update_document_window)
update_button.grid(row=0, column=1, padx=5)

delete_button = Button(button_frame, text="Delete Document", command=delete_document_window)
delete_button.grid(row=0, column=2, padx=5)

# Initial display of documents
display_documents()

root.mainloop()