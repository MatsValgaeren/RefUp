from PySide6 import QtWidgets
from PySide6.QtCore import QObject, Signal
from maya import cmds
import json
import os
import re

class IOManager:
    def __init__(self):
        """Initialize the IOManager with the given UI instance."""
        self.script_dir = os.path.dirname(__file__)
        self.settings_path = os.path.abspath(os.path.join(self.script_dir, "..", "prefs", "RefUp", "settings.json"))
        self.scene_name = cmds.file(q=True, sn=True)
        self.global_settings = self.load_settings()
        self.settings = self.global_settings.setdefault(self.scene_name, {'directory': '', 'files_to_update': []})

    def load_settings(self):
        try:
            with open(self.settings_path, 'r') as f:
                settings = json.load(f)
                if self.scene_name not in settings:
                    settings[self.scene_name] = {'directory': '', 'files_to_update': []}
                return settings
        except (json.JSONDecodeError, IOError):
            return {}

    def save_settings(self):
        with open(self.settings_path, 'w') as f:
            json.dump(self.global_settings, f, indent=4)

class StartupManager:
    def __init__(self):
        """Handles setup logic when the script starts."""
        self.io_manager = IOManager()
        self.func_instance = RefupFunc(self.io_manager)
        self.run_startup_tasks()

    def run_startup_tasks(self):
        selected_files = self.get_new_references()
        print(selected_files)
        self.check_and_update(selected_files)

    def get_new_references(self):
        new_files = {}
        ref_up_ui = RefUpUI()
        selected_files = ref_up_ui.get_selected_files()
        print(selected_files)
        for ref_model in selected_files.keys():
            to_update = self.io_manager.settings['files_to_update']
            print(ref_model, to_update)
            ref_model_base = self.extract_base_and_version(os.path.basename(ref_model))[0]
            if ref_model_base in to_update:
                new_files[ref_model] = selected_files[ref_model]
        print(new_files)
        return new_files

    def get_new_referencess(self):
        """Gets the selected files from combo boxes."""
        selected_files = {}

        ref_up_ui = RefUpUI()
        selected_files = ref_up_ui.get_selected_files()
        self.list = self.func_instance.build_list()
        print('list')
        print(self.list)
        print(selected_files)
        for ref_model in selected_files.keys():
            print(ref_model)
            to_update = self.io_manager.settings['files_to_update']
            ref_model_base = self.extract_base_and_version(os.path.basename(ref_model))[0]
            print(ref_model_base, to_update)
            if ref_model in to_update:
                selected_files[list[ref_model]] = self.list[ref_model][-1]
        return selected_files

    def extract_base_and_version(self, filename):
        """Splits filename into base name and version, regardless of extension."""
        match = re.match(r"(.+_)(v\d+)\.(\w+)$", filename)
        if match:
            base, version, ext = match.groups()
            return base, version
        return filename, ""

    def check_and_update(self, scene_list):
        if scene_list:
            self.func_instance.update_references(scene_list)

class UIManager(QObject):
    setting_updated = Signal()

    def __init__(self):
        super().__init__()
        self._settings = {}

    def update_settings(self, key, value):
        self._settings_update.emit()

    def get_settings(self, key):
        return self._settings.get(key)

class RefUpUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(RefUpUI, self).__init__(parent)
        self.setWindowTitle("RefUp")
        self.setMinimumWidth(220)
        self.ui_manager = UIManager()
        self.ui_manager.setting_updated.connect(self.init_ui)
        self.all_dir_field = None
        self.combo_boxes = {}
        self.checkboxes = {}
        self.io_manager = IOManager()
        self.func_instance = RefupFunc(self.io_manager)
        self.ref_to_update = {}
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components and layout."""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.tab_widget = QtWidgets.QTabWidget(central_widget)

        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.addWidget(self.tab_widget)
        layout.addStretch()
        # layout.stretch(0)

        self.update_tab = QtWidgets.QWidget()
        self.settings_tab = QtWidgets.QWidget()

        self.tab_widget.addTab(self.update_tab, "Update")
        self.tab_widget.addTab(self.settings_tab, "Settings")

        self.setup_update_tab()
        self.setup_settings_tab()

        self.adjust_window_height()



    def setup_update_tab(self):
        self.update_layout = QtWidgets.QVBoxLayout(self.update_tab)
        self.load_references()
        if self.io_manager.settings['directory']:
            label_text = "Settings are up to date."
            update_label = self.add_label(label_text, self.update_layout)
            update_label.setStyleSheet("color: green")
        else:
            label_text = "You need to update your settings!"
            update_label = self.add_label(label_text, self.update_layout)
            update_label.setStyleSheet("color: red")
        update_label.setFixedHeight(23)


        # self.add_label(label_text, self.update_layout)
        self.add_divider(self.update_layout)
        self.add_label("Referenced Files:", self.update_layout)
        self.populate_combo_boxes(self.update_tab)
        self.add_divider(self.update_layout)
        self.update_button = self.add_button(
            "Update References",
            lambda: self.func_instance.update_references(self.get_selected_files()),
            self.update_layout
        )

    def setup_settings_tab(self):
        self.settings_layout = QtWidgets.QVBoxLayout(self.settings_tab)
        self.dict_references = self.func_instance.build_list()
        self.all_dir_field = self.add_file_field("Directory: ", self.settings_layout)
        self.add_divider(self.settings_layout)
        self.add_label("Files to Auto-Update:", self.settings_layout)
        # self.add_divider(self.settings_layout)
        self.populate_checkboxes(self.settings_tab)
        self.add_divider(self.settings_layout)
        self.save_button = self.add_button("Update Settings", self.update_settings, self.settings_layout)

    def load_references(self):
        """Loads the references into the UI after initialization."""
        self.dict_references = self.func_instance.build_list()

    def add_divider(self, layout):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        layout.addWidget(line)

    def add_label(self, label, layout):
        layout_ref = QtWidgets.QHBoxLayout()
        lbl = QtWidgets.QLabel(label)
        layout_ref.addWidget(lbl)

        layout.addLayout(layout_ref)
        return lbl

    def add_file_field(self, label, layout):
        """Creates a file input field with a label and browse button."""
        layout_ref = QtWidgets.QHBoxLayout()
        lbl = QtWidgets.QLabel(label)
        lbl.setFixedHeight(20)


        layout_ref.addWidget(lbl)
        text_field = QtWidgets.QLineEdit()

        if self.io_manager.settings:
            directory = self.io_manager.settings.get('directory', "")
            text_field.setText(directory)

        browse_button = QtWidgets.QPushButton("Browse")
        browse_button.clicked.connect(lambda: self.select_directory(text_field))
        browse_button.setFixedHeight(18)
        layout_ref.addWidget(text_field)
        layout_ref.addWidget(browse_button)
        layout.addLayout(layout_ref)
        return text_field

    def add_button(self, label, callback, layout):
        """Creates a button and assigns a callback function."""
        button = QtWidgets.QPushButton(label)
        button.clicked.connect(callback)
        layout.addWidget(button)

    def select_directory(self, text_field):
        """Handles the directory selection event."""
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            text_field.setText(directory)

    def populate_combo_boxes(self, parent_layout):
        """Creates a dropdown for each referenced file and selects the latest one."""
        for ref_model, ref_list in self.dict_references.items():
            base_name, _ = self.extract_base_and_version(os.path.basename(ref_model))
            ref_label = QtWidgets.QLabel(base_name)
            combo_box = QtWidgets.QComboBox()
            combo_box.setFixedWidth(80)
            combo_box.setFixedHeight(20)
            file_map = {}

            for file in ref_list:
                file_name = os.path.basename(file)
                _, version = self.extract_base_and_version(file_name)
                file_map[version] = file

            sorted_versions = sorted(file_map.keys(), key=lambda v: os.path.getmtime(file_map[v]), reverse=True)
            for version in sorted_versions:
                combo_box.addItem(version)

            combo_box.setProperty("file_map", file_map)
            self.combo_boxes[ref_model] = combo_box

            layout = QtWidgets.QHBoxLayout()
            layout.addWidget(ref_label)
            layout.addWidget(combo_box)
            # layout_ref.stretch(10)
            # parent_layout.setLayout(QtWidgets.QVBoxLayout())
            parent_layout = parent_layout.layout()
            parent_layout.addLayout(layout)

    def populate_checkboxes(self, parent_layout):
        """Creates a checkbox for each referenced model."""
        parent_layout = parent_layout.layout()
        seen = set()
        for ref_model in self.dict_references.keys():
            checkbox = QtWidgets.QCheckBox(os.path.basename(ref_model))
            checkbox.setChecked(ref_model in self.io_manager.settings['files_to_update'])
            checkbox.setFixedHeight(20)
            self.checkboxes[ref_model] = checkbox
            layout = QtWidgets.QHBoxLayout()
            layout.addStretch()
            layout.addWidget(checkbox)
            parent_layout.addLayout(layout)

    def extract_base_and_version(self, filename):
        """Splits filename into base name and version, regardless of extension."""
        match = re.match(r"(.+_)(v\d+)\.(\w+)$", filename)
        if match:
            base, version, ext = match.groups()
            return base, version
        return filename, ""

    def get_selected_models(self):
        """Returns a list of selected reference models."""
        return [model for model, checkbox in self.checkboxes.items() if checkbox.isChecked()]

    def get_selected_files(self):
        """Gets the selected files from combo boxes."""
        selected_files = {}
        for ref_name, combo_box in self.combo_boxes.items():
            selected_version = combo_box.currentText()
            file_map = combo_box.property("file_map")
            base_name = self.extract_base_and_version(ref_name)
            for ref_model in self.dict_references[base_name[0]]:
                if ref_model in self.func_instance.get_all_referenced_files():
                    selected_files[ref_model] = file_map.get(selected_version, None)
        return selected_files

    def update_settings(self):
        self.io_manager.settings['directory'] = self.all_dir_field.text()
        self.io_manager.settings["files_to_update"] = self.get_selected_models()
        self.io_manager.save_settings()
        self.ui_manager.setting_updated.emit()
        self.adjust_window_height()

    def adjust_window_height(self):
        """Adjusts the window height based on the number of references."""
        base_height = 180  # Base height for the window
        additional_height_per_ref = 20  # Additional height per reference
        num_references = len(self.dict_references)
        total_height = base_height + (num_references * additional_height_per_ref)
        self.tab_widget.setFixedHeight(total_height)

class RefupFunc:
    def __init__(self, io_manager):
        self.io_manager = io_manager

    def get_all_referenced_files(self):
        """Retrieves all valid references in the Maya scene."""
        referenced_nodes = cmds.file(query=True, reference=True) or []
        valid_references = []

        for ref_node in referenced_nodes:
            try:
                # Get the reference file path without copy number
                ref_path = cmds.referenceQuery(ref_node,
                                               filename=True,
                                               withoutCopyNumber=True)
                valid_references.append(ref_path)
            except RuntimeError:
                # Skip invalid/unloaded references
                print(f"Warning: Skipping invalid reference node {ref_node}")

        return valid_references

    def build_list(self):
        all_ref_files = self.get_all_referenced_files()
        dic_all_ref_files = {}
        for ref in all_ref_files:
            dic_all_ref_files[os.path.basename(self.extract_base_name(ref))] = set()
        for file in all_ref_files:
            dic_all_ref_files[os.path.basename(self.extract_base_name(file)).replace('\\', '/')] = file
        files_dict = {}
        for dirpath, _, filenames in os.walk(self.io_manager.settings['directory']):
            for file in filenames:
                base_name = self.extract_base_name(file)
                if base_name in dic_all_ref_files:
                    if base_name not in files_dict:
                        files_dict[base_name] = []
                    full_path = os.path.join(dirpath, file).replace('\\', '/')
                    files_dict[base_name].append(full_path)

        for ref, versions in files_dict.items():
            files_dict[ref] = sorted(versions, key=self.extract_version_number)
        return files_dict

    def extract_base_name(self, filename):
        """Extracts the base name from a filename, regardless of extension."""
        match = re.match(r"(.+_)(v\d+)\.(\w+)$", filename)
        return match.group(1) if match else filename

    def extract_version_number(self, filename):
        match = re.search(r'v(\d+)', filename)
        return int(match.group(1)) if match else 0

    def update_references(self, selected_files):
        """Handles updating references when button is clicked."""
        self.replace_references(selected_files)

    def get_asset_base(self, path):
        normalized = os.path.normpath(path)
        filename = os.path.basename(normalized)
        return re.sub(r'_v\d+\.ma$', '', filename)

    def replace_references(self, selected_files):
        ref_nodes = cmds.ls(type="reference")
        asset_to_new_path = {}
        for old_path, new_path in selected_files.items():
            old_norm = os.path.normpath(old_path)
            asset_base = self.get_asset_base(old_norm)
            asset_to_new_path[asset_base] = os.path.normpath(new_path)

        cmds.refresh(suspend=True)
        for ref_node in ref_nodes:
            try:
                current_ref = cmds.referenceQuery(ref_node, filename=True, withoutCopyNumber=True)
                current_asset = self.get_asset_base(current_ref)
                if current_asset in asset_to_new_path:
                    new_ref = asset_to_new_path[current_asset]
                    cmds.file(new_ref, loadReference=ref_node)
            except RuntimeError as e:
                print(f"Error updating reference: {e}")
        cmds.refresh(suspend=False)

def show_ui():
    """Creates and displays the UI."""
    global simple_window
    try:
        simple_window.close()
    except:
        pass
    simple_window = RefUpUI()
    simple_window.show()