# image_toggle_gallery.py

import ipywidgets as widgets
from IPython.display import HTML, clear_output, display


def make_img_html(srcs: list[str], width="90%") -> str:
    """
    Convenience helper: from a list of image paths/URLs, build an HTML block.
    """
    parts = [
        f'<img src="{src}" width="{width}" style="display:block;margin:auto;">' for src in srcs
    ]
    return "\n".join(parts)


class ImageToggleGallery:
    """
    A mutually-exclusive image gallery for Jupyter using ipywidgets.

    - Each entry (page) is a ToggleButton + Output area.
    - Opening one page closes others; toggling the same page again hides it.
    - You can add/remove/replace pages and call refresh() to rebuild the UI.
    """

    def __init__(
        self,
        image_sets: dict[str, str],
        *,
        include_close_all: bool = False,
        button_style: str = "",  # e.g. "primary", "warning" (ipywidgets styles)
        layout: widgets.Layout | None = None,
    ):
        """
        Args:
            image_sets: dict mapping name -> HTML (e.g., from make_img_html or raw <img> tags)
            include_close_all: if True, shows a "Close all pages" button
            button_style: ipywidgets button_style for toggle buttons
            layout: optional layout for the outer VBox
        """
        self.image_sets: dict[str, str] = dict(image_sets)
        self.include_close_all = include_close_all
        self.button_style = button_style
        self.layout = layout

        # runtime state
        self._buttons: dict[str, widgets.ToggleButton] = {}
        self._outputs: dict[str, widgets.Output] = {}

        # the root widget you can display
        # self.container = widgets.VBox(layout=self.layout)
        self.container = widgets.VBox() if self.layout is None else widgets.VBox(layout=self.layout)
        self.refresh()

    # ---------- public API ----------

    def display(self):
        """Display the whole gallery."""
        display(self.container)

    def add_set(self, name: str, html: str):
        """Add a new page/set."""
        self.image_sets[name] = html

    def remove_set(self, name: str):
        """Remove a page/set if it exists."""
        self.image_sets.pop(name, None)

    def replace_set(self, name: str, html: str):
        """Replace or create a page/set."""
        self.image_sets[name] = html

    def rename_set(self, old: str, new: str):
        """Rename a page/set, preserving content (no-op if old not found)."""
        if old in self.image_sets:
            self.image_sets[new] = self.image_sets.pop(old)

    def refresh(self):
        """Rebuild the UI from current image_sets."""
        self._buttons.clear()
        self._outputs.clear()

        rows = []
        for name in self.image_sets:
            btn = widgets.ToggleButton(
                description=f"Show {name}", value=False, button_style=self.button_style
            )
            out = widgets.Output()
            btn.observe(lambda ch, n=name: self._on_toggle(ch, n), names="value")
            self._buttons[name] = btn
            self._outputs[name] = out
            rows.append(widgets.VBox([btn, out]))

        if self.include_close_all:
            close_all_btn = widgets.Button(description="Close all pages")
            close_all_btn.on_click(self._close_all)
            self.container.children = (widgets.VBox([close_all_btn, widgets.VBox(rows)]),)
        else:
            self.container.children = (widgets.VBox(rows),)

    # ---------- internals ----------

    def _show_html(self, name: str):
        # render chosen
        with self._outputs[name]:
            clear_output()
            display(HTML(self.image_sets[name]))
        # close everyone else
        for other in self.image_sets:
            if other != name:
                with self._outputs[other]:
                    clear_output()
                if self._buttons[other].value:
                    self._buttons[other].value = False

    def _hide_html(self, name: str):
        with self._outputs[name]:
            clear_output()

    def _on_toggle(self, change, name: str):
        if change.get("name") != "value":
            return
        if change["new"] is True:
            self._show_html(name)
            self._buttons[name].description = f"Hide {name}"
        else:
            self._hide_html(name)
            self._buttons[name].description = f"Show {name}"

    def _close_all(self, _=None):
        for name in self.image_sets:
            if self._buttons[name].value:
                self._buttons[name].value = False
            else:
                self._hide_html(name)
            self._buttons[name].description = f"Show {name}"
