print('userSetup is getting executed')

import maya.cmds as cmds
import RefUp
import importlib

importlib.reload(RefUp)
def run_on_file_open():
    RefUp.StartupManager()

cmds.scriptJob(event=["SceneOpened", run_on_file_open], permanent=True)

print('userSetup executed')