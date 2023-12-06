from datetime import datetime
import os
import tkinter as tk
from tkinter import ttk
import numpy as np

class AHPApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Wspomaganie decyzji przy kupnie auta - AHP")

        # Ustawienia rozmiaru okna
        self.window_width = 600
        self.window_height = 300

        # Kryteria i alternatywy
        self.criteria = ["Rok produkcji", "Cena", "Stan mechaniczny", "Stan lakierniczy", "Wyposażenie"]
        self.alternatives = ["Samochód A", "Samochód B", "Samochód C", "Samochód D"]

        # Macierz porównań par kryteriów
        self.criteria_matrix = np.ones((len(self.criteria), len(self.criteria)), dtype=float)

        # Lista DoubleVar do przechowywania wartości skali
        self.scale_vars = [[None for _ in range(len(self.criteria))] for _ in range(len(self.criteria))]

        # Aktualne porównanie kryteriów
        self.current_comparison = 0

        # GUI
        self.create_welcome_gui()

    def create_welcome_gui(self):
        # Ustawienia rozmiaru okna powitalnego
        self.master.geometry(f"{self.window_width}x{self.window_height}")

        # Ramka ekranu powitalnego
        self.welcome_frame = ttk.Frame(self.master, padding="10")
        self.welcome_frame.grid(row=0, column=0, columnspan=3)

        # Tworzenie etykiety powitalnej
        ttk.Label(self.welcome_frame, text="Witaj w ankiecie AHP dotyczącej kryteriów kupna auta").grid(row=0, column=0, columnspan=2, pady=(10, 0))

        # Przycisk do przejścia do pierwszego porównania
        ttk.Button(self.welcome_frame, text="Rozpocznij ankietę", command=self.show_next_comparison).grid(row=1, column=0, columnspan=2, pady=(10, 0))

    def show_next_comparison(self):
        if self.current_comparison < len(self.criteria) * (len(self.criteria) - 1):
            # Przejdź do kolejnego porównania
            self.create_comparison_gui()
        else:
            # Przejdź do podsumowania
            self.show_summary()

    def create_comparison_gui(self):
        # Usuń ekran powitalny
        self.welcome_frame.destroy()

        # Ustawienia rozmiaru okna porównania
        self.master.geometry(f"{self.window_width}x{self.window_height}")

        # Ramka do formularza
        form_frame = ttk.Frame(self.master, padding="10")
        form_frame.grid(row=0, column=0, columnspan=3)

        # Porównanie aktualnych kryteriów
        while True:
            i, j = divmod(self.current_comparison, len(self.criteria))
            if i != j and self.scale_vars[i][j] is None:
                break
            self.current_comparison += 1

        criterion = self.criteria[i]
        col_criterion = self.criteria[j]

        # Zeruj zawartość okna
        for widget in form_frame.winfo_children():
            widget.destroy()

        # Tworzenie etykiet i pól do wprowadzania danych
        ttk.Label(form_frame, text=f"Pytanie {self.current_comparison + 1}").grid(row=0, column=0, columnspan=3)
        ttk.Label(form_frame, text=f"{criterion}").grid(row=1, column=0, sticky="e")

        # Oblicz środkową wartość skali
        middle_value = (1 + 10) / 2

        scale_var = tk.DoubleVar(value=middle_value)
        ttk.Scale(form_frame, variable=scale_var, from_=1, to=10, orient="horizontal", length=100).grid(row=1, column=1)

        ttk.Label(form_frame, text=f"{col_criterion}").grid(row=1, column=2, padx=(0, 5))
        self.scale_vars[i][j] = scale_var  # Przypisanie DoubleVar do listy

        # Przycisk do przejścia do kolejnego porównania
        ttk.Button(self.master, text="Przejdź dalej", command=self.show_next_comparison).grid(row=2, column=0, columnspan=3, pady=(10, 0))

        # Zwiększenie licznika porównań
        self.current_comparison += 1

    def show_summary(self):
        # Usuń ramkę porównania
        self.master.destroy()

        # Utwórz ramkę podsumowania
        summary_root = tk.Tk()
        summary_root.title("Podsumowanie wyników")

        result_frame = ttk.Frame(summary_root, padding="10")
        result_frame.grid(row=0, column=0)

        ttk.Label(result_frame, text="Wagi").grid(row=0, column=0, columnspan=2)

        result_text = tk.Text(result_frame, height=len(self.criteria), width=20, state="disabled")
        result_text.grid(row=1, column=0, columnspan=2)

        # Oblicz wagi i wyświetl wyniki
        self.calculate_weights()
        weights = ahp(self.criteria_matrix)
        result_str = ""

        for i, weight in enumerate(weights):
            result_str += f"{self.criteria[i]}: {weight:.3f}\n"

        # Zapisz wyniki do pliku
        self.save_results(result_str)

        result_text.config(state="normal")
        result_text.insert(tk.END, result_str)
        result_text.config(state="disabled")

        summary_root.mainloop()

    def save_results(self, result_str):
        # Utwórz katalog PODSUMOWANIA, jeśli nie istnieje
        summary_dir = "podsumowania"
        if not os.path.exists(summary_dir):
            os.makedirs(summary_dir)

        # Utwórz nazwę pliku zgodnie z wymaganiami
        now = datetime.now()
        date_str = now.strftime("%d-%m-%Y")
        time_str = now.strftime("%H-%M")
        filename = f"podsumowanie_{date_str}_{time_str}.txt"
        filepath = os.path.join(summary_dir, filename)

        # Zapisz wyniki do pliku
        with open(filepath, "w") as file:
            file.write(result_str)

    def calculate_weights(self):
        for i in range(len(self.criteria)):
            for j in range(len(self.criteria)):
                if i == j:
                    continue
                scale_var = self.scale_vars[i][j]
                if scale_var is not None:
                    self.criteria_matrix[i, j] = scale_var.get()

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
