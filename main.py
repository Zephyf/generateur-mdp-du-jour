import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import date

APP_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORIQUE_FILE = os.path.join(APP_DIR, "historique.json")


def charger_historique():
    if os.path.exists(HISTORIQUE_FILE):
        with open(HISTORIQUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def sauvegarder_historique(historique):
    with open(HISTORIQUE_FILE, "w", encoding="utf-8") as f:
        json.dump(historique, f, indent=2, ensure_ascii=False)


def generer_mot_de_passe(longueur, maj, chiffres, symboles):
    caracteres = string.ascii_lowercase
    if maj:
        caracteres += string.ascii_uppercase
    if chiffres:
        caracteres += string.digits
    if symboles:
        caracteres += "!@#$%^&*()-_=+"
    return "".join(random.choice(caracteres) for _ in range(longueur))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Générateur de mots de passe")
        self.geometry("420x460")
        self.resizable(False, False)

        self.historique = charger_historique()
        self._assurer_mot_du_jour()
        self._construire_interface()

    def _assurer_mot_du_jour(self):
        aujourdhui = date.today().isoformat()
        if aujourdhui not in self.historique:
            self.historique[aujourdhui] = generer_mot_de_passe(14, True, True, True)
            sauvegarder_historique(self.historique)

    def _construire_interface(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        onglet_generateur = ttk.Frame(notebook)
        onglet_jour = ttk.Frame(notebook)
        notebook.add(onglet_generateur, text="Générer")
        notebook.add(onglet_jour, text="Mot de passe du jour")

        self._construire_onglet_generateur(onglet_generateur)
        self._construire_onglet_jour(onglet_jour)

    def _construire_onglet_generateur(self, parent):
        ttk.Label(parent, text="Longueur :").pack(pady=(15, 0))
        self.longueur_var = tk.IntVar(value=12)
        self.longueur_label = ttk.Label(parent, text="12")
        ttk.Scale(
            parent, from_=6, to=32, variable=self.longueur_var, orient="horizontal",
            command=lambda v: self.longueur_label.config(text=str(int(float(v)))),
        ).pack(fill="x", padx=30)
        self.longueur_label.pack()

        self.maj_var = tk.BooleanVar(value=True)
        self.chiffres_var = tk.BooleanVar(value=True)
        self.symboles_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(parent, text="Majuscules (A-Z)", variable=self.maj_var).pack(anchor="w", padx=30, pady=2)
        ttk.Checkbutton(parent, text="Chiffres (0-9)", variable=self.chiffres_var).pack(anchor="w", padx=30, pady=2)
        ttk.Checkbutton(parent, text="Symboles (!@#...)", variable=self.symboles_var).pack(anchor="w", padx=30, pady=2)

        ttk.Button(parent, text="Générer", command=self._generer).pack(pady=15)

        self.resultat_var = tk.StringVar()
        ttk.Entry(
            parent, textvariable=self.resultat_var, font=("Consolas", 14), justify="center"
        ).pack(fill="x", padx=30, pady=5)

        ttk.Button(parent, text="Copier", command=lambda: self._copier_texte(self.resultat_var.get())).pack(pady=5)

    def _construire_onglet_jour(self, parent):
        aujourdhui = date.today().isoformat()

        ttk.Label(parent, text="Suggestion du jour :", font=("Segoe UI", 11)).pack(pady=(20, 5))
        self.mdp_jour_var = tk.StringVar(value=self.historique[aujourdhui])
        ttk.Entry(
            parent, textvariable=self.mdp_jour_var, font=("Consolas", 14),
            justify="center", state="readonly",
        ).pack(fill="x", padx=30, pady=5)

        boutons = ttk.Frame(parent)
        boutons.pack(pady=5)
        ttk.Button(boutons, text="Copier", command=lambda: self._copier_texte(self.mdp_jour_var.get())).pack(side="left", padx=5)
        ttk.Button(boutons, text="Regénérer aujourd'hui", command=self._regenerer_jour).pack(side="left", padx=5)

        ttk.Label(parent, text="Historique :").pack(pady=(20, 5))
        self.liste_historique = tk.Listbox(parent, font=("Consolas", 10))
        self.liste_historique.pack(fill="both", expand=True, padx=30, pady=(0, 15))
        self._rafraichir_historique()

    def _generer(self):
        longueur = self.longueur_var.get()
        if not (self.maj_var.get() or self.chiffres_var.get() or self.symboles_var.get()):
            messagebox.showwarning("Attention", "Coche au moins une option en plus des minuscules.")
        mdp = generer_mot_de_passe(longueur, self.maj_var.get(), self.chiffres_var.get(), self.symboles_var.get())
        self.resultat_var.set(mdp)

    def _copier_texte(self, texte):
        if texte:
            self.clipboard_clear()
            self.clipboard_append(texte)

    def _regenerer_jour(self):
        aujourdhui = date.today().isoformat()
        self.historique[aujourdhui] = generer_mot_de_passe(14, True, True, True)
        sauvegarder_historique(self.historique)
        self.mdp_jour_var.set(self.historique[aujourdhui])
        self._rafraichir_historique()

    def _rafraichir_historique(self):
        self.liste_historique.delete(0, "end")
        for jour in sorted(self.historique, reverse=True):
            self.liste_historique.insert("end", f"{jour} : {self.historique[jour]}")


if __name__ == "__main__":
    App().mainloop()
