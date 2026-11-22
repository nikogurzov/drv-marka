#!/usr/bin/env python3
"""Драйвери: проверка, търсене и инсталиране на драйвери за Debian.
   ./drv-marka.py                   прозорец
   ./drv-marka.py --text            проверка в терминала
   ./drv-marka.py --text --search   и търсене на драйвери за устройствата
   ./drv-marka.py --fix             търси и инсталира (пита преди всяко нещо)
   ./drv-marka.py --kernel          кое ядро работи и инсталиране на по-ново (по избор)
   ./drv-marka.py --reset           връща всичко, направено от програмата (като фабрично)
Проверката само чете. Нещо се променя само след „Поправи“ и паролата (pkexec)."""
import os
import subprocess
import sys
import threading

HERE = os.path.dirname(os.path.realpath(__file__))   # realpath: командата drv-marka е символна връзка
sys.path.insert(0, HERE)
import jezgro
from ezik import _

HELPER = os.path.join(HERE, "popravi.py")


def HELP():
    return [
        (_("Как се ползва"), _("1. Програмата сама проверява компютъра. Отгоре пише дали всичко е наред.\n"
                               "2. <b>Намери драйвери</b> търси пакет за всяко устройство без драйвер и липсващ фърмуер.\n"
                               "3. <b>Поправи…</b> показва какво може да се направи. Отметни нужното и въведи паролата си.\n"
                               "4. Рестартирай компютъра, за да се заредят новите драйвери.")),
        (_("Безопасно ли е?"), _("Проверката само чете. Нищо не се инсталира без „Поправи“ и паролата. Преди всяка поправка apt прави проба, "
                                 "а пакетите, които би махнал, се показват в червено. Старите извори на apt се пазят в <tt>/var/backups/drv-marka</tt>.")),
        (_("Ако нещо се обърка"), _("• Натисни <b>↶</b> (Върни както беше): маха пакетите, сложени от програмата, и връща старите извори.\n"
                                    "• Ако новото ядро не тръгва, избери старото в менюто при стартиране и пусни „Върни“ оттам.\n"
                                    "• От терминала: <tt>drv-marka --reset</tt>")),
        (_("NVIDIA"), _("<b>Ядро Linux</b> и „Намери драйвери“ ползват nvidia-detect на Debian, за да предложат правилния драйвер. "
                        "При Secure Boot след рестарт се иска потвърждение на ключа (MOK).")),
        (_("Команден ред"), _("<tt>drv-marka --text --search</tt>  проверка и търсене в терминала\n<tt>drv-marka --fix</tt>  пита за всяка поправка\n"
                              "<tt>drv-marka --kernel</tt>  по-ново ядро\n<tt>drv-marka --reset</tt>  връща всичко както беше")),
        (_("Проблем или идея?"), _("Пиши в GitHub: <a href=\"https://github.com/nikogurzov/drv-marka/issues\">github.com/nikogurzov/drv-marka/issues</a>")),
    ]


def main_text(deep):
    print(jezgro.as_text(jezgro.collect(deep=deep)), end="")


def main_fix():
    r = jezgro.collect(lambda s: print(s), deep=True)
    if not r.fixes:
        print(_("Няма какво да се инсталира."))
        return
    chosen = []
    for f in r.fixes:
        d = _("Д/н") if f.default else _("д/Н")
        a = input(_(f"{f.title}\n  {f.detail}\n  Да го направя ли? [{d}] ")).strip().lower()
        if a in ("д", "да", "y", "yes") or (a == "" and f.default):
            chosen.append(f)
    if chosen:
        sys.exit(subprocess.run(jezgro.fix_command(chosen, HELPER)).returncode)


def main_kernel():
    k = jezgro.kernels()
    print(_(f"Сега работи ядро {k.running}. Инсталирани: {', '.join(k.installed)}"))
    if not k.options:
        print(_("Няма по-ново ядро за този компютър."))
        return
    for f in k.options:
        a = input(_(f"{f.title}\n  {f.detail}\n  Да го инсталирам ли? [д/Н] ")).strip().lower()
        if a in ("д", "да", "y", "yes"):
            sys.exit(subprocess.run(jezgro.fix_command([f], HELPER)).returncode)


