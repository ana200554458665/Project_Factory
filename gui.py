import tkinter as tk
from tkinter import ttk, messagebox
import requests


BASE_URL = "http://127.0.0.1:8000"


class FactoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Factory Quality Control")
        self.root.geometry("1000x700")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.create_identifiers_tab()
        self.create_measurements_tab()
        self.create_quality_check_tab()
        self.create_statistics_tab()

    # ---------------- IDENTIFIERS ----------------
    def create_identifiers_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Identifiers")

        self.identifiers_tree = ttk.Treeview(
            frame,
            columns=("identifier_name", "description", "identifier_type"),
            show="headings",
            height=15
        )
        self.identifiers_tree.heading("identifier_name", text="Identifier Name")
        self.identifiers_tree.heading("description", text="Description")
        self.identifiers_tree.heading("identifier_type", text="Identifier Type")
        self.identifiers_tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Load Identifiers", command=self.load_identifiers).grid(row=0, column=0, padx=5)

        ttk.Label(btn_frame, text="Identifier").grid(row=1, column=0)
        self.identifier_name_entry = ttk.Entry(btn_frame)
        self.identifier_name_entry.grid(row=1, column=1)

        ttk.Label(btn_frame, text="Description").grid(row=2, column=0)
        self.description_entry = ttk.Entry(btn_frame)
        self.description_entry.grid(row=2, column=1)

        ttk.Label(btn_frame, text="Type").grid(row=3, column=0)
        self.identifier_type_entry = ttk.Entry(btn_frame)
        self.identifier_type_entry.grid(row=3, column=1)

        ttk.Button(btn_frame, text="Add Identifier", command=self.add_identifier).grid(row=4, column=0, columnspan=2, pady=5)

    def load_identifiers(self):
        try:
            response = requests.get(f"{BASE_URL}/identifiers")
            response.raise_for_status()
            data = response.json()

            for item in self.identifiers_tree.get_children():
                self.identifiers_tree.delete(item)

            for row in data:
                self.identifiers_tree.insert("", tk.END, values=(
                    row["identifier_name"],
                    row["description"],
                    row["identifier_type"]
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_identifier(self):
        payload = {
            "identifier_name": self.identifier_name_entry.get(),
            "description": self.description_entry.get(),
            "identifier_type": self.identifier_type_entry.get()
        }

        try:
            response = requests.post(f"{BASE_URL}/identifiers", json=payload)
            response.raise_for_status()
            messagebox.showinfo("Success", "Identifier added successfully")
            self.load_identifiers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- MEASUREMENTS ----------------
    def create_measurements_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Measurements")

        self.measurements_tree = ttk.Treeview(
            frame,
            columns=("id", "identifier", "master", "characteristic", "value", "status", "measured_at"),
            show="headings",
            height=15
        )
        self.measurements_tree.heading("id", text="ID")
        self.measurements_tree.heading("identifier", text="Identifier")
        self.measurements_tree.heading("master", text="Master Name")
        self.measurements_tree.heading("characteristic", text="Characteristic")
        self.measurements_tree.heading("value", text="Measured Value")
        self.measurements_tree.heading("status", text="Status")
        self.measurements_tree.heading("measured_at", text="Measured At")
        self.measurements_tree.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(frame, text="Load Measurements", command=self.load_measurements).pack(pady=10)

    def load_measurements(self):
        try:
            response = requests.get(f"{BASE_URL}/measurements")
            response.raise_for_status()
            data = response.json()

            for item in self.measurements_tree.get_children():
                self.measurements_tree.delete(item)

            for row in data:
                self.measurements_tree.insert("", tk.END, values=(
                    row["measurement_id"],
                    row["identifier_name"],
                    row["master_name"],
                    row["characteristic_name"],
                    row["measured_value"],
                    row["status"],
                    row["measured_at"]
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- QUALITY CHECK ----------------
    def create_quality_check_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Quality Check")

        ttk.Label(frame, text="Identifier Name").grid(row=0, column=0, padx=10, pady=10)
        self.q_identifier = ttk.Entry(frame)
        self.q_identifier.grid(row=0, column=1)

        ttk.Label(frame, text="Master Name").grid(row=1, column=0, padx=10, pady=10)
        self.q_master = ttk.Entry(frame)
        self.q_master.grid(row=1, column=1)

        ttk.Label(frame, text="Characteristic Name").grid(row=2, column=0, padx=10, pady=10)
        self.q_characteristic = ttk.Entry(frame)
        self.q_characteristic.grid(row=2, column=1)

        ttk.Label(frame, text="Measured Value").grid(row=3, column=0, padx=10, pady=10)
        self.q_value = ttk.Entry(frame)
        self.q_value.grid(row=3, column=1)

        ttk.Button(frame, text="Run Quality Check", command=self.run_quality_check).grid(row=4, column=0, columnspan=2, pady=15)
        ttk.Button(frame, text="Save Measurement", command=self.save_measurement).grid(row=5, column=0, columnspan=2, pady=5)

        self.quality_result = tk.Text(frame, height=12, width=60)
        self.quality_result.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    def run_quality_check(self):
        try:
            payload = {
                "identifier_name": self.q_identifier.get(),
                "master_name": self.q_master.get(),
                "characteristic_name": self.q_characteristic.get(),
                "measured_value": float(self.q_value.get())
            }

            response = requests.post(f"{BASE_URL}/quality-check", json=payload)
            response.raise_for_status()
            data = response.json()

            self.quality_result.delete("1.0", tk.END)
            self.quality_result.insert(tk.END, str(data))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_measurement(self):
        try:
            payload = {
                "identifier_name": self.q_identifier.get(),
                "master_name": self.q_master.get(),
                "characteristic_name": self.q_characteristic.get(),
                "measured_value": float(self.q_value.get())
            }

            response = requests.post(f"{BASE_URL}/measurements", json=payload)
            response.raise_for_status()
            data = response.json()

            messagebox.showinfo("Saved", str(data))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- STATISTICS ----------------
    def create_statistics_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Statistics")

        ttk.Label(frame, text="Identifier Name").grid(row=0, column=0, padx=10, pady=10)
        self.stats_identifier = ttk.Entry(frame)
        self.stats_identifier.grid(row=0, column=1)

        ttk.Button(frame, text="Load Statistics", command=self.load_statistics).grid(row=1, column=0, columnspan=2, pady=10)

        self.stats_result = tk.Text(frame, height=15, width=60)
        self.stats_result.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def load_statistics(self):
        try:
            identifier_name = self.stats_identifier.get()
            response = requests.get(f"{BASE_URL}/statistics/{identifier_name}")
            response.raise_for_status()
            data = response.json()

            self.stats_result.delete("1.0", tk.END)
            self.stats_result.insert(tk.END, str(data))
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = FactoryGUI(root)
    root.mainloop()