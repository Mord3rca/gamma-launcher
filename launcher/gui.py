import sys
import re
import pathlib
import threading
import time
from io import StringIO

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib, Gtk

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
        self.preserve_user_config = False


class Wrapper():
    def __init__(self, function, line):
        self.function = function
        self.line = line
    def __call__(self, button, state):
        self.function(button, state, self.line)


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

    def remove_titled_from_stack(self, name):
        child = self.stack.get_child_by_name(name)
        if child:
            self.stack.remove(child)

    def init_stack(self):
        self.stack_switcher = Gtk.StackSwitcher()
        self.stack_switcher.set_stack(self.stack)
        self.header.set_title_widget(self.stack_switcher)


class GuiAnomalyInstall(Gtk.Application):
    """Gui for Gamma-Launcher."""

    def do_activate(self):
        self.entries = {'default': []}
        self.thread = threading.Thread()
        self.output = StringIO()
        self.textbuffer = Gtk.TextBuffer()
        self.stderr = sys.stderr
        self.stdout = sys.stdout
        if len(sys.argv) > 1 and sys.argv[1] == '--debug':
            print("stdout and stderr aren't redirected")
        else:
            print("Redirecting stdout and stderr")
            sys.stdout = self.output
            sys.stderr = self.output
        self.win = StackWindow(application=app)
        self.mods = []
        self.entry_buffers = {}
        self.load_button = None

        self.win.init_stack()
        self.win.present()

        self.generic_tab('Install Anomaly', ['Anomaly Dir', 'Cache Dir'], self.anomaly_install)
        self.generic_tab('Full Gamma Setup', ['Anomaly Dir', 'Gamma Dir', 'Custom Gamma Definition', 'Custom Gamma Repository', 'Cache Dir'], self.full_install)
        self.generic_tab('Partial Gamma Setup', ['Anomaly Dir', 'Gamma Dir', 'Custom Gamma Definition', 'Custom Gamma Repository', 'Cache Dir'], self.gamma_setup)
        self.generic_tab('Full Gamma Install', ['Anomaly Dir', 'Gamma Dir', 'Final Gamma Dir'], self.gamma_usvfs)
        self.mod_chooser_tab()

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
            if i not in self.entry_buffers:
                self.entry_buffers[i] = Gtk.EntryBuffer()
            entry = Gtk.Entry.new_with_buffer(self.entry_buffers[i])
            self.entries[name].append(entry)
            hbox.append(entry)
        self.button = Gtk.Button()
        self.button.set_label('Execute')
        self.button.connect('clicked', install_fnct)
        hbox.append(self.button)
        # ===============
        textview = Gtk.TextView.new_with_buffer(self.textbuffer)
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        scroll = Gtk.ScrolledWindow()
        scroll.set_child(textview)
        scroll.set_propagate_natural_height(True)
        exp = Gtk.Expander()
        exp.set_child(scroll)
        exp.set_expanded(True)
        exp.set_resize_toplevel(True)
        hbox.append(exp)
        # =============
        listbox.append(row)
        box_outer.append(listbox)
        self.win.add_titled_to_stack(box_outer, name, name)
        self.win.init_stack()

    def load_mods(self, button):
        self.file_name = self.entries['Mod Chooser'][0].get_chars(0, -1)
        self.file_name = pathlib.Path(self.file_name) / 'profiles' / 'G.A.M.M.A' / 'modlist.txt'
        try:
            with open(self.file_name, 'r') as mods:
                self.mods = mods.readlines()
        except:
            self.win.remove_titled_from_stack('Mod Chooser')
            self.mods = []
            self.mod_chooser_tab()
            self.load_button.set_label("modlist.txt not found, try to Load again?")
        else:
            self.win.remove_titled_from_stack('Mod Chooser')
            self.mod_chooser_tab()
            self.load_button.set_label('Loaded, Run Again?')

    def do_switch(self, button, state, line):
        line_content = self.mods [line]
        if state:
            cont_state = '+'
        else:
            cont_state = '-'
        line_content = re.sub(r'^[+-]', cont_state, line_content)
        self.mods[line] = line_content
        with open(self.file_name, 'w') as mods_cont:
            mods_cont.write("".join(self.mods))

    def mod_chooser_tab(self):
        name = 'Mod Chooser'
        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        listbox = Gtk.ListBox()
        listbox.props.selection_mode = Gtk.SelectionMode.NONE
        listbox.props.show_separators = True
        scroll = Gtk.ScrolledWindow()
        scroll.set_propagate_natural_height(True)
        scroll.set_child(listbox)
        row = Gtk.ListBoxRow()
        hbox = Gtk.ListBox()
        hbox.append(Gtk.Label(label='Gamma Dir'))
        if 'Gamma Dir' not in self.entry_buffers:
            self.entry_buffers['Gamma Dir'] = Gtk.EntryBuffer()
        entry = Gtk.Entry.new_with_buffer(self.entry_buffers['Gamma Dir'])
        self.entries[name] = []
        self.entries[name].append(entry)
        self.load_button = Gtk.Button()
        self.load_button.set_label('Load')
        hbox.append(entry)
        hbox.append(self.load_button)
        self.load_button.connect('clicked', self.load_mods)

        mods_number = len(self.mods)
        for i in reversed([j.strip() for j in self.mods]):
            if len(i) == 0 or i[0] == '#':
                mods_number -= 1
                continue
            if '_separator' in i:
                mods_number -= 1
                k = re.split(r"[_ ]", i)[1]
                hbox.append(Gtk.Separator())
                hbox.append(Gtk.Label(label=k))
                hbox.append(Gtk.Separator())
            else:
                vbox = Gtk.Box()
                k = i[1:-1]
                state = i[0]
                vbox.set_orientation(Gtk.Orientation.HORIZONTAL)
                switch = Gtk.Switch()
                if state == '+':
                    switch.set_state(True)
                    switch.set_active(True)
                else:
                    switch.set_state(False)
                    switch.set_active(False)
                switch.connect('state_set', Wrapper(self.do_switch, mods_number-1))
                mods_number -= 1
                vbox.append(switch)
                vbox.append(Gtk.Label(label=k))
                hbox.append(vbox)
        #hbox.append(vbox)
        row.set_child(hbox)
        #hbox.append(vbox)
        listbox.append(row)
        box_outer.append(scroll)
        self.win.add_titled_to_stack(box_outer, name, name)

    def gamma_terminal_worker(self):
        self.textbuffer.insert(self.textbuffer.get_end_iter(), self.output.getvalue())
        self.output.truncate(0)
        self.output.seek(0)
        time.sleep(0.1)
        if self.thread.is_alive():
            return True
        else:
            return False

    def gamma_launcher_worker(self, target, button, args):
        GLib.idle_add(self.gamma_terminal_worker)
        try:
            target(args)
        except:
            button.set_label('Failed, Try Again?')
        else:
            button.set_label('Executed, Run Again?')
        finally:
            self.gamma_terminal_worker()

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
        cache_dir = self.entries['Full Gamma Setup'][4].get_chars(0, -1)
        gamma_setup = GammaSetup()
        args = Args()
        args.anomaly = anomaly_dir
        args.gamma = gamma_dir
        args.custom_def = custom_def if custom_def else ''
        args.custom_repo = custom_repo if custom_repo else 'Grokitach/Stalker_GAMMA'
        args.cache_path = cache_dir

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


app = GuiAnomalyInstall()


def main():
    GLib.threads_init()
    app.run(None)


if __name__ == '__main__':
    main()
