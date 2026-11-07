"""
Cricket Performance Management Dashboard
Student: Gurukiran G N
Register Number: 25SSDS415020

A single-file Tkinter + SQLite application.
Run: python cricket_dashboard.py
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "cricket_dashboard.db"

# ----------------------------- DATABASE ---------------------------------

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_database():
    """Create the three related tables without deleting existing records."""
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                opponent_team TEXT NOT NULL,
                match_date TEXT NOT NULL,
                FOREIGN KEY (player_id)
                    REFERENCES players(player_id) ON DELETE CASCADE
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS performance_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                stat_name TEXT NOT NULL,
                stat_value REAL NOT NULL,
                FOREIGN KEY (match_id)
                    REFERENCES matches(match_id) ON DELETE CASCADE
            )
        """)

        # Add sample data only when the database has no players.
        cur.execute("SELECT COUNT(*) FROM players")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO players (player_name, email) VALUES (?, ?)",
                [
                    ("Rahul", "rahul@gmail.com"),
                    ("Virat", "virat@gmail.com"),
                    ("Rohit", "rohit@gmail.com")
                ]
            )
            cur.executemany(
                """INSERT INTO matches (player_id, opponent_team, match_date)
                   VALUES (?, ?, ?)""",
                [
                    (1, "Team A", "2026-10-10"),
                    (1, "Team B", "2026-10-15"),
                    (2, "Team A", "2026-10-10"),
                    (3, "Team C", "2026-10-20")
                ]
            )
            cur.executemany(
                """INSERT INTO performance_items (match_id, stat_name, stat_value)
                   VALUES (?, ?, ?)""",
                [
                    (1, "Runs", 75),
                    (1, "Wickets", 2),
                    (2, "Runs", 45),
                    (3, "Runs", 90),
                    (3, "Catches", 1),
                    (4, "Wickets", 3)
                ]
            )


# ----------------------------- APPLICATION -------------------------------

class CricketDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Cricket Performance Management System")
        self.root.geometry("1250x780")
        self.root.minsize(1050, 650)
        self.root.configure(bg="#eef3f7")

        self.green = "#145b36"
        self.dark_green = "#10452d"
        self.light_green = "#e0f2e8"
        self.bg = "#eef3f7"
        self.white = "#ffffff"
        self.text = "#183b2b"

        self.selected_player_id = None
        self.selected_match_id = None
        self.selected_performance_id = None

        self.setup_style()
        self.build_header()
        self.build_tabs()
        self.refresh_all()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=29, font=("Segoe UI", 10),
                        background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                        background=self.green, foreground="white")
        style.map("Treeview.Heading", background=[("active", self.dark_green)])
        style.configure("TNotebook", background=self.bg, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"),
                        padding=(18, 10))
        style.map("TNotebook.Tab",
                  background=[("selected", self.green), ("!selected", "#dce8e1")],
                  foreground=[("selected", "white"), ("!selected", self.text)])
        style.configure("TButton", font=("Segoe UI", 10), padding=7)
        style.configure("Green.TButton", background=self.green, foreground="white")
        style.map("Green.TButton", background=[("active", self.dark_green)])

    def build_header(self):
        header = tk.Frame(self.root, bg=self.dark_green, height=105)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="CRICKET ANALYTICS",
                 font=("Segoe UI", 25, "bold"), bg=self.dark_green,
                 fg="white").pack(anchor="w", padx=30, pady=(17, 0))
        tk.Label(header, text="PLAYER PERFORMANCE AND MATCH MANAGEMENT SYSTEM",
                 font=("Segoe UI", 10), bg=self.dark_green,
                 fg="#cce8d8").pack(anchor="w", padx=32, pady=(2, 0))

    def build_tabs(self):
        container = tk.Frame(self.root, bg=self.bg)
        container.pack(fill="both", expand=True, padx=18, pady=14)

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)

        self.dashboard_tab = tk.Frame(self.notebook, bg=self.bg)
        self.players_tab = tk.Frame(self.notebook, bg=self.bg)
        self.matches_tab = tk.Frame(self.notebook, bg=self.bg)
        self.performance_tab = tk.Frame(self.notebook, bg=self.bg)
        self.analytics_tab = tk.Frame(self.notebook, bg=self.bg)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.players_tab, text="Players")
        self.notebook.add(self.matches_tab, text="Matches")
        self.notebook.add(self.performance_tab, text="Performance")
        self.notebook.add(self.analytics_tab, text="Analytics")

        self.build_dashboard_tab()
        self.build_players_tab()
        self.build_matches_tab()
        self.build_performance_tab()
        self.build_analytics_tab()

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def section_title(self, parent, title):
        tk.Label(parent, text=title, font=("Segoe UI", 19, "bold"),
                 bg=self.bg, fg=self.green).pack(anchor="w", pady=(10, 12))

    def make_tree(self, parent, columns, headings, widths=None):
        frame = tk.Frame(parent, bg=self.white, bd=1, relief="solid")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        for i, (col, heading) in enumerate(zip(columns, headings)):
            tree.heading(col, text=heading)
            width = widths[i] if widths else 150
            tree.column(col, width=width, anchor="center")
        yscroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=yscroll.set)
        tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        return frame, tree

    def build_dashboard_tab(self):
        self.section_title(self.dashboard_tab, "Performance Overview")

        top = tk.Frame(self.dashboard_tab, bg=self.bg)
        top.pack(fill="x", pady=(0, 12))
        self.stat_labels = {}
        for key, title in [
            ("players", "TOTAL PLAYERS"),
            ("matches", "TOTAL MATCHES"),
            ("runs", "TOTAL RUNS"),
            ("wickets", "TOTAL WICKETS"),
            ("records", "PERFORMANCE RECORDS")
        ]:
            card = tk.Frame(top, bg=self.white, bd=1, relief="solid")
            card.pack(side="left", fill="both", expand=True, padx=5, ipady=9)
            tk.Label(card, text=title, bg=self.white, fg="#536477",
                     font=("Segoe UI", 9, "bold")).pack(pady=(8, 3))
            value = tk.Label(card, text="0", bg=self.white, fg=self.green,
                             font=("Segoe UI", 23, "bold"))
            value.pack(pady=(0, 5))
            self.stat_labels[key] = value

        highlight_row = tk.Frame(self.dashboard_tab, bg=self.bg)
        highlight_row.pack(fill="x", pady=5)
        self.top_runs_label = tk.Label(highlight_row, text="TOP RUN SCORER\nNo data",
                                       bg=self.light_green, fg=self.text,
                                       font=("Segoe UI", 12, "bold"),
                                       justify="left", padx=18, pady=15)
        self.top_runs_label.pack(side="left", fill="both", expand=True, padx=5)
        self.top_wickets_label = tk.Label(highlight_row, text="TOP WICKET TAKER\nNo data",
                                          bg=self.light_green, fg=self.text,
                                          font=("Segoe UI", 12, "bold"),
                                          justify="left", padx=18, pady=15)
        self.top_wickets_label.pack(side="left", fill="both", expand=True, padx=5)

        lower = tk.Frame(self.dashboard_tab, bg=self.bg)
        lower.pack(fill="both", expand=True, pady=8)

        left = tk.LabelFrame(lower, text="PLAYER LEADERBOARD",
                             bg=self.white, fg=self.green,
                             font=("Segoe UI", 10, "bold"), padx=6, pady=6)
        left.pack(side="left", fill="both", expand=True, padx=5)
        self.leader_tree_frame, self.leader_tree = self.make_tree(
            left, ("player", "matches", "runs", "wickets"),
            ("Player", "Matches", "Runs", "Wickets"), (150, 90, 100, 100))
        self.leader_tree_frame.pack(fill="both", expand=True)

        right = tk.LabelFrame(lower, text="RECENT PERFORMANCES",
                              bg=self.white, fg=self.green,
                              font=("Segoe UI", 10, "bold"), padx=6, pady=6)
        right.pack(side="left", fill="both", expand=True, padx=5)
        self.recent_frame, self.recent_tree = self.make_tree(
            right, ("player", "opponent", "date", "stat", "value"),
            ("Player", "Opponent", "Date", "Stat", "Value"),
            (110, 105, 105, 100, 75))
        self.recent_frame.pack(fill="both", expand=True)

        tk.Button(self.dashboard_tab, text="↻ Refresh Data",
                  command=self.refresh_all, bg=self.green, fg="white",
                  activebackground=self.dark_green, activeforeground="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  padx=15, pady=7).pack(anchor="e", pady=5)

    # ----------------------------- PLAYERS --------------------------------

    def build_players_tab(self):
        self.section_title(self.players_tab, "Player Management")
        form = tk.LabelFrame(self.players_tab, text="Player Details",
                             bg=self.bg, fg=self.green,
                             font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        form.pack(fill="x", padx=5, pady=5)

        tk.Label(form, text="Player name", bg=self.bg).grid(row=0, column=0, sticky="w")
        self.player_name_entry = ttk.Entry(form, width=28)
        self.player_name_entry.grid(row=1, column=0, padx=(0, 12), pady=5)

        tk.Label(form, text="Email address", bg=self.bg).grid(row=0, column=1, sticky="w")
        self.player_email_entry = ttk.Entry(form, width=32)
        self.player_email_entry.grid(row=1, column=1, padx=(0, 12), pady=5)

        ttk.Button(form, text="Add Player", style="Green.TButton",
                   command=self.add_player).grid(row=1, column=2, padx=4)
        ttk.Button(form, text="Update Selected",
                   command=self.update_player).grid(row=1, column=3, padx=4)
        ttk.Button(form, text="Delete Selected",
                   command=self.delete_player).grid(row=1, column=4, padx=4)
        ttk.Button(form, text="Clear",
                   command=self.clear_player_form).grid(row=1, column=5, padx=4)

        search_row = tk.Frame(self.players_tab, bg=self.bg)
        search_row.pack(fill="x", padx=5, pady=8)
        tk.Label(search_row, text="Search player:", bg=self.bg).pack(side="left")
        self.player_search = tk.StringVar()
        search_entry = ttk.Entry(search_row, textvariable=self.player_search, width=30)
        search_entry.pack(side="left", padx=8)
        self.player_search.trace_add("write", lambda *_: self.load_players())

        self.players_tree_frame, self.players_tree = self.make_tree(
            self.players_tab, ("id", "name", "email"),
            ("Player ID", "Player Name", "Email"), (110, 250, 300))
        self.players_tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.players_tree.bind("<<TreeviewSelect>>", self.select_player)

    def add_player(self):
        name = self.player_name_entry.get().strip()
        email = self.player_email_entry.get().strip()
        if not name or not email:
            messagebox.showwarning("Missing details", "Enter both player name and email.")
            return
        if "@" not in email or "." not in email:
            messagebox.showwarning("Invalid email", "Enter a valid email address.")
            return
        try:
            with get_connection() as conn:
                conn.execute("INSERT INTO players (player_name, email) VALUES (?, ?)",
                             (name, email))
            self.clear_player_form()
            self.refresh_all()
            messagebox.showinfo("Success", "Player added successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This player name already exists.")

    def select_player(self, _event=None):
        selected = self.players_tree.selection()
        if not selected:
            return
        values = self.players_tree.item(selected[0], "values")
        self.selected_player_id = int(values[0])
        self.player_name_entry.delete(0, "end")
        self.player_name_entry.insert(0, values[1])
        self.player_email_entry.delete(0, "end")
        self.player_email_entry.insert(0, values[2])

    def update_player(self):
        if not self.selected_player_id:
            messagebox.showwarning("Select player", "Select a player from the table first.")
            return
        name = self.player_name_entry.get().strip()
        email = self.player_email_entry.get().strip()
        if not name or not email:
            messagebox.showwarning("Missing details", "Enter both player name and email.")
            return
        try:
            with get_connection() as conn:
                conn.execute("""UPDATE players SET player_name=?, email=?
                                WHERE player_id=?""",
                             (name, email, self.selected_player_id))
            self.clear_player_form()
            self.refresh_all()
            messagebox.showinfo("Success", "Player updated successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "That player name is already in use.")

    def delete_player(self):
        if not self.selected_player_id:
            messagebox.showwarning("Select player", "Select a player from the table first.")
            return
        if messagebox.askyesno("Confirm delete",
                               "Delete this player and all their matches and performance records?"):
            with get_connection() as conn:
                conn.execute("DELETE FROM players WHERE player_id=?",
                             (self.selected_player_id,))
            self.clear_player_form()
            self.refresh_all()

    def clear_player_form(self):
        self.selected_player_id = None
        self.player_name_entry.delete(0, "end")
        self.player_email_entry.delete(0, "end")
        if hasattr(self, "players_tree"):
            self.players_tree.selection_remove(self.players_tree.selection())

    def load_players(self):
        if not hasattr(self, "players_tree"):
            return
        for item in self.players_tree.get_children():
            self.players_tree.delete(item)
        search = self.player_search.get().strip() if hasattr(self, "player_search") else ""
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT player_id, player_name, email FROM players
                WHERE player_name LIKE ? OR email LIKE ?
                ORDER BY player_name
            """, (f"%{search}%", f"%{search}%")).fetchall()
        for row in rows:
            self.players_tree.insert("", "end", values=row)

    # ----------------------------- MATCHES ---------------------------------

    def build_matches_tab(self):
        self.section_title(self.matches_tab, "Match Management")
        form = tk.LabelFrame(self.matches_tab, text="Add Match",
                             bg=self.bg, fg=self.green,
                             font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        form.pack(fill="x", padx=5, pady=5)

        tk.Label(form, text="Player", bg=self.bg).grid(row=0, column=0, sticky="w")
        self.match_player_var = tk.StringVar()
        self.match_player_combo = ttk.Combobox(form, textvariable=self.match_player_var,
                                               state="readonly", width=25)
        self.match_player_combo.grid(row=1, column=0, padx=(0, 12), pady=5)

        tk.Label(form, text="Opponent team", bg=self.bg).grid(row=0, column=1, sticky="w")
        self.opponent_entry = ttk.Entry(form, width=25)
        self.opponent_entry.grid(row=1, column=1, padx=(0, 12), pady=5)

        tk.Label(form, text="Match date (YYYY-MM-DD)", bg=self.bg).grid(row=0, column=2, sticky="w")
        self.match_date_entry = ttk.Entry(form, width=22)
        self.match_date_entry.grid(row=1, column=2, padx=(0, 12), pady=5)

        ttk.Button(form, text="Add Match", style="Green.TButton",
                   command=self.add_match).grid(row=1, column=3, padx=4)
        ttk.Button(form, text="Delete Selected",
                   command=self.delete_match).grid(row=1, column=4, padx=4)

        self.matches_tree_frame, self.matches_tree = self.make_tree(
            self.matches_tab, ("id", "player", "opponent", "date"),
            ("Match ID", "Player", "Opponent Team", "Match Date"),
            (100, 200, 220, 180))
        self.matches_tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.matches_tree.bind("<<TreeviewSelect>>", self.select_match)

    def add_match(self):
        player_label = self.match_player_var.get()
        opponent = self.opponent_entry.get().strip()
        date = self.match_date_entry.get().strip()
        if not player_label or not opponent or not date:
            messagebox.showwarning("Missing details", "Complete all match fields.")
            return
        try:
            from datetime import datetime
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid date", "Use YYYY-MM-DD format, for example 2026-11-07.")
            return
        player_id = int(player_label.split(" | ")[0])
        with get_connection() as conn:
            conn.execute("""INSERT INTO matches (player_id, opponent_team, match_date)
                            VALUES (?, ?, ?)""", (player_id, opponent, date))
        self.opponent_entry.delete(0, "end")
        self.match_date_entry.delete(0, "end")
        self.refresh_all()
        messagebox.showinfo("Success", "Match added successfully.")

    def select_match(self, _event=None):
        selected = self.matches_tree.selection()
        if selected:
            self.selected_match_id = int(self.matches_tree.item(selected[0], "values")[0])

    def delete_match(self):
        if not self.selected_match_id:
            messagebox.showwarning("Select match", "Select a match from the table first.")
            return
        if messagebox.askyesno("Confirm delete",
                               "Delete this match and its performance records?"):
            with get_connection() as conn:
                conn.execute("DELETE FROM matches WHERE match_id=?",
                             (self.selected_match_id,))
            self.selected_match_id = None
            self.refresh_all()

    def load_matches(self):
        for item in self.matches_tree.get_children():
            self.matches_tree.delete(item)
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT m.match_id, p.player_name, m.opponent_team, m.match_date
                FROM matches m JOIN players p ON m.player_id=p.player_id
                ORDER BY m.match_date DESC, m.match_id DESC
            """).fetchall()
        for row in rows:
            self.matches_tree.insert("", "end", values=row)

    def load_player_choices(self):
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT player_id, player_name FROM players ORDER BY player_name"
            ).fetchall()
        self.match_player_combo["values"] = [
            f"{player_id} | {name}" for player_id, name in rows
        ]
        if rows and not self.match_player_var.get():
            self.match_player_var.set(f"{rows[0][0]} | {rows[0][1]}")

    # -------------------------- PERFORMANCE -------------------------------

    def build_performance_tab(self):
        self.section_title(self.performance_tab, "Performance Management")
        form = tk.LabelFrame(self.performance_tab, text="Add Performance Record",
                             bg=self.bg, fg=self.green,
                             font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        form.pack(fill="x", padx=5, pady=5)

        tk.Label(form, text="Match", bg=self.bg).grid(row=0, column=0, sticky="w")
        self.performance_match_var = tk.StringVar()
        self.performance_match_combo = ttk.Combobox(
            form, textvariable=self.performance_match_var,
            state="readonly", width=35)
        self.performance_match_combo.grid(row=1, column=0, padx=(0, 12), pady=5)

        tk.Label(form, text="Statistic", bg=self.bg).grid(row=0, column=1, sticky="w")
        self.stat_var = tk.StringVar(value="Runs")
        self.stat_combo = ttk.Combobox(form, textvariable=self.stat_var,
                                       values=("Runs", "Wickets", "Catches"),
                                       state="readonly", width=18)
        self.stat_combo.grid(row=1, column=1, padx=(0, 12), pady=5)

        tk.Label(form, text="Value", bg=self.bg).grid(row=0, column=2, sticky="w")
        self.stat_value_entry = ttk.Entry(form, width=15)
        self.stat_value_entry.grid(row=1, column=2, padx=(0, 12), pady=5)

        ttk.Button(form, text="Add Record", style="Green.TButton",
                   command=self.add_performance).grid(row=1, column=3, padx=4)
        ttk.Button(form, text="Delete Selected",
                   command=self.delete_performance).grid(row=1, column=4, padx=4)

        self.performance_tree_frame, self.performance_tree = self.make_tree(
            self.performance_tab, ("id", "player", "opponent", "date", "stat", "value"),
            ("Record ID", "Player", "Opponent", "Date", "Statistic", "Value"),
            (90, 150, 150, 130, 130, 100))
        self.performance_tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.performance_tree.bind("<<TreeviewSelect>>", self.select_performance)

    def load_match_choices(self):
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT m.match_id, p.player_name, m.opponent_team, m.match_date
                FROM matches m JOIN players p ON m.player_id=p.player_id
                ORDER BY m.match_date DESC
            """).fetchall()
        self.performance_match_combo["values"] = [
            f"{mid} | {player} vs {opponent} | {date}"
            for mid, player, opponent, date in rows
        ]
        if rows and not self.performance_match_var.get():
            mid, player, opponent, date = rows[0]
            self.performance_match_var.set(f"{mid} | {player} vs {opponent} | {date}")
        if not rows:
            self.performance_match_var.set("")

    def add_performance(self):
        match_label = self.performance_match_var.get()
        stat = self.stat_var.get()
        value_text = self.stat_value_entry.get().strip()
        if not match_label or not value_text:
            messagebox.showwarning("Missing details", "Select a match and enter a value.")
            return
        try:
            value = float(value_text)
            if value < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid value", "Enter a non-negative number.")
            return
        match_id = int(match_label.split(" | ")[0])
        with get_connection() as conn:
            conn.execute("""INSERT INTO performance_items
                            (match_id, stat_name, stat_value)
                            VALUES (?, ?, ?)""", (match_id, stat, value))
        self.stat_value_entry.delete(0, "end")
        self.refresh_all()
        messagebox.showinfo("Success", "Performance record added successfully.")

    def select_performance(self, _event=None):
        selected = self.performance_tree.selection()
        if selected:
            self.selected_performance_id = int(
                self.performance_tree.item(selected[0], "values")[0]
            )

    def delete_performance(self):
        if not self.selected_performance_id:
            messagebox.showwarning("Select record", "Select a record from the table first.")
            return
        if messagebox.askyesno("Confirm delete", "Delete this performance record?"):
            with get_connection() as conn:
                conn.execute("DELETE FROM performance_items WHERE item_id=?",
                             (self.selected_performance_id,))
            self.selected_performance_id = None
            self.refresh_all()

    def load_performance(self):
        for item in self.performance_tree.get_children():
            self.performance_tree.delete(item)
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT pi.item_id, p.player_name, m.opponent_team,
                       m.match_date, pi.stat_name, pi.stat_value
                FROM performance_items pi
                JOIN matches m ON pi.match_id=m.match_id
                JOIN players p ON m.player_id=p.player_id
                ORDER BY m.match_date DESC, pi.item_id DESC
            """).fetchall()
        for row in rows:
            self.performance_tree.insert("", "end", values=row)

    # ----------------------------- DASHBOARD -------------------------------

    def refresh_dashboard(self):
        with get_connection() as conn:
            cur = conn.cursor()
            players = cur.execute("SELECT COUNT(*) FROM players").fetchone()[0]
            matches = cur.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
            records = cur.execute("SELECT COUNT(*) FROM performance_items").fetchone()[0]
            runs = cur.execute("""
                SELECT COALESCE(SUM(stat_value), 0)
                FROM performance_items WHERE lower(stat_name)='runs'
            """).fetchone()[0]
            wickets = cur.execute("""
                SELECT COALESCE(SUM(stat_value), 0)
                FROM performance_items WHERE lower(stat_name)='wickets'
            """).fetchone()[0]

            self.stat_labels["players"].config(text=str(players))
            self.stat_labels["matches"].config(text=str(matches))
            self.stat_labels["runs"].config(text=f"{runs:g}")
            self.stat_labels["wickets"].config(text=f"{wickets:g}")
            self.stat_labels["records"].config(text=str(records))

            top_runs = cur.execute("""
                SELECT p.player_name, SUM(pi.stat_value) AS total
                FROM performance_items pi
                JOIN matches m ON pi.match_id=m.match_id
                JOIN players p ON m.player_id=p.player_id
                WHERE lower(pi.stat_name)='runs'
                GROUP BY p.player_id ORDER BY total DESC LIMIT 1
            """).fetchone()
            top_wickets = cur.execute("""
                SELECT p.player_name, SUM(pi.stat_value) AS total
                FROM performance_items pi
                JOIN matches m ON pi.match_id=m.match_id
                JOIN players p ON m.player_id=p.player_id
                WHERE lower(pi.stat_name)='wickets'
                GROUP BY p.player_id ORDER BY total DESC LIMIT 1
            """).fetchone()

            self.top_runs_label.config(
                text=("TOP RUN SCORER\n" + f"{top_runs[0]} - {top_runs[1]:g} runs")
                if top_runs else "TOP RUN SCORER\nNo data"
            )
            self.top_wickets_label.config(
                text=("TOP WICKET TAKER\n" + f"{top_wickets[0]} - {top_wickets[1]:g} wickets")
                if top_wickets else "TOP WICKET TAKER\nNo data"
            )

            leaderboard = cur.execute("""
                SELECT p.player_name,
                       COUNT(DISTINCT m.match_id),
                       COALESCE(SUM(CASE WHEN lower(pi.stat_name)='runs'
                                         THEN pi.stat_value ELSE 0 END), 0),
                       COALESCE(SUM(CASE WHEN lower(pi.stat_name)='wickets'
                                         THEN pi.stat_value ELSE 0 END), 0)
                FROM players p
                LEFT JOIN matches m ON p.player_id=m.player_id
                LEFT JOIN performance_items pi ON m.match_id=pi.match_id
                GROUP BY p.player_id
                ORDER BY 3 DESC, 4 DESC
            """).fetchall()

            recent = cur.execute("""
                SELECT p.player_name, m.opponent_team, m.match_date,
                       pi.stat_name, pi.stat_value
                FROM performance_items pi
                JOIN matches m ON pi.match_id=m.match_id
                JOIN players p ON m.player_id=p.player_id
                ORDER BY m.match_date DESC, pi.item_id DESC LIMIT 10
            """).fetchall()

        for tree in (self.leader_tree, self.recent_tree):
            for item in tree.get_children():
                tree.delete(item)
        for row in leaderboard:
            self.leader_tree.insert("", "end", values=(
                row[0], row[1], f"{row[2]:g}", f"{row[3]:g}"
            ))
        for row in recent:
            self.recent_tree.insert("", "end", values=(
                row[0], row[1], row[2], row[3], f"{row[4]:g}"
            ))

    # ------------------------------ ANALYTICS -------------------------------

    def build_analytics_tab(self):
        self.section_title(self.analytics_tab, "Player Analytics & Comparison")

        chart_frame = tk.LabelFrame(
            self.analytics_tab, text="Player-wise Runs and Wickets",
            bg=self.white, fg=self.green, font=("Segoe UI", 10, "bold"),
            padx=10, pady=8
        )
        chart_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.analytics_canvas = tk.Canvas(
            chart_frame, bg=self.white, height=300,
            highlightthickness=0
        )
        self.analytics_canvas.pack(fill="both", expand=True)
        self.analytics_canvas.bind(
            "<Configure>", lambda _event: self.draw_player_chart()
        )

        comparison_frame = tk.LabelFrame(
            self.analytics_tab, text="Player Performance Comparison",
            bg=self.white, fg=self.green, font=("Segoe UI", 10, "bold"),
            padx=8, pady=8
        )
        comparison_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.comparison_tree_frame, self.comparison_tree = self.make_tree(
            comparison_frame,
            ("player", "matches", "runs", "wickets", "catches", "average"),
            ("Player", "Matches", "Total Runs", "Wickets", "Catches",
             "Runs / Match"),
            (180, 100, 110, 100, 100, 120)
        )
        self.comparison_tree_frame.pack(fill="both", expand=True)

        tk.Button(
            self.analytics_tab, text="Refresh Analytics",
            command=self.refresh_analytics, bg=self.green, fg="white",
            activebackground=self.dark_green, activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat",
            padx=15, pady=7
        ).pack(anchor="e", padx=5, pady=5)

    def get_player_analytics(self):
        with get_connection() as conn:
            return conn.execute("""
                SELECT
                    p.player_name,
                    COUNT(DISTINCT m.match_id) AS matches_played,
                    COALESCE(SUM(CASE
                        WHEN lower(pi.stat_name) = 'runs'
                        THEN pi.stat_value ELSE 0 END), 0) AS total_runs,
                    COALESCE(SUM(CASE
                        WHEN lower(pi.stat_name) = 'wickets'
                        THEN pi.stat_value ELSE 0 END), 0) AS total_wickets,
                    COALESCE(SUM(CASE
                        WHEN lower(pi.stat_name) = 'catches'
                        THEN pi.stat_value ELSE 0 END), 0) AS total_catches
                FROM players p
                LEFT JOIN matches m ON p.player_id = m.player_id
                LEFT JOIN performance_items pi ON m.match_id = pi.match_id
                GROUP BY p.player_id, p.player_name
                ORDER BY total_runs DESC, total_wickets DESC
            """).fetchall()

    def refresh_analytics(self):
        if not hasattr(self, "comparison_tree"):
            return

        rows = self.get_player_analytics()

        for item in self.comparison_tree.get_children():
            self.comparison_tree.delete(item)

        for player, matches, runs, wickets, catches in rows:
            average = runs / matches if matches else 0
            self.comparison_tree.insert(
                "", "end",
                values=(player, matches, f"{runs:g}", f"{wickets:g}",
                        f"{catches:g}", f"{average:.2f}")
            )

        self.analytics_rows = rows
        self.draw_player_chart()

    def draw_player_chart(self):
        if not hasattr(self, "analytics_canvas"):
            return

        canvas = self.analytics_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 500)
        height = max(canvas.winfo_height(), 260)
        rows = getattr(self, "analytics_rows", [])

        if not rows:
            canvas.create_text(
                width / 2, height / 2,
                text="Add players and performance records to view analytics.",
                fill=self.text, font=("Segoe UI", 12)
            )
            return

        # Display the top eight players by total runs.
        chart_rows = rows[:8]
        max_value = max(
            [max(float(row[2]), float(row[3])) for row in chart_rows] + [1]
        )

        left, right, top, bottom = 55, width - 25, 35, height - 55
        chart_height = bottom - top
        chart_width = right - left

        canvas.create_text(
            width / 2, 15, text="Runs and Wickets by Player",
            fill=self.green, font=("Segoe UI", 12, "bold")
        )

        # Horizontal guide lines and scale labels.
        for step in range(5):
            value = max_value * step / 4
            y = bottom - (chart_height * step / 4)
            canvas.create_line(left, y, right, y, fill="#e5ece8")
            canvas.create_text(
                left - 10, y, text=f"{value:.0f}",
                anchor="e", fill="#536477", font=("Segoe UI", 8)
            )

        group_width = chart_width / len(chart_rows)
        bar_width = min(24, group_width * 0.25)

        for index, row in enumerate(chart_rows):
            player, _matches, runs, wickets, _catches = row
            center = left + group_width * (index + 0.5)

            for offset, value, color in [
                (-bar_width / 2, float(runs), "#238b57"),
                (bar_width / 2, float(wickets), "#e0a12f")
            ]:
                bar_height = (value / max_value) * chart_height
                x1 = center + offset - bar_width / 2
                x2 = center + offset + bar_width / 2
                y1 = bottom - bar_height
                canvas.create_rectangle(
                    x1, y1, x2, bottom, fill=color, outline=""
                )
                if value > 0:
                    canvas.create_text(
                        (x1 + x2) / 2, max(y1 - 9, top - 3),
                        text=f"{value:g}", fill=self.text,
                        font=("Segoe UI", 8)
                    )

            canvas.create_text(
                center, bottom + 18, text=player[:12],
                fill=self.text, font=("Segoe UI", 8)
            )

        # Chart legend.
        canvas.create_rectangle(width - 205, 5, width - 193, 17,
                                fill="#238b57", outline="")
        canvas.create_text(width - 187, 11, text="Runs", anchor="w",
                           fill=self.text, font=("Segoe UI", 8))
        canvas.create_rectangle(width - 125, 5, width - 113, 17,
                                fill="#e0a12f", outline="")
        canvas.create_text(width - 107, 11, text="Wickets", anchor="w",
                           fill=self.text, font=("Segoe UI", 8))

    # ------------------------------- HELPERS --------------------------------

    def refresh_all(self):
        self.load_players()
        self.load_matches()
        self.load_performance()
        self.load_player_choices()
        self.load_match_choices()
        self.refresh_dashboard()
        self.refresh_analytics()

    def on_tab_changed(self, _event=None):
        # Refresh displayed information whenever a tab is opened.
        self.refresh_all()


def main():
    create_database()
    root = tk.Tk()
    CricketDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
