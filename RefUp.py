"""RefUp helps you manage the version of your references in maya.

This tool allows you to choose a directory and automatically scan
for all available versions of the referenced assets in your Maya scene.
You can then view the different versions of each reference
and select which version to use for every reference in your scene.

Additionally, there is an auto-update feature that can be enabled for specific references,
ensuring they always use the latest available version whenever the scene is opened.
"""

__author__ = "Mats Valgaeren"
__contact__ = "contact@matsvalgaeren.com"
__date__ = "2025-05-07"
__license__ = "GPLv3"
__version__ = "0.1.1"

# Standard Library Imports
import json
import os
import re

# Maya-Specific Imports
from maya import cmds

# Import QApplication from PySide6
from PySide6 import QtWidgets
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication


class IOManager:
    """Class to handle importing and exporting of the RefUp settings.json.

    The json file consists of a list of all maya scenes that use this tool,
    in every lists is a directory with a directory where RefUp searches for reference files
    and a list of files to auto update on startup.
    """
    def __init__(self):
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
    """Class to execute the auto update of selected references on startup.

    This is only run from userSetup.py!
    """
    def __init__(self):
        self.io_manager = IOManager()
        self.func_instance = RefupFunc(self.io_manager)
        self.run_startup_tasks()

    def run_startup_tasks(self):
        files_to_update = self.get_new_references()
        if files_to_update:
            self.func_instance.replace_references(files_to_update)

    def get_new_references(self):
        new_files = {}
        ref_up_ui = RefUpUI()
        selected_files_to_update = ref_up_ui.selected_files_to_update()

        for ref_model in selected_files_to_update.keys():
            to_update = self.io_manager.settings['files_to_update']
            ref_model_base = ref_up_ui.extract_base_and_version(os.path.basename(ref_model))[0]
            if ref_model_base in to_update:
                new_files[ref_model] = selected_files_to_update[ref_model]
        return new_files


class UIManager(QObject):
    """Class to update UI when a signal is given."""
    setting_updated = Signal()

    def __init__(self):
        super().__init__()
        self._settings = {}

