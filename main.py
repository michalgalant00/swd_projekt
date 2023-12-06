import tkinter as tk
from tkinter import ttk
import numpy as np

class AHPApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Wspomaganie decyzji przy kupnie auta - AHP")

        # Kryteria i alternatywy
        self.criteria = ["Rok produkcji", "Cena", "Stan mechaniczny", "Stan lakierniczy", "Wyposażenie"]
        self.alternatives = ["Samochód A", "Samochód B", "Samochód C", "Samochód D"]

        # Macierz porównań par kryteriów
        self.criteria_matrix = np.ones((len(self.criteria), len(self.criteria)), dtype=float)

        # Lista DoubleVar do przechowywania wartości skali
        self.scale_vars = [[None for _ in range(len(self.criteria))] for _ in range(len(self.criteria))]

        # GUI
        self.create_gui()

    def create_gui(self):
        # Ramka do formularza
        form_frame = ttk.Frame(self.master, padding="10")
        form_frame.grid(row=0, column=0, columnspan=3)

        # Tworzenie etykiet i pól do wprowadzania danych
        for i, criterion in enumerate(self.criteria):
            ttk.Label(form_frame, text=criterion).grid(row=i, column=0, sticky="e")
            for j, col_criterion in enumerate(self.criteria):
                if i == j:
                    continue

                ttk.Label(form_frame, text=f"vs {col_criterion}").grid(row=i, column=j*2+1, padx=(5, 0))
                scale_var = tk.DoubleVar()
                ttk.Scale(form_frame, variable=scale_var, from_=1, to=10, orient="horizontal", length=100).grid(row=i, column=j*2+2)
                self.scale_vars[i][j] = scale_var  # Przypisanie DoubleVar do listy

        # Przycisk do obliczeń
        ttk.Button(self.master, text="Oblicz", command=self.calculate_weights).grid(row=1, column=0, columnspan=3, pady=(10, 0))

        # Wyniki
        result_frame = ttk.Frame(self.master, padding="10")
        result_frame.grid(row=2, column=0, columnspan=3)

        ttk.Label(result_frame, text="Wagi").grid(row=0, column=0, columnspan=2)

        self.result_text = tk.Text(result_frame, height=len(self.criteria), width=20, state="disabled")
        self.result_text.grid(row=1, column=0, columnspan=2)

    def calculate_weights(self):
        for i in range(len(self.criteria)):
            for j in range(len(self.criteria)):
                if i == j:
                    continue
                scale_var = self.scale_vars[i][j]
                self.criteria_matrix[i, j] = scale_var.get()

        weights = ahp(self.criteria_matrix)
        result_str = ""

        for i, weight in enumerate(weights):
            result_str += f"{self.criteria[i]}: {weight:.3f}\n"

        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_str)
        self.result_text.config(state="disabled")

def ahp(matrix):
    col_sums = matrix.sum(axis=0)
    normalized_matrix = matrix / col_sums
    weights = normalized_matrix.mean(axis=1)
    global_weights = weights / weights.sum()
    return global_weights

def main():
    root = tk.Tk()
    app = AHPApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