def main_reset():
    h = jezgro.history()
    if not h:
        print(_("Програмата не е променяла нищо. Няма какво да връщам."))
        return
    pk = sorted({p for e in h for p in e.get("packages", [])})
    print(_("Ще махна пакетите, сложени от програмата:"), " ".join(pk) or _("няма"))
    print(_("Ще върна старите извори на apt и групите на потребителя."))
    if input(_("Да продължа ли? [д/Н] ")).strip().lower() in ("д", "да", "y", "yes"):
        sys.exit(subprocess.run(jezgro.reset_command(HELPER)).returncode)


def main_gui():
    try:
        import gi
        gi.require_version("Gtk", "4.0")
        gi.require_version("Gdk", "4.0")
        from gi.repository import Gdk, Gio, GLib, Gtk, Pango
    except (ImportError, ValueError):
        print(_("Липсва GTK 4 за прозореца. Инсталирай го с:\n  sudo apt install python3-gi gir1.2-gtk-4.0\n"
              "Дотогава работи в терминала: drv-marka.py --text --search  или  drv-marka.py --fix\n"))
        main_text(False)
        return

    CSS = b"""
    .ok { color: #1b7f3b; } .warn { color: #b3261e; } .info { color: alpha(currentColor, .6); }
    .verdict { font-size: 18pt; font-weight: bold; padding: 8px 16px 0 16px; }
    .sub { padding: 0 16px 8px 16px; opacity: .7; }
    .name { font-weight: bold; }
    .small { font-size: 90%; opacity: .75; }
    .log { font-family: monospace; font-size: 90%; }
    row { padding: 6px 12px; }
    """

    class FixWin(Gtk.Window):
        """Отметки какво да се направи, после изходът от apt."""
        def __init__(self, parent, fixes, on_done, reset=None, head=None, title=None):
            super().__init__(transient_for=parent, modal=True, title=title or (_("Върни както беше") if reset else _("Поправи")), default_width=640, default_height=520)
            self.on_done, self.fixes, self.reset = on_done, fixes, reset
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin_top=12, margin_bottom=12, margin_start=12, margin_end=12)
            self.set_child(box)
            head = reset or head or _("Избери какво да направя. Ще поискам паролата ти.")
            box.append(Gtk.Label(label=head, xalign=0, css_classes=["name"], wrap=True))
            lb = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
            self.checks = []
            for f in ([] if reset else fixes):
                c = Gtk.CheckButton(active=f.default)
                v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                v.append(Gtk.Label(label=f.title, xalign=0, css_classes=["name"], wrap=True))
                v.append(Gtk.Label(label=f.detail, xalign=0, css_classes=["small", "warn"] if f.removes else ["small"], wrap=True))
                c.set_child(v)
                self.checks.append(c)
                lb.append(c)
            self.top = Gtk.ScrolledWindow(child=lb, vexpand=True)
            box.append(self.top)
            self.buf = Gtk.TextBuffer()
            self.view = Gtk.TextView(buffer=self.buf, editable=False, monospace=True, css_classes=["log"], wrap_mode=Gtk.WrapMode.WORD_CHAR)
            self.logsw = Gtk.ScrolledWindow(child=self.view, vexpand=True, visible=False)
            box.append(self.logsw)
            bar = Gtk.Box(spacing=8, halign=Gtk.Align.END)
            self.close_b = Gtk.Button(label=_("Затвори"))
            self.close_b.connect("clicked", lambda *_a: self.close())
            self.go = Gtk.Button(label=_("Върни") if reset else _("Инсталирай") if title else _("Поправи"), css_classes=["destructive-action" if reset else "suggested-action"])
            self.go.connect("clicked", self.start)
            bar.append(self.close_b)
            bar.append(self.go)
            self.go.set_visible(bool(fixes) or bool(reset))
            box.append(bar)
            self.connect("close-request", self.closing)
            self.ran = False

        def add(self, s):
            self.buf.insert(self.buf.get_end_iter(), s)
            self.view.scroll_to_mark(self.buf.get_insert(), 0, False, 0, 1)
            return False

        def start(self, *_a):
            chosen = [f for f, c in zip(self.fixes, self.checks) if c.get_active()]
            if not chosen and not self.reset:
                return
            self.ran = True
            self.go.set_sensitive(False)
            self.close_b.set_sensitive(False)
            self.top.set_visible(False)
            self.logsw.set_visible(True)
            cmd = jezgro.reset_command(HELPER) if self.reset else jezgro.fix_command(chosen, HELPER)

            def work():
                try:
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace", bufsize=1)
                    for line in p.stdout:
                        GLib.idle_add(self.add, line)
                    code = p.wait()
                except OSError as e:
                    GLib.idle_add(self.add, f"{e}\n")
                    code = 1
                msg = {0: "", 126: _("\nОтказано: паролата не беше въведена.\n"), 127: _("\nОтказано: паролата не беше въведена.\n")}.get(code, _(f"\nСпря с грешка (код {code}).\n"))
                GLib.idle_add(self.add, msg)
                GLib.idle_add(self.close_b.set_sensitive, True)
            threading.Thread(target=work, daemon=True).start()

        def closing(self, *_a):
            if self.ran:
                self.on_done()
            return False

    class Win(Gtk.ApplicationWindow):
        def __init__(self, app):
            super().__init__(application=app, title=_("Драйвери (drv-marka)"), default_width=860, default_height=700)
            self.report, self.deep = None, False
            head = Gtk.HeaderBar()
            self.set_titlebar(head)
            self.btn = Gtk.Button(icon_name="view-refresh-symbolic", tooltip_text=_("Провери отново"))
            self.btn.connect("clicked", lambda *_a: self.load(self.deep))
            head.pack_start(self.btn)
            self.find_b = Gtk.Button(label=_("Намери драйвери"), tooltip_text=_("Търси драйвери и пакети за всяко устройство"))
            self.find_b.connect("clicked", lambda *_a: self.load(True))
            head.pack_start(self.find_b)
            self.kern_b = Gtk.Button(label=_("Ядро Linux"), tooltip_text=_("Кое ядро работи и има ли по-ново"))
            self.kern_b.connect("clicked", self.kernel)
            head.pack_start(self.kern_b)
            menu = Gio.Menu()
            menu.append(_("Помощ"), "app.help")
            menu.append(_("За програмата"), "app.about")
            head.pack_end(Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=menu, tooltip_text=_("Меню"), primary=True))
            copy = Gtk.Button(icon_name="edit-copy-symbolic", tooltip_text=_("Копирай всичко като текст"))
            copy.connect("clicked", self.copy)
            head.pack_end(copy)
            self.fix_b = Gtk.Button(label=_("Поправи…"), css_classes=["suggested-action"], sensitive=False)
            self.fix_b.connect("clicked", self.fix)
            head.pack_end(self.fix_b)
            self.reset_b = Gtk.Button(icon_name="edit-undo-symbolic", tooltip_text=_("Върни както беше: маха всичко, сложено от програмата"), sensitive=False)
            self.reset_b.connect("clicked", self.undo)
            head.pack_end(self.reset_b)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.set_child(box)
            self.title_l = Gtk.Label(xalign=0, css_classes=["verdict"], label=_("Проверявам…"), wrap=True)
            self.sub_l = Gtk.Label(xalign=0, css_classes=["sub"], wrap=True)
            box.append(self.title_l)
            box.append(self.sub_l)
            self.search = Gtk.SearchEntry(placeholder_text=_("Търси драйвер или устройство"), margin_start=12, margin_end=12, margin_bottom=8)
            self.search.connect("search-changed", lambda *_a: self.fill())
            box.append(self.search)
            sw = Gtk.StackSwitcher(halign=Gtk.Align.CENTER, margin_bottom=6)
            self.stack = Gtk.Stack(vexpand=True)
            sw.set_stack(self.stack)
            box.append(sw)
            box.append(self.stack)
            self.lists = {}
            for key, title in (("check", _("Проверка")), ("dev", _("Устройства")), ("mod", _("Заредени драйвери")), ("pkg", _("Фърмуер и пакети"))):
                lb = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
                sc = Gtk.ScrolledWindow(child=lb)
                self.stack.add_titled(sc, key, title)
                self.lists[key] = lb
            self.load(False)

        def load(self, deep):
            self.deep = deep
            for b in (self.btn, self.find_b, self.fix_b, self.reset_b):
                b.set_sensitive(False)
            self.title_l.set_text(_("Търся драйвери…") if deep else _("Проверявам…"))
            self.title_l.remove_css_class("ok")
            self.title_l.remove_css_class("warn")

            def work():
                r = jezgro.collect(lambda s: GLib.idle_add(self.sub_l.set_text, s), deep=deep)
                GLib.idle_add(self.done, r)
            threading.Thread(target=work, daemon=True).start()

        def done(self, r):
            self.report = r
            lvl, text = jezgro.verdict(r)
            self.title_l.set_text(text)
            self.title_l.add_css_class(lvl if lvl != jezgro.INFO else "ok")
            how = _("Търсенето е направено.") if r.deep else _("За по-задълбочено търсене натисни „Намери драйвери“.")
            self.sub_l.set_text(_(f"{r.system}, ядро {r.kernel}. {how}"))
            self.btn.set_sensitive(True)
            self.find_b.set_sensitive(True)
            self.fix_b.set_sensitive(bool(r.fixes))
            self.fix_b.set_label(_(f"Поправи ({len(r.fixes)})…") if r.fixes else _("Поправи…"))
            self.reset_b.set_sensitive(bool(r.history))
            self.fill()
            return False

        def row(self, lb, level, title, sub="", right=""):
            mark = {jezgro.OK: "✓", jezgro.WARN: "!", jezgro.INFO: "•"}[level]
            h = Gtk.Box(spacing=12)
            h.append(Gtk.Label(label=mark, css_classes=[level, "name"], valign=Gtk.Align.START))
            v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True)
            v.append(Gtk.Label(label=title, xalign=0, css_classes=["name"], wrap=True, selectable=True))
            if sub:
                v.append(Gtk.Label(label=sub, xalign=0, css_classes=["small"], wrap=True, selectable=True))
            h.append(v)
            if right:
                h.append(Gtk.Label(label=right, css_classes=["small"], valign=Gtk.Align.START, selectable=True, ellipsize=Pango.EllipsizeMode.END, max_width_chars=26))
            lb.append(h)

        def fill(self):
            r = self.report
            if not r:
                return
            q = self.search.get_text().strip().lower()
            hit = lambda *a: not q or q in " ".join(a).lower()
            for lb in self.lists.values():
                while (c := lb.get_first_child()):
                    lb.remove(c)
            lc = self.lists["check"]
            for f in r.findings:
                if hit(f.title, f.detail, f.package):
                    self.row(lc, f.level, f.title, f.detail)
            for x in r.limits:
                if hit(x):
                    self.row(lc, jezgro.INFO, _("Не беше проверено"), x)
            if lc.get_first_child() is None and not q:
                self.row(lc, jezgro.OK, _("Няма какво да се прави"), _("Не намерих липсващи драйвери или фърмуер."))
            for d in sorted(r.devices, key=lambda d: ({jezgro.WARN: 0, jezgro.OK: 1, jezgro.INFO: 2}[d.state], d.bus, d.kind)):
                if hit(d.name, d.kind, d.driver, d.bus):
                    self.row(self.lists["dev"], d.state, d.name, f"{d.bus} · {d.kind}" + (f"\n{d.note}" if d.note else ""), d.driver or _("без драйвер"))
            for m in r.modules:
                if hit(m.name, m.description):
                    self.row(self.lists["mod"], jezgro.OK, m.name, m.description, f"{m.size_kb} KB")
            for p in r.packages:
                if hit(p.name, p.summary):
                    self.row(self.lists["pkg"], jezgro.OK, p.name, p.summary, p.version)

        def fix(self, *_a):
            if self.report and self.report.fixes:
                FixWin(self, self.report.fixes, lambda: self.load(self.deep)).present()

        def kernel(self, *_a):
            self.kern_b.set_sensitive(False)

            def work():
                k = jezgro.kernels()
                GLib.idle_add(show, k)

            def show(k):
                self.kern_b.set_sensitive(True)
                inst = "\n".join(f"  • {v}" + (_("  ← работи сега") if v == k.running else "") for v in k.installed)
                text = _(f"Сега работи ядро {k.running}.\nИнсталирани:\n{inst}\n\n")
                text += (_("Може да се сложи (не е отметнато, избери само ако имаш нужда, например нов хардуер без драйвер):")
                         if k.options else _("Няма по-ново ядро за този компютър."))
                FixWin(self, k.options, lambda: self.load(self.deep), head=text, title=_("Ядро Linux")).present()
                return False
            threading.Thread(target=work, daemon=True).start()

        def undo(self, *_a):
            h = self.report.history if self.report else []
            if not h:
                return
            pk = sorted({p for e in h for p in e.get("packages", [])})
            text = (_("Ще махна всичко, сложено от програмата, и ще върна старите извори на apt.\n\n"
                    f"Пакети ({len(pk)}): {', '.join(pk) or 'няма'}\n\nПосле рестартирай компютъра."))
            FixWin(self, [], lambda: self.load(self.deep), reset=text).present()

        def copy(self, *_a):
            if self.report:
                self.get_clipboard().set(jezgro.as_text(self.report))
                self.sub_l.set_text(_("Копирано."))

    def about(*_a):
        d = Gtk.AboutDialog(transient_for=app.get_active_window(), modal=True, program_name=_("Драйвери (drv-marka)"),
                            logo_icon_name="preferences-system", version=jezgro.VERSION, authors=["Nikolay Gurzov"],
                            website="https://github.com/nikogurzov/drv-marka", website_label="GitHub",
                            license_type=Gtk.License.MIT_X11, copyright="© 2026 Nikolay Gurzov",
                            comments=_("Проверка, търсене и инсталиране на драйвери за Debian — с „Върни както беше“."))
        d.present()

    def help_(*_a):
        w = Gtk.Window(application=app, transient_for=app.get_active_window(), modal=True, title=_("Помощ"), default_width=620, default_height=620)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14, margin_top=16, margin_bottom=16, margin_start=18, margin_end=18)
        for title, body in HELP():
            box.append(Gtk.Label(label=title, xalign=0, css_classes=["name"]))
            box.append(Gtk.Label(label=body, xalign=0, wrap=True, use_markup=True, selectable=True))
        w.set_child(Gtk.ScrolledWindow(child=box))
        w.present()
        GLib.idle_add(lambda: (w.set_focus(None), False)[1])

    def activate(app):
        p = Gtk.CssProvider()
        p.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), p, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        Win(app).present()

    app = Gtk.Application(application_id="com.palamarka.drvmarka", flags=Gio.ApplicationFlags.FLAGS_NONE)
    for name, fn, acc in (("help", help_, "F1"), ("about", about, None)):
        a = Gio.SimpleAction.new(name, None)
        a.connect("activate", fn)
        app.add_action(a)
        if acc:
            app.set_accels_for_action("app." + name, [acc])
    app.connect("activate", activate)
    app.run([sys.argv[0]])


if __name__ == "__main__":
    if "--version" in sys.argv:
        print("drv-marka", jezgro.VERSION)
    elif "--fix" in sys.argv:
        main_fix()
    elif "--reset" in sys.argv:
        main_reset()
    elif "--kernel" in sys.argv:
        main_kernel()
    elif "--text" in sys.argv:
        main_text("--search" in sys.argv)
    else:
        main_gui()