class RefUpUI(QtWidgets.QMainWindow):
    """Class to handle all UI elements for the RefUp tool."""
    def __init__(self, parent=None):
        super(RefUpUI, self).__init__(parent)
        self.setWindowTitle("RefUp")
        self.setMinimumWidth(220)

        # This gets the dpi of the screen, and then resizes ui correctly
        self.dpi_scale = self.get_dpi_scale()
        self.size_ui_elements = self.dpi_scale_value(24)

        self.all_dir_field = None
        self.combo_boxes = {}
        self.checkboxes = {}
        self.ref_to_update = {}

        self.ui_manager = UIManager()
        self.ui_manager.setting_updated.connect(self.build_ui)
        self.io_manager = IOManager()
        self.func_instance = RefupFunc(self.io_manager)

        self.build_ui()

    def build_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.tab_widget = QtWidgets.QTabWidget(central_widget)

        layout = QtWidgets.QVBoxLayout(central_widget)
        layout.addWidget(self.tab_widget)
        layout.addStretch()

        self.update_tab = QtWidgets.QWidget()
        self.settings_tab = QtWidgets.QWidget()

        self.tab_widget.addTab(self.update_tab, "Update")
        self.tab_widget.addTab(self.settings_tab, "Settings")

        self.setup_update_tab()
        self.setup_settings_tab()

        self.adjust_window_height()

    def setup_update_tab(self):
        self.update_layout = QtWidgets.QVBoxLayout(self.update_tab)
        self.dict_references = self.func_instance.build_list()

        self.add_error_label(self.io_manager.settings['directory'], self.update_layout)
        self.add_divider(self.update_layout)
        self.add_label("Referenced Files:", self.update_layout)
        self.add_combo_boxes(self.update_tab)
        self.add_divider(self.update_layout)
        self.update_button = self.add_button(
            "Update References",
            lambda: self.func_instance.replace_references(self.get_selected_files()),
            self.update_layout
        )

    def setup_settings_tab(self):
        self.settings_layout = QtWidgets.QVBoxLayout(self.settings_tab)
        self.dict_references = self.func_instance.build_list()

        self.all_dir_field = self.add_file_field("Directory: ", self.settings_layout)
        self.add_divider(self.settings_layout)
        self.add_label("Files to Auto-Update:", self.settings_layout)
        self.add_checkboxes(self.settings_tab)
        self.add_divider(self.settings_layout)
        self.save_button = self.add_button("Update Settings", self.update_settings, self.settings_layout)

    def add_error_label(self, field, layout):
        if field:
            label_text = "Settings are up to date."
            update_label = self.add_label(label_text, layout)
            update_label.setStyleSheet("color: green")
        else:
            label_text = "You need to update your settings!"
            update_label = self.add_label(label_text, layout)
            update_label.setStyleSheet("color: red")
        update_label.setFixedHeight(self.size_ui_elements)

    def add_label(self, label, layout):
        local_layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(label)
        local_layout.addWidget(label)
        layout.addLayout(local_layout)
        return label

    def add_divider(self, layout):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        layout.addWidget(line)

    def add_combo_boxes(self, parent_layout):
        """Creates a dropdown for each referenced file and selects the latest one."""
        for ref_model, ref_list in self.dict_references.items():
            base_name, _ = self.extract_base_and_version(os.path.basename(ref_model))
            ref_label = QtWidgets.QLabel(base_name)
            ref_label.setFixedHeight(self.size_ui_elements)
            file_map = {}

            combo_box = QtWidgets.QComboBox()
            combo_box.setFixedWidth(80)

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

            parent_layout = parent_layout.layout()
            parent_layout.addLayout(layout)

    def add_button(self, label, callback, layout):
        button = QtWidgets.QPushButton(label)
        button.setFixedHeight(self.size_ui_elements)
        button.clicked.connect(callback)
        layout.addWidget(button)

    def add_file_field(self, label, layout):
        """Creates a label, file input field and a browse button."""
        layout_ref = QtWidgets.QHBoxLayout()
        lbl = QtWidgets.QLabel(label)

        layout_ref.addWidget(lbl)
        text_field = QtWidgets.QLineEdit()
        # this resizes the file field so it is the same same as a single label
        text_field.setFixedHeight(self.size_ui_elements*0.94)

        if self.io_manager.settings:
            directory = self.io_manager.settings.get('directory', "")
            text_field.setText(directory)

        browse_button = QtWidgets.QPushButton("Browse")
        browse_button.clicked.connect(lambda: self.select_directory(text_field))
        # making the button 10% smaller will make it align with the text field
        browse_button.setFixedHeight(self.size_ui_elements*0.9)

        layout_ref.addWidget(text_field)
        layout_ref.addWidget(browse_button)
        layout.addLayout(layout_ref)

        return text_field

    def add_checkboxes(self, parent_layout):
        seen = set()
        for ref_model in self.dict_references.keys():
            checkbox = QtWidgets.QCheckBox(os.path.basename(ref_model))
            checkbox.setFixedHeight(self.size_ui_elements)
            checkbox.setChecked(ref_model in self.io_manager.settings['files_to_update'])
            self.checkboxes[ref_model] = checkbox

            layout = QtWidgets.QHBoxLayout()
            layout.addStretch()
            layout.addWidget(checkbox)

            parent_layout = parent_layout.layout()
            parent_layout.addLayout(layout)

    def update_settings(self):
        self.io_manager.settings['directory'] = self.all_dir_field.text()
        self.io_manager.settings["files_to_update"] = self.get_selected_models()
        self.io_manager.save_settings()
        self.ui_manager.setting_updated.emit()
        self.adjust_window_height()

    def adjust_window_height(self):
        """Calculates the size of the total UI.

        It takes the size of always existing elements and references into account.
        """
        base_height = self.size_ui_elements*6
        num_references = len(self.dict_references)
        additional_height_per_ref = self.size_ui_elements*1.2

        total_height = base_height + (num_references * additional_height_per_ref)
        self.tab_widget.setFixedHeight(total_height)

    def select_directory(self, text_field):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            text_field.setText(directory)

    def get_dpi_scale(self):
        """This gets the dpi scale based on your monitor.

        This is used to resize the UI to keep all elements aligned.
        """
        app = QApplication.instance()
        dpi = app.primaryScreen().logicalDotsPerInch()
        default_dpi = 96
        multiplier = dpi / default_dpi # gets the dpi difference from the one I used to create the ui
        multiplier += multiplier * (1/multiplier * 0.1) # less size change
        return multiplier

    def dpi_scale_value(self, value):
        return value * self.dpi_scale

    def get_selected_files(self):
        """Gets the selected files from combo boxes."""
        selected_files = {}
        # Iterate over each reference and its associated combo box
        for ref_name, combo_box in self.combo_boxes.items():
            selected_version = combo_box.currentText()
            # Retrieve the file map (version label -> file path) stored as a property
            file_map = combo_box.property("file_map")
            base_name = self.extract_base_and_version(ref_name)
            for ref_model in self.dict_references[base_name[0]]:
                # Only update if this reference is currently loaded in the scene
                if ref_model in self.func_instance.get_all_referenced_files():
                    # Map the reference model to the selected file path (or None if not found)
                    selected_files[ref_model] = file_map.get(selected_version, None)
        return selected_files

    def get_selected_models(self):
        return [model for model, checkbox in self.checkboxes.items() if checkbox.isChecked()]

    def extract_base_and_version(self, filename):
        """Splits filename into base name and version, regardless of extension."""
        match = re.match(r"(.+_)(v\d+)\.(\w+)$", filename)
        if match:
            base, version, ext = match.groups()
            return base, version
        return filename, ""


