import threading

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from launcher.commands import AnomalyInstall, FullInstall, GammaSetup, Usvfs


class Args:
    """Arguments sent to gamma-launcher module."""

    def __init__(self):
        self.anomaly = ''
        self.gamma = ''
        self.cache_path = ''
        self.anomaly_verify = ''
        self.anomaly_purge_cache = ''
        self.custom_def = ''
        self.custom_repo = 'Grokitach/Stalker_GAMMA'
        self.gamma_install_mo = True
        self.mo_version = 'v2.4.4'
        self.final = ''
        self.update_def = True
        self.anomaly_patch = True


class StackWindow(Gtk.ApplicationWindow):
    """Window with stacked tabs."""

    def __init__(self, **kargs):
        super().__init__(**kargs, title='Gamma Launcher')

        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)
        self.set_icon_name('applications-games')
        self.stack = Gtk.Stack()
        self.stack.props.transition_type = Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        self.stack.props.transition_duration = 1000
        self.set_child(self.stack)

    def add_titled_to_stack(self, object_t, name, label):
        self.stack.add_titled(object_t, name, label)

    def init_stack(self):
        self.stack_switcher = Gtk.StackSwitcher()
        self.stack_switcher.set_stack(self.stack)
        self.header.set_title_widget(self.stack_switcher)


def on_activate(app):
    # Create window
    gui = GuiAnomalyInstall()
    gui.generic_tab('Install Anomaly', ['Anomaly Dir', 'Cache Dir'], gui.anomaly_install)
    gui.generic_tab(
        'Full Gamma Setup', ['Anomaly Dir', 'Gamma Dir', 'Custom Gamma Definition', 'Custom Gamma Repository', 'Cache Dir'], gui.full_install
    )
    gui.generic_tab('Partial Gamma Setup', ['Anomaly Dir', 'Gamma Dir', 'Custom Gamma Definition', 'Custom Gamma Repository'], gui.gamma_setup)
    gui.generic_tab('Full Gamma Install', ['Anomaly Dir', 'Gamma Dir', 'Final Gamma Dir'], gui.gamma_usvfs)


class GuiAnomalyInstall:
    """Gui for Gamma-Launcher."""

    def __init__(self):
        self.entries = {'default': []}
        self.thread = threading.Thread()
        self.win = StackWindow(application=app)
        checkbutton = Gtk.CheckButton()
        checkbutton.props.hexpand = True
        checkbutton.props.halign = Gtk.Align.CENTER
        self.win.init_stack()
        self.win.present()

    def generic_tab(self, name, list_inputs, install_fnct):
        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        listbox = Gtk.ListBox()
        listbox.props.selection_mode = Gtk.SelectionMode.NONE
        listbox.props.show_separators = True
        row = Gtk.ListBoxRow()
        hbox = Gtk.ListBox()
        row.set_child(hbox)  # We set the Box as the ListBoxRow child
        self.entries[name] = []
        for i in list_inputs:
            hbox.append(Gtk.Label(label=i))
            entry = Gtk.Entry()
            self.entries[name].append(entry)
            hbox.append(entry)
        self.button = Gtk.Button()
        self.button.set_label('Execute')
        self.button.connect('clicked', install_fnct)
        hbox.append(self.button)
        listbox.append(row)
        box_outer.append(listbox)
        self.win.add_titled_to_stack(box_outer, name, name)
        self.win.init_stack()

    def gamma_launcher_worker(self, target, button, args):
        try:
            target(args)
        except:
            button.set_label('Failed, Try Again?')
        else:
            button.set_label('Executed, Run Again?')

    def anomaly_install(self, button):
        if self.thread.is_alive():
            return
        button.set_label('Executing')
        anomaly_dir = self.entries['Install Anomaly'][0].get_chars(0, -1)
        cache_dir = self.entries['Install Anomaly'][1].get_chars(0, -1)
        anomaly_install = AnomalyInstall()
        args = Args()
        args.anomaly = anomaly_dir
        args.cache_path = cache_dir

        self.thread = threading.Thread(target=self.gamma_launcher_worker, args=(anomaly_install.run, button, args))
        self.thread.start()

    def full_install(self, button):
        if self.thread.is_alive():
            return
        button.set_label('Executing')
        anomaly_dir = self.entries['Full Gamma Setup'][0].get_chars(0, -1)
        gamma_dir = self.entries['Full Gamma Setup'][1].get_chars(0, -1)
        custom_def = self.entries['Full Gamma Setup'][2].get_chars(0, -1)
        custom_repo = self.entries['Full Gamma Setup'][3].get_chars(0, -1)
        cache_dir = self.entries['Full Gamma Setup'][4].get_chars(0, -1)
        full_install = FullInstall()
        args = Args()
        args.anomaly = anomaly_dir
        args.gamma = gamma_dir
        args.custom_def = custom_def if custom_def else ''
        args.custom_repo = custom_repo if custom_repo else 'Grokitach/Stalker_GAMMA'
        args.cache_path = cache_dir

        self.thread = threading.Thread(target=self.gamma_launcher_worker, args=(full_install.run, button, args))
        self.thread.start()

    def gamma_setup(self, button):
        if self.thread.is_alive():
            return
        button.set_label('Executing')
        anomaly_dir = self.entries['Partial Gamma Setup'][0].get_chars(0, -1)
        gamma_dir = self.entries['Partial Gamma Setup'][1].get_chars(0, -1)
        custom_def = self.entries['Partial Gamma Setup'][2].get_chars(0, -1)
        custom_repo = self.entries['Partial Gamma Setup'][3].get_chars(0, -1)
        gamma_setup = GammaSetup()
        args = Args()
        args.anomaly = anomaly_dir
        args.gamma = gamma_dir
        args.custom_def = custom_def if custom_def else ''
        args.custom_repo = custom_repo if custom_repo else 'Grokitach/Stalker_GAMMA'

        self.thread = threading.Thread(target=self.gamma_launcher_worker, args=(gamma_setup.run, button, args))
        self.thread.start()

    def gamma_usvfs(self, button):
        if self.thread.is_alive():
            return
        button.set_label('Executing')
        anomaly_dir = self.entries['Full Gamma Install'][0].get_chars(0, -1)
        gamma_dir = self.entries['Full Gamma Install'][1].get_chars(0, -1)
        final = self.entries['Full Gamma Install'][2].get_chars(0, -1)
        gamma_usvfs = Usvfs()
        args = Args()
        args.anomaly = anomaly_dir
        args.gamma = gamma_dir
        args.final = final

        self.thread = threading.Thread(target=self.gamma_launcher_worker, args=(gamma_usvfs.run, button, args))
        self.thread.start()

app = Gtk.Application(application_id='org.gamma_launcher')
app.connect('activate', on_activate)

def main():
    app.run(None)

if __name__ == "__main__":
    main()
