.. _example:


*******
Example
*******

A more detailed example can be find in the example folder. Here is a basic one::

  import casefoam

  # directory of the base case
  baseCase = 'forwardStep'

  # list of parent, child and grandchild names
  caseStructure = [['Ux1', 'Ux2', 'Ux3'],
                   ['T1', 'T2']]

  # dictionarys with data for the caseData dictionary
  update_Ux1 = {
      '0/U': {'boundaryField': {'inlet': {'value': 'uniform (1 0 0)'}}}}

  update_Ux2 = {
      '0/U': {'boundaryField': {'inlet': {'value': 'uniform (2 0 0)'}}}}

  update_Ux3 = {
      '0/U': {'boundaryField': {'inlet': {'value': 'uniform (3 0 0)'}}}}

  update_T1 = {
      '0/T': {'boundaryField': {'inlet': {'value': 'uniform 1'}}}}

  update_T2 = {
      '0/T': {'boundaryField': {'inlet': {'value': 'uniform 2'}}}}

  # dictionary of data to update
  caseData = {'Ux1': update_Ux1,
              'Ux2': update_Ux2,
              'Ux3': update_Ux3,
              'T1': update_T1,
              'T2': update_T2}

  # generate cases
  casefoam.mkCases(baseCase, caseStructure, caseData, hierarchy='tree')
