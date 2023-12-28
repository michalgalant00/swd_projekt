from datetime import datetime
import os
import tkinter as tk
from tkinter import ttk
import numpy as np
from fractions import Fraction
from numpy.linalg import eig

class AHPApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Wspomaganie decyzji przy kupnie auta - AHP")

        # Ustawienia rozmiaru okna
        self.window_width = 600
        self.window_height = 300

        # Kryteria
        self.criteria = ["Spalanie", "Cena", "Stan mechaniczny", "Stan lakierniczy", "Wyposażenie"]
        # Wartości
        self.slider_values = [1/9, 1/7, 1/5, 1/3, 1, 3, 5, 7, 9]

        # Macierz porównań par kryteriów
        self.criteria_matrix = np.ones((len(self.criteria), len(self.criteria)), dtype=float)

        # Lista DoubleVar do przechowywania wartości skali
        self.scale_vars = [[None for _ in range(len(self.criteria))] for _ in range(len(self.criteria))]

        # Aktualne porównanie kryteriów
        self.current_comparison = 0

        # Aktualne porównanie kryteriów
        self.current_i = None
        self.current_j = None

        # Czas ostatniej udzielonej odpowiedzi
        self.last_answer_time = datetime.now()  # Inicjalizacja z bieżącym czasem
        # Lista przechowująca wartości międzyczasowe i wybrane wartości
        self.intermediate_times_per_question = {}

        # Katalog, w którym będą przechowywane podsumowania
        self.summary_dir = "podsumowania"
        # Tekst podsumowujący zmiany w odpowiedziach
        self.summary_text = ""

        # Lista przechowująca odpowiedzi użytkownika
        self.user_responses = []

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
        if self.current_comparison < len(self.criteria) * (len(self.criteria) - 1) / 2:
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
        self.current_i, self.current_j = self.get_next_comparison_pair()
        if self.current_i is not None:
            criterion = self.criteria[self.current_i]
            col_criterion = self.criteria[self.current_j]

            # Zeruj zawartość okna
            for widget in form_frame.winfo_children():
                widget.destroy()

            # Tworzenie etykiet i pól do wprowadzania danych
            ttk.Label(form_frame, text=f"Pytanie {self.current_comparison + 1}").grid(row=0, column=0, columnspan=3)
            ttk.Label(form_frame, text=f"{criterion}").grid(row=1, column=0, sticky="e")

            # Oblicz środkową wartość suwaka
            middle_value = len(self.slider_values) // 2

            # Ustawienia suwaka
            scale_var = tk.DoubleVar(value=middle_value)
            scale = ttk.Scale(form_frame, variable=scale_var, from_=0, to=len(self.slider_values)-1, orient="horizontal", length=200,
                command=lambda x:
                    scale_var.set(round(float(x))))
            scale.grid(row=1, column=1)

            # Przypisz zdarzenie puszczenia przycisku myszy do funkcji on_slider_release
            scale.bind("<ButtonRelease-1>", lambda event: self.on_slider_release(scale_var.get()))

            ttk.Label(form_frame, text=f"{col_criterion}").grid(row=1, column=2, padx=(0, 5))
            self.scale_vars[self.current_i][self.current_j] = scale_var  # Przypisanie DoubleVar do listy

            # Przycisk do zatwierdzenia odpowiedzi
            ttk.Button(self.master, text="Zatwierdź odpowiedź", command=self.confirm_answer).grid(row=3, column=0, columnspan=3, pady=(10, 0))

            # Zwiększenie licznika porównań
            self.current_comparison += 1
        else:
            # Jeśli nie ma więcej par do porównania, przejdź do podsumowania
            self.show_summary()

    def on_slider_release(self, value):
        # Funkcja wywoływana po puszczeniu suwaka
        print(f"Suwak został puszczony na wartości: {self.slider_values[int(value)]}")

        # Dodaj informację o puszczeniu suwaka do listy wartości międzyczasowych
        elapsed_time = datetime.now() - self.last_answer_time
        elapsed_seconds = elapsed_time.total_seconds()
        selected_value = self.slider_values[int(value)]
        
        # Dodaj informacje o puszczeniu suwaka do słownika
        question_key = (self.current_i, self.current_j)
        if question_key in self.intermediate_times_per_question:
            self.intermediate_times_per_question[question_key].append((elapsed_seconds, selected_value))
        else:
            self.intermediate_times_per_question[question_key] = [(elapsed_seconds, selected_value)]

    def confirm_answer(self):
        # Dodaj informację o ostatecznej odpowiedzi do podsumowania
        selected_value = self.slider_values[int(self.scale_vars[self.current_i][self.current_j].get())]
        self.summary_text += f"ostateczna odpowiedz: {selected_value}\n"

        # Dodaj informacje o porównaniu do listy
        elapsed_time = datetime.now() - self.last_answer_time
        elapsed_seconds = elapsed_time.total_seconds()
        current_comparison_data = {
            'pytanie': f"{self.criteria[self.current_i]} vs {self.criteria[self.current_j]}",
            'czas': elapsed_seconds,
            'odpowiedz': selected_value
        }

        # Przypisz wartości międzyczasowe do pytania
        intermediate_data = self.intermediate_times_per_question.get((self.current_i, self.current_j), [])
        if intermediate_data:
            current_comparison_data['międzyczasowe'] = intermediate_data

        self.user_responses.append(current_comparison_data)

        # Zaktualizuj czas ostatniej udzielonej odpowiedzi
        self.last_answer_time = datetime.now()

        # Przejdź do kolejnego porównania lub podsumowania
        self.show_next_comparison()

    def get_next_comparison_pair(self):
        for i in range(len(self.criteria)):
            for j in range(i + 1, len(self.criteria)):
                if self.scale_vars[i][j] is None and self.scale_vars[j][i] is None:
                    return i, j
        return None, None

    def show_summary(self):
        # Usuń ramkę porównania
        self.master.destroy()

        # Utwórz ramkę podsumowania
        summary_root = tk.Tk()
        summary_root.title("Podsumowanie ankiety")

        result_frame = ttk.Frame(summary_root, padding="10")
        result_frame.grid(row=0, column=0)

        # Label PODSUMOWANIE ANKIETY
        ttk.Label(result_frame, text="PODSUMOWANIE ANKIETY").grid(row=0, column=0, columnspan=2)

        # Wprowadź podsumowanie do pola TextArea
        summary_text = tk.Text(result_frame, height=20, width=40)
        summary_text.grid(row=1, column=0, columnspan=2)

        # Wagi
        summary_text.insert(tk.END, "WAGI:\n")
        weights = self.calculate_weights()  # Wywołaj funkcję do obliczania wag
        for i, weight in enumerate(weights):
            summary_text.insert(tk.END, f"{self.criteria[i]}: {weight:.3f}\n")

        # Współczynnik konsekwentności
        consistency_ratio = self.calculate_consistency_ratio()
        summary_text.insert(tk.END, f"\nWSPÓŁCZYNNIK KONSEKWENTNOŚCI: {consistency_ratio:.3f}\n")

        # Odpowiedzi
        summary_text.insert(tk.END, "\nODPOWIEDZI:\n")
        for idx, response in enumerate(self.user_responses):
            czas = round(response['czas'], 2)
            odpowiedz = Fraction(response['odpowiedz']).limit_denominator() if '.' in str(response['odpowiedz']) else response['odpowiedz']
            summary_text.insert(tk.END, f"{idx+1}. {response['pytanie']}\n")
            summary_text.insert(tk.END, f"Czas: {czas} sekund, Odpowiedź: {odpowiedz}\n")

        # Międzyczasowe
        summary_text.insert(tk.END, "\nODPOWIEDZI MIĘDZYCZASOWE:\n")
        for (i, j), times_values in self.intermediate_times_per_question.items():
            summary_text.insert(tk.END, f"{i+1} vs {j+1}:\n")
            for time, value in times_values:
                summary_text.insert(tk.END, f"Czas: {round(time, 2)} sekund, Odpowiedź: {Fraction(value).limit_denominator() if '.' in str(value) else value}\n")

        summary_text.config(state="disabled")

        self.save_results(summary_text.get("1.0", tk.END))

        summary_root.mainloop()


    def save_results(self, result_str):
        # Utwórz katalog PODSUMOWANIA, jeśli nie istnieje
        if not os.path.exists(self.summary_dir):
            os.makedirs(self.summary_dir)

        # Utwórz nazwę pliku zgodnie z wymaganiami
        now = datetime.now()
        date_str = now.strftime("%d-%m-%Y")
        time_str = now.strftime("%H-%M")
        filename = f"podsumowanie_{date_str}_{time_str}.txt"
        filepath = os.path.join(self.summary_dir, filename)

        # Zapisz wyniki do pliku
        with open(filepath, "w") as file:
            file.write(result_str)

    def calculate_weights(self):
        matrix = np.ones((len(self.criteria), len(self.criteria)), dtype=float)
        for i in range(len(self.criteria)):
            for j in range(len(self.criteria)):
                if i == j:
                    continue
                scale_var = self.scale_vars[i][j]
                if scale_var is not None:
                    matrix[i, j] = scale_var.get()
        # Oblicz wagi za pomocą algorytmu AHP
        return ahp(matrix)
    
    def calculate_consistency_ratio(self):
        matrix = np.array(self.criteria_matrix)
        eigvals, _ = eig(matrix)
        max_eigval = max(eigvals)
        consistency_index = (max_eigval - len(self.criteria)) / (len(self.criteria) - 1)
        random_index = self.calculate_random_index(len(self.criteria))
        consistency_ratio = consistency_index / random_index

        # Dodaj wpływ czasów międzyczasowych na współczynnik konsekwentności
        for (i, j), times_values in self.intermediate_times_per_question.items():
            total_time = sum(time for time, _ in times_values)
            consistency_ratio += total_time / len(times_values)

        return consistency_ratio

    def calculate_random_index(self, n):
        # Wartości indeksu przypadkowego dla n = 1, 2, ..., 10 (zdefiniowane empirycznie)
        random_indices = [0, 0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]
        return random_indices[n - 1]
    
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
