from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, Checkbox
from textual.containers import VerticalScroll, Horizontal
from textual.reactive import reactive
import yaml
from pathlib import Path
from datetime import datetime
import subprocess

TEMPLATE_DIR = Path(__file__).parent / "templates"
OUTPUT_DIR = Path(__file__).parent / "packing"
OUTPUT_DIR.mkdir(exist_ok=True)

SYMBOLS = ["*", "#", "$", "@", "&", "%", "+", "!", "^", "~"]

class PackingApp(App):
    CSS_PATH = None
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("t", "toggle_tags", "Toggle Topic Tags"),
        ("e", "export_pdf", "Export PDF")
    ]

    selected_topics = reactive(set)
    checklist_data = reactive([])
    topic_symbols = reactive({})
    tag_mode = reactive(False)
    last_markdown_path = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("[b]Select Topics:[/b]")
        with VerticalScroll(id="topics"):
            for file in TEMPLATE_DIR.glob("*.yaml"):
                name = file.stem
                yield Checkbox(name)
        with Horizontal():
            yield Button("Confirm Selections", id="confirm")
            yield Button("Toggle Tags", id="toggle")
            yield Button("Save Checklist", id="save")
            yield Button("Export PDF", id="export")
            yield Button("Quit", id="quit")
        yield Static("[b]Checklist Output:[/b]")
        self.output_box = VerticalScroll(id="output")
        yield self.output_box
        yield Footer()

    def action_toggle_tags(self):
        self.tag_mode = not self.tag_mode
        self.generate_checklist()

    def action_export_pdf(self):
        self.export_to_pdf()

    def on_mount(self):
        self.selected_topics = set()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.value:
            self.selected_topics.add(event.checkbox.label)
        else:
            self.selected_topics.discard(event.checkbox.label)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.generate_checklist()
        elif event.button.id == "toggle":
            self.action_toggle_tags()
        elif event.button.id == "save":
            self.save_checklist()
        elif event.button.id == "export":
            self.export_to_pdf()
        elif event.button.id == "quit":
            self.exit()

    def generate_checklist(self):
        all_items = {}
        topic_map = {}

        sorted_topics = sorted(self.selected_topics)
        symbol_map = {topic: SYMBOLS[i % len(SYMBOLS)] for i, topic in enumerate(sorted_topics)}
        self.topic_symbols = symbol_map

        for topic in sorted_topics:
            path = TEMPLATE_DIR / f"{topic}.yaml"
            if path.exists():
                with open(path) as f:
                    data = yaml.safe_load(f) or {}
                    for section, items in data.items():
                        for item in items:
                            key = item.strip().lower()
                            if key not in all_items:
                                all_items[key] = (item, section)
                                topic_map[key] = topic

        grouped = {}
        for key, (item, section) in all_items.items():
            grouped.setdefault(section, []).append((item, topic_map[key]))

        self.checklist_data = grouped
        self.output_box.remove_children()

        for section in sorted(grouped.keys()):
            self.output_box.mount(Static(f"\n[b]{section}[/b]"))
            for item, topic in sorted(grouped[section]):
                suffix = f" {symbol_map[topic]}" if self.tag_mode else ""
                self.output_box.mount(Static(f"- [ ] {item}{suffix}"))

        if self.tag_mode:
            self.output_box.mount(Static("\n[b]Legend[/b]"))
            for topic in sorted_topics:
                self.output_box.mount(Static(f"{symbol_map[topic]} = {topic}"))

    def save_checklist(self):
        if not self.checklist_data:
            return
        now = datetime.now().strftime("%Y-%m-%d")
        out_path = OUTPUT_DIR / f"{now}-trip.md"
        self.last_markdown_path = out_path
        with open(out_path, "w") as f:
            for section in sorted(self.checklist_data.keys()):
                f.write(f"## {section}\n")
                for item, topic in sorted(self.checklist_data[section]):
                    suffix = f" {self.topic_symbols[topic]}" if self.tag_mode else ""
                    f.write(f"- [ ] {item}{suffix}\n")
                f.write("\n")
            if self.tag_mode:
                f.write("## Legend\n")
                for topic in sorted(self.topic_symbols.keys()):
                    f.write(f"{self.topic_symbols[topic]} = {topic}\n")
        self.output_box.mount(Static(f"[green]Saved to {out_path}[/green]"))

    def export_to_pdf(self):
        if not self.last_markdown_path:
            self.output_box.mount(Static("[red]You must save the checklist before exporting to PDF.[/red]"))
            return
        pdf_path = self.last_markdown_path.with_suffix(".pdf")
        result = subprocess.run(["python", "export_pdf.py", str(self.last_markdown_path), str(pdf_path)])
        if result.returncode == 0:
            self.output_box.mount(Static(f"[green]Exported PDF to {pdf_path}[/green]"))
        else:
            self.output_box.mount(Static("[red]PDF export failed.[/red]"))

if __name__ == "__main__":
    app = PackingApp()
    app.run()