class RefupFunc:
    """Class to handle RefUp functionality.

    - getting referenced files
    - building reference lists
    - replacing references
    """
    def __init__(self, io_manager):
        self.io_manager = io_manager

    def get_all_referenced_files(self):
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
        """Build a dictionary mapping each referenced asset base name to all available version file paths."""
        # Get all referenced files in the current Maya scene
        all_ref_files = self.get_all_referenced_files()
        dic_all_ref_files = {}

        # Initialize dictionary with asset base names as keys
        for ref in all_ref_files:
            dic_all_ref_files[os.path.basename(self.extract_base_name(ref))] = set()

        # Map asset base names to their full reference file paths
        for file in all_ref_files:
            dic_all_ref_files[os.path.basename(self.extract_base_name(file)).replace('\\', '/')] = file

        files_dict = {}
        # Walk through the target directory to find all files
        for dirpath, _, filenames in os.walk(self.io_manager.settings['directory']):
            for file in filenames:
                base_name = self.extract_base_name(file)
                # If the file matches a referenced asset, add its full path to the list
                if base_name in dic_all_ref_files:
                    if base_name not in files_dict:
                        files_dict[base_name] = []

                    full_path = os.path.join(dirpath, file).replace('\\', '/')
                    files_dict[base_name].append(full_path)

        # Sort version file paths for each asset by version number
        for ref, versions in files_dict.items():
            files_dict[ref] = sorted(versions, key=self.extract_version_number)
        return files_dict

    def replace_references(self, selected_files):
        """ Replace referenced assets in the Maya scene with new versions."""
        # Get all reference nodes in the scene
        ref_nodes = cmds.ls(type="reference")
        asset_to_new_path = {}

        # Build a mapping from asset base name to new file path
        for old_path, new_path in selected_files.items():
            old_norm = os.path.normpath(old_path)
            asset_base = self.get_asset_base(old_norm)
            asset_to_new_path[asset_base] = os.path.normpath(new_path)

        # Suspend viewport refresh for performance during batch update
        cmds.refresh(suspend=True)
        for ref_node in ref_nodes:
            try:
                # Get the current file path of the reference node
                current_ref = cmds.referenceQuery(ref_node, filename=True, withoutCopyNumber=True)
                current_asset = self.get_asset_base(current_ref)

                # If a new version is selected for this asset, update the reference
                if current_asset in asset_to_new_path:
                    new_ref = asset_to_new_path[current_asset]
                    cmds.file(new_ref, loadReference=ref_node)
            except RuntimeError as e:
                print(f"Error updating reference: {e}")
        # Resume viewport refresh
        cmds.refresh(suspend=False)

    def split_filename(self, filename):
        """Return base name and version (e.g., 'model_', 'v003') from 'model_v003.ma'."""
        match = re.match(r"(.+_)(v\d+)\.(\w+)$", filename)
        if match:
            return match.group(1), match.group(2)
        return filename, ""

    def extract_base_name(self, filename):
        return self.split_filename(filename)[0]

    def extract_version_number(self, filename):
        match = re.search(r'v(\d+)', filename)
        return int(match.group(1)) if match else 0

    def get_asset_base(self, path):
        filename = os.path.basename(os.path.normpath(path))
        base, _ = self.split_filename(filename)
        return base.rstrip('_')

def show_ui():
    global simple_window
    try:
        simple_window.close()
    except:
        pass
    simple_window = RefUpUI()
    simple_window.show()
