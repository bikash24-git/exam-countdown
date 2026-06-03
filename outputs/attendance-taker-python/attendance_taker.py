import csv
import json
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk


APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "attendance_data.json"


class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Taker")
        self.root.geometry("1180x740")
        self.root.minsize(980, 640)

        self.people = []
        self.sessions = []
        self.current_status = {}
        self.session_title = tk.StringVar(value=f"Session - {datetime.now().strftime('%d %b %Y')}")
        self.search_text = tk.StringVar()

        self.present_color = "#00f5a0"
        self.absent_color = "#ff4d6d"
        self.blue = "#5b8cff"
        self.violet = "#9d4edd"
        self.cyan = "#00d4ff"
        self.bg = "#070b18"
        self.panel = "#0e172a"
        self.panel_2 = "#111c34"
        self.field = "#0a1022"
        self.line = "#243451"
        self.ink = "#eaf2ff"
        self.muted = "#91a4c4"

        self.load_data()
        self.build_ui()
        self.refresh_people_list()
        self.update_summary()

    def load_data(self):
        if not DATA_FILE.exists():
            return

        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            self.people = data.get("people", [])
            self.sessions = data.get("sessions", [])
        except json.JSONDecodeError:
            messagebox.showwarning("Data issue", "Saved attendance data could not be read.")

    def save_data_file(self):
        data = {
            "people": self.people,
            "sessions": self.sessions,
        }
        DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def build_ui(self):
        self.root.configure(bg=self.bg)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            rowheight=40,
            font=("Segoe UI", 10),
            background=self.field,
            fieldbackground=self.field,
            foreground=self.ink,
            bordercolor=self.line,
            lightcolor=self.line,
            darkcolor=self.line,
        )
        style.map(
            "Treeview",
            background=[("selected", "#1d3b70")],
            foreground=[("selected", "#ffffff")],
        )
        style.configure(
            "Treeview.Heading",
            background="#17243d",
            foreground=self.cyan,
            bordercolor=self.line,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.configure(
            "Vertical.TScrollbar",
            background="#1a2742",
            troughcolor=self.field,
            bordercolor=self.line,
            arrowcolor=self.cyan,
        )

        header = tk.Frame(self.root, bg=self.bg)
        header.pack(fill="x", padx=28, pady=(22, 10))

        title_wrap = tk.Frame(header, bg=self.bg)
        title_wrap.pack(side="left")

        tk.Label(
            title_wrap,
            text="ATTENDANCE COMMAND CENTER",
            bg=self.bg,
            fg=self.cyan,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

        title = tk.Label(
            title_wrap,
            text="Attendance Taker",
            bg=self.bg,
            fg=self.ink,
            font=("Segoe UI", 30, "bold"),
        )
        title.pack(anchor="w")

        tk.Label(
            title_wrap,
            text="Real-time present and absent tracking with live visual analytics",
            bg=self.bg,
            fg=self.muted,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(2, 0))

        self.make_button(header, "New Session", self.new_session, self.blue).pack(side="right", pady=(8, 0))

        session_row = tk.Frame(self.root, bg=self.bg)
        session_row.pack(fill="x", padx=28, pady=(0, 16))

        tk.Label(session_row, text="Session name", bg=self.bg, fg=self.muted, font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Entry(
            session_row,
            textvariable=self.session_title,
            bg=self.field,
            fg=self.ink,
            insertbackground=self.cyan,
            relief="flat",
            borderwidth=1,
            font=("Segoe UI", 11, "bold"),
            width=42,
        ).pack(side="left", padx=(10, 0))

        content = tk.Frame(self.root, bg=self.bg)
        content.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        left = tk.Frame(content, bg=self.panel, highlightbackground=self.line, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(content, bg=self.bg, width=330)
        right.pack(side="right", fill="y", padx=(18, 0))
        right.pack_propagate(False)

        controls = tk.Frame(left, bg=self.panel)
        controls.pack(fill="x", padx=14, pady=14)

        tk.Entry(
            controls,
            textvariable=self.search_text,
            bg=self.field,
            fg=self.ink,
            insertbackground=self.cyan,
            relief="flat",
            borderwidth=1,
            font=("Segoe UI", 10),
            width=30,
        ).pack(side="left")
        self.search_text.trace_add("write", lambda *_: self.refresh_people_list())

        self.make_button(controls, "Add Person", self.add_person, self.present_color).pack(side="left", padx=(10, 0))
        self.make_button(controls, "Edit", self.edit_person, "#52627f").pack(side="left", padx=(8, 0))
        self.make_button(controls, "Delete", self.delete_person, self.absent_color).pack(side="left", padx=(8, 0))

        table_wrap = tk.Frame(left, bg=self.panel)
        table_wrap.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        columns = ("name", "status")
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text="Name")
        self.tree.heading("status", text="Attendance")
        self.tree.column("name", width=300, anchor="w")
        self.tree.column("status", width=140, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)

        actions = tk.Frame(left, bg=self.panel)
        actions.pack(fill="x", padx=14, pady=(0, 14))
        self.make_button(actions, "Mark Present", self.mark_present, self.present_color).pack(side="left")
        self.make_button(actions, "Mark Absent", self.mark_absent, self.absent_color).pack(side="left", padx=(10, 0))
        self.make_button(actions, "Save Session", self.save_session, self.blue).pack(side="right")
        self.make_button(actions, "Export CSV", self.export_csv, self.violet).pack(side="right", padx=(0, 10))

        self.build_summary_panel(right)
        self.build_history_panel(right)

    def build_summary_panel(self, parent):
        panel = tk.Frame(parent, bg=self.panel, highlightbackground=self.line, highlightthickness=1)
        panel.pack(fill="x")

        tk.Label(panel, text="LIVE SUMMARY", bg=self.panel, fg=self.cyan, font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=16, pady=(16, 2)
        )
        tk.Label(panel, text="Attendance Pulse", bg=self.panel, fg=self.ink, font=("Segoe UI", 18, "bold")).pack(
            anchor="w", padx=16, pady=(0, 6)
        )

        cards = tk.Frame(panel, bg=self.panel)
        cards.pack(fill="x", padx=14, pady=(6, 8))

        self.total_value = self.make_metric(cards, "TOTAL", self.blue)
        self.present_value = self.make_metric(cards, "PRESENT", self.present_color)
        self.absent_value = self.make_metric(cards, "ABSENT", self.absent_color)

        self.percent_label = tk.Label(panel, text="", bg=self.panel, fg=self.muted, font=("Segoe UI", 10, "bold"))
        self.percent_label.pack(anchor="w", padx=16, pady=(0, 10))

        self.chart = tk.Canvas(panel, width=280, height=250, bg=self.panel, highlightthickness=0)
        self.chart.pack(padx=14, pady=(0, 14))

    def build_history_panel(self, parent):
        panel = tk.Frame(parent, bg=self.panel, highlightbackground=self.line, highlightthickness=1)
        panel.pack(fill="both", expand=True, pady=(18, 0))

        tk.Label(panel, text="SESSION ARCHIVE", bg=self.panel, fg=self.cyan, font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=16, pady=(16, 2)
        )
        tk.Label(panel, text="Saved Sessions", bg=self.panel, fg=self.ink, font=("Segoe UI", 18, "bold")).pack(
            anchor="w", padx=16, pady=(0, 8)
        )

        self.history = tk.Listbox(
            panel,
            bg=self.field,
            fg=self.ink,
            relief="flat",
            font=("Segoe UI", 10),
            activestyle="none",
            selectbackground="#1d3b70",
            selectforeground="#ffffff",
            highlightthickness=1,
            highlightbackground=self.line,
        )
        self.history.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        self.history.bind("<Double-Button-1>", lambda _: self.load_selected_session())

        self.make_button(panel, "Open Selected Session", self.load_selected_session, "#52627f").pack(
            fill="x", padx=16, pady=(0, 16)
        )
        self.refresh_history()

    def make_metric(self, parent, label, color):
        card = tk.Frame(parent, bg=self.panel_2, highlightbackground=self.line, highlightthickness=1)
        card.pack(side="left", fill="x", expand=True, padx=3)

        tk.Label(card, text=label, bg=self.panel_2, fg=color, font=("Segoe UI", 8, "bold")).pack(pady=(8, 0))
        value = tk.Label(card, text="0", bg=self.panel_2, fg=self.ink, font=("Segoe UI", 18, "bold"))
        value.pack(pady=(0, 8))
        return value

    def make_button(self, parent, text, command, color):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="#06111f" if color in (self.present_color, self.cyan) else "white",
            activebackground=color,
            activeforeground="#06111f" if color in (self.present_color, self.cyan) else "white",
            relief="flat",
            bd=0,
            padx=16,
            pady=10,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )

    def filtered_people(self):
        query = self.search_text.get().strip().lower()
        if not query:
            return self.people
        return [person for person in self.people if query in person["name"].lower()]

    def refresh_people_list(self):
        self.tree.delete(*self.tree.get_children())
        for person in self.filtered_people():
            status = self.current_status.get(person["id"], "Absent")
            tag = "present" if status == "Present" else "absent"
            self.tree.insert("", "end", iid=person["id"], values=(person["name"], status), tags=(tag,))
        self.tree.tag_configure("present", foreground=self.present_color)
        self.tree.tag_configure("absent", foreground=self.absent_color)

    def refresh_history(self):
        if not hasattr(self, "history"):
            return
        self.history.delete(0, "end")
        for session in reversed(self.sessions):
            present, absent = self.session_counts(session)
            label = f"{session['title']}  |  P: {present}  A: {absent}"
            self.history.insert("end", label)

    def selected_person_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select person", "Please select a person first.")
            return None
        return selected[0]

    def add_person(self):
        name = simpledialog.askstring("Add person", "Enter person name:")
        if not name:
            return

        person_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.people.append({"id": person_id, "name": name.strip()})
        self.current_status[person_id] = "Absent"
        self.save_data_file()
        self.refresh_people_list()
        self.update_summary()

    def edit_person(self):
        person_id = self.selected_person_id()
        if not person_id:
            return

        person = self.find_person(person_id)
        if not person:
            return

        new_name = simpledialog.askstring("Edit person", "Update person name:", initialvalue=person["name"])
        if not new_name:
            return

        person["name"] = new_name.strip()
        self.save_data_file()
        self.refresh_people_list()

    def delete_person(self):
        person_id = self.selected_person_id()
        if not person_id:
            return

        person = self.find_person(person_id)
        if not person:
            return

        confirm = messagebox.askyesno("Delete person", f"Delete {person['name']}?")
        if not confirm:
            return

        self.people = [item for item in self.people if item["id"] != person_id]
        self.current_status.pop(person_id, None)
        self.save_data_file()
        self.refresh_people_list()
        self.update_summary()

    def find_person(self, person_id):
        return next((person for person in self.people if person["id"] == person_id), None)

    def mark_present(self):
        self.mark_selected("Present")

    def mark_absent(self):
        self.mark_selected("Absent")

    def mark_selected(self, status):
        person_id = self.selected_person_id()
        if not person_id:
            return
        self.current_status[person_id] = status
        self.refresh_people_list()
        self.tree.selection_set(person_id)
        self.update_summary()

    def new_session(self):
        confirm = messagebox.askyesno("New session", "Start a new blank attendance session?")
        if not confirm:
            return

        self.session_title.set(f"Session - {datetime.now().strftime('%d %b %Y')}")
        self.current_status = {person["id"]: "Absent" for person in self.people}
        self.refresh_people_list()
        self.update_summary()

    def save_session(self):
        title = self.session_title.get().strip() or f"Session - {datetime.now().strftime('%d %b %Y')}"
        records = {
            person["id"]: self.current_status.get(person["id"], "Absent")
            for person in self.people
        }

        session = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "title": title,
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "records": records,
        }

        self.sessions.append(session)
        self.save_data_file()
        self.refresh_history()
        messagebox.showinfo("Saved", "Attendance session saved.")

    def load_selected_session(self):
        selected = self.history.curselection()
        if not selected:
            messagebox.showinfo("Select session", "Please select a saved session first.")
            return

        reversed_sessions = list(reversed(self.sessions))
        session = reversed_sessions[selected[0]]
        self.session_title.set(session["title"])
        self.current_status = dict(session.get("records", {}))
        self.refresh_people_list()
        self.update_summary()

    def export_csv(self):
        if not self.people:
            messagebox.showinfo("No data", "Add people before exporting.")
            return

        filename = filedialog.asksaveasfilename(
            title="Export attendance",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="attendance.csv",
        )
        if not filename:
            return

        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Session", self.session_title.get().strip()])
            writer.writerow(["Exported At", datetime.now().strftime("%d %b %Y, %I:%M %p")])
            writer.writerow([])
            writer.writerow(["Name", "Status"])
            for person in self.people:
                writer.writerow([person["name"], self.current_status.get(person["id"], "Absent")])

        messagebox.showinfo("Exported", "Attendance CSV exported successfully.")

    def update_summary(self):
        total = len(self.people)
        present = sum(1 for person in self.people if self.current_status.get(person["id"], "Absent") == "Present")
        absent = total - present
        present_percent = (present / total * 100) if total else 0
        absent_percent = 100 - present_percent if total else 0

        self.total_value.config(text=str(total))
        self.present_value.config(text=str(present))
        self.absent_value.config(text=str(absent))
        self.percent_label.config(text=f"Present {present_percent:.1f}%  |  Absent {absent_percent:.1f}%")
        self.draw_chart(present, absent, present_percent)

    def draw_chart(self, present, absent, present_percent):
        self.chart.delete("all")
        total = present + absent

        self.chart.create_text(140, 20, text="PRESENT VS ABSENT", fill=self.cyan, font=("Segoe UI", 10, "bold"))
        self.chart.create_line(42, 38, 238, 38, fill=self.line, width=1)

        if total == 0:
            self.chart.create_oval(75, 58, 205, 188, outline=self.line, width=18)
            self.chart.create_text(140, 113, text="No data", fill=self.muted, font=("Segoe UI", 13, "bold"))
            return

        present_extent = 359.9 * (present / total)
        self.chart.create_oval(65, 50, 215, 200, outline="#17243d", width=26)
        self.chart.create_arc(
            65,
            50,
            215,
            200,
            start=90,
            extent=-present_extent,
            style="arc",
            outline=self.present_color,
            width=24,
        )
        self.chart.create_arc(
            65,
            50,
            215,
            200,
            start=90 - present_extent,
            extent=-(359.9 - present_extent),
            style="arc",
            outline=self.absent_color,
            width=24,
        )

        self.chart.create_oval(92, 77, 188, 173, outline=self.line, width=1)
        self.chart.create_text(140, 116, text=f"{present_percent:.0f}%", fill=self.ink, font=("Segoe UI", 28, "bold"))
        self.chart.create_text(140, 147, text="present", fill=self.muted, font=("Segoe UI", 10, "bold"))

        self.chart.create_rectangle(28, 218, 41, 231, fill=self.present_color, outline="")
        self.chart.create_text(88, 224, text=f"Present {present}", fill=self.ink, font=("Segoe UI", 10, "bold"))
        self.chart.create_rectangle(154, 218, 167, 231, fill=self.absent_color, outline="")
        self.chart.create_text(214, 224, text=f"Absent {absent}", fill=self.ink, font=("Segoe UI", 10, "bold"))

    def session_counts(self, session):
        records = session.get("records", {})
        present = sum(1 for status in records.values() if status == "Present")
        absent = len(records) - present
        return present, absent


def main():
    root = tk.Tk()
    AttendanceApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
