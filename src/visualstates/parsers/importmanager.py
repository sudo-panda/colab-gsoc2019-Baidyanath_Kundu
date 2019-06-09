'''
   Copyright (C) 1997-2018 JDERobot Developers Team

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU Library General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, see <http://www.gnu.org/licenses/>.

   Authors : Pushkal Katara (katarapushkal@gmail.com)

  '''

from visualstates.configs.rosconfig import RosConfig
from visualstates.gui.dialogs.dupparamsdialog import DuplicateParamsDialog
from visualstates.gui.dialogs.paramsdialog import ParamsDialog

class ImportManager():
    """
    Functionality:
    Import PreBuild State into Current State
    Verify Configurations
    Verify Libraries
    Verify Functions
    Verify Variables

    :param rootState: Root Imported State
    :param config: Configurations of Imported State
    :param libraries: Libraries of Imported State
    :param functions: Functions of Imported State
    :param variables: Variables of Imported State

    Returns list of States which needs to be Imported
    """

    def updateAuxiliaryData(self, file, klass):
        """Wrapper upon all update functions"""
        params, importedState, globalNamespace = self.updateParams(file[0], file[1], file[4], klass.params)
        importedState = self.updateActiveState(importedState, klass.automataScene.stateIndex, klass.automataScene.transitionIndex, klass.activeState)
        config = self.updateConfigs(file[2], klass.config)
        libraries = self.updateLibraries(file[3], klass.libraries)
        globalNamespace = self.updateNamespace(globalNamespace, klass.globalNamespace)
        return params, importedState, config, libraries, globalNamespace

    def updateNamespace(self, newNamespace, namespace):
        newFunctions = newNamespace.getFunctions()
        newVariables = newNamespace.getVariables()
        if newFunctions and newVariables:
            namespace.addFunctions(newFunctions)
            namespace.addVariables(newVariables)
        return namespace

    def updateLibraries(self, newLibraries, libraries):
        """Updates existing libraries with imported libraries"""
        for lib in newLibraries:
            if lib not in libraries:
                libraries.append(lib)
        return libraries

    def updateConfigs(self, newConfig, config):
        """Updates Existing Configurations with imported Configurations"""
        if newConfig:
            if config is None:
                config = RosConfig()
            config.updateROSConfig(newConfig)
        return config

    def updateActiveState(self, importState, stateID, transitionID, activeState):
        """Updates Parent State with States to be imported"""
        importState = self.updateIDs(importState, stateID, transitionID)
        for state in importState.getChildren():
            activeState.addChild(state)
            state.setParent(activeState)
        updatedParentNamespace = self.updateNamespace(importState.getNamespace(), activeState.namespace)
        activeState.setNamespace(updatedParentNamespace)
        return importState

    def updateIDs(self, importState, stateID, transitionID):
        """ Wrapper upon UpdateStateIDs """
        self.updateStateIDs(importState, stateID)
        self.updateTranIDs(importState, transitionID)
        return importState

    def updateStateIDs(self, importState, stateID):
        """ Assign New IDs to Imported State Data Recursively """
        for child in importState.getChildren():
            child.setID(stateID + child.getID())
            self.updateStateIDs(child, stateID)

    def updateTranIDs(self, importState, transitionID):
        for child in importState.getChildrenTransitions():
            child.setID(transitionID + child.getID())

    def updateParams(self, newParams, importedState, globalNamespace, origParams):
        for newParam in newParams:
            newName = ''
            duplicate = False
            for origParam in origParams:
                if origParam.name == newParam.name :
                    dialog = DuplicateParamsDialog('Resolve Duplicate Parameter', newParam, origParam, newParams, origParams)
                    dialog.exec_()
                    newName = dialog.getName()
                    duplicate = True
            if duplicate:
                if newName != newParam.name :
                    importedState, globalNamespace = self.replaceParamName(newParam.name, newName, importedState, globalNamespace)
                    newParam.name = newName
                    origParams.append(newParam)
            else:
                origParams.append(newParam)
        dialog = ParamsDialog('Imported Parameters', newParams, False)
        dialog.exec_()

        return origParams, importedState, globalNamespace

    def replaceParamName(self, oldName, newName, importedState, globalNamespace):
        findText = '${'+oldName+'}'
        replaceText = '${'+newName+'}'
        self.replaceStateParams(findText, replaceText, importedState)
        (globalNamespace).setFunctions(((globalNamespace).getFunctions()).replace(findText, replaceText))
        (globalNamespace).setVariables(((globalNamespace).getVariables()).replace(findText, replaceText))

        return importedState, globalNamespace

    def replaceStateParams(self, findText, replaceText, state):
        (state.getNamespace()).setFunctions(((state.getNamespace()).getFunctions()).replace(findText, replaceText))
        (state.getNamespace()).setVariables(((state.getNamespace()).getVariables()).replace(findText, replaceText))
        for trans in state.getChildrenTransitions():
            trans.setCode(trans.getCode().replace(findText, replaceText))
            trans.setCondition(trans.getCondition().replace(findText, replaceText))
        for child in state.getChildren():
            child.setCode(child.getCode().replace(findText, replaceText))
            self.replaceStateParams(findText, replaceText, child)