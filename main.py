from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, Checkbox
from textual.containers import VerticalScroll, Horizontal
from textual.reactive import reactive
import yaml
from pathlib import Path
from datetime import datetime

TEMPLATE_DIR = Path(__file__).parent / "templates"
OUTPUT_DIR = Path(__file__).parent / "packing"
OUTPUT_DIR.mkdir(exist_ok=True)

class PackingApp(App):
    CSS_PATH = None
    BINDINGS = [("q", "quit", "Quit")]

    selected_topics = reactive(set)
    checklist_data = reactive([])

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Select Topics:")
        with VerticalScroll(id="topics"):
            for file in TEMPLATE_DIR.glob("*.yaml"):
                name = file.stem
                yield Checkbox(name)
        yield Button("Confirm Selections", id="confirm")
        yield Static("Checklist Output (grouped by section):")
        self.output_box = VerticalScroll(id="output")
        yield self.output_box
        with Horizontal():
            yield Button("Save Checklist", id="save")
            yield Button("Quit", id="quit")
        yield Footer()

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
        elif event.button.id == "save":
            self.save_checklist()
        elif event.button.id == "quit":
            self.exit()

    def generate_checklist(self):
        all_items = []
        for topic in self.selected_topics:
            path = TEMPLATE_DIR / f"{topic}.yaml"
            if path.exists():
                with open(path) as f:
                    items = yaml.safe_load(f) or []
                    all_items.extend(items)

        unique = {}
        for entry in all_items:
            key = entry["item"].strip().lower()
            if key not in unique:
                unique[key] = entry

        grouped = {}
        for entry in unique.values():
            section = entry.get("section", "Misc")
            grouped.setdefault(section, []).append(entry["item"])

        self.checklist_data = grouped

        self.output_box.remove_children()
        for section in sorted(grouped.keys()):
            self.output_box.mount(Static(f"## {section}"))
            for item in sorted(grouped[section]):
                self.output_box.mount(Static(f"[ ] {item}"))

    def save_checklist(self):
        if not self.checklist_data:
            return
        now = datetime.now().strftime("%Y-%m-%d")
        out_path = OUTPUT_DIR / f"{now}-trip.md"
        with open(out_path, "w") as f:
            for section in sorted(self.checklist_data.keys()):
                f.write(f"## {section}\n")
                for item in sorted(self.checklist_data[section]):
                    f.write(f"- [ ] {item}\n")
                f.write("\n")
        self.output_box.mount(Static(f"Saved to {out_path}"))

if __name__ == "__main__":
    app = PackingApp()
    app.run()
