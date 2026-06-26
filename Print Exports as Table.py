#MenuTitle: Print Exports as Table

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
Prints details of the exports as a table. Respects the selection of exports if the Exports tab is active. Make sure the Macro Panel is open.
'''

from AppKit import NSApp, NSTableView
from GlyphsApp import Glyphs
import hashlib
Glyphs.clearLog()

MAX_CP_STRING_LENGTH = 48

def sortedByIndices(listOfLists, onlyNonIdentical=False):
	indices = []
	for n in range(0, len(listOfLists[0])):
		if onlyNonIdentical and all(listOfLists[i][n] == listOfLists[i + 1][n] for i in range(len(listOfLists) - 1)):
			continue
		if all(listOfLists[i][n] <= listOfLists[i + 1][n] for i in range(len(listOfLists) - 1)):
			indices.append(n)
		elif all(listOfLists[i][n] >= listOfLists[i + 1][n] for i in range(len(listOfLists) - 1)):
			indices.append(n)
	return indices

def shortenCP(text):
	text = ''.join(str(text).split())
	contractions = (
		('ScaletoUPM', 'UPM'),
		('PreFilter', 'PreF'),
		('Filter', 'F'),
		('Rename', 'Rnm'),
		('Remove', 'Rmv'),
		('Glyphs', 'G'),
		('Features', 'Ft'),
		('Feature', 'Ft'),
		('RMX', ''),
		('Transformations','Transf')
	)
	for full, contracted in contractions:
		text = text.replace(full, contracted)
	return text

def truncate(text, max_length, ellipsis='…'):
	if len(text) <= max_length:
		return text
	return text[:max_length - len(ellipsis)] + ellipsis

def cpStrings(cp):
	cpStringFull = '•' if cp.active else ' '
	cpString = cpStringFull
	cpStringFull += cp.name
	cpString += truncate(shortenCP(cp.name), 8, ellipsis='') + ' '
	valueString = ''.join(str(cp.value).split())
	cpStringFull += valueString
	cpString += truncate(shortenCP(valueString), 10)
	return cpStringFull, cpString

axis_names = [axis.axisTag for axis in  Glyphs.font.axes]
axis_names += ['wt_c', 'wd_c', 'RIBBI', 'CP']
longest_axis_name = max(axis_names, key = len)
axis_column_width = max(6, len(longest_axis_name) + 1)

# determine selected exports:
view = NSApp.keyWindow().firstResponder()
while view is not None and not isinstance(view, NSTableView):
	try:
		view = view.superview()
	except AttributeError:
		view = None
selectedInstances = None
if view is not None:
	selectedInstances = [Glyphs.font.instances[index] for index in view.selectedRowIndexes()]
if not selectedInstances:
	selectedInstances = Glyphs.font.instances

instance_names = [instance.fullName for instance in selectedInstances]
longest_instance_name = max(instance_names, key = len)
first_column_width = len(longest_instance_name) + 1

headerLine = ' ' + ''.ljust(first_column_width) + ''.join([ n.rjust(axis_column_width) for n in axis_names])

# determine shared CPs:
allCPs = [[cpStrings(cp)[0] for cp in instance.customParameters] for instance in selectedInstances]
sharedCPs = set.intersection(*(set(items) for items in allCPs))

# set up instances:
displayInstances = []
for instance in selectedInstances:
	displayName = (' ' if instance.active else '*') + instance.fullName.ljust(first_column_width)
	displayInstance = [(0, displayName)]
	if not instance.axes:
		# VF instance
		c = float('inf')
		displayInstance.extend([(c, f'{c:{axis_column_width}.0f}')] * len(Glyphs.font.axes))
	else:
		for c in instance.axes:
			if c.is_integer():
				displayInstance.append((c, f'{c:{axis_column_width}.0f}'))
			else:
				displayInstance.append((c, f'{c:{axis_column_width}.2f}'))
	displayInstance.append((instance.weightClass, f'{instance.weightClass:{axis_column_width}}'))
	displayInstance.append((instance.widthClass, f'{instance.widthClass:{axis_column_width}}'))
	ribbiStr = ('B' if instance.isBold else '') + ('I' if instance.isItalic else '') or ''
	ribbiInt = 2 * instance.isBold + instance.isItalic
	displayInstance.append((ribbiInt, ribbiStr.rjust(axis_column_width)))
	allCPstrings = [cpStrings(cp) for cp in instance.customParameters if not cpStrings(cp)[0] in sharedCPs]
	cpStringFull = ''.join([s[0] for s in allCPstrings])
	cpString = ' '.join([s[1] for s in allCPstrings])
	cpString = '    ' + hashlib.md5(cpString.encode('utf-8')).hexdigest()[:5] + ' ' + cpString
	displayInstance.append((cpStringFull, truncate(cpString, MAX_CP_STRING_LENGTH)))
	displayInstances.append(displayInstance)
alreadySorted = sortedByIndices(displayInstances)

# print in default order:
print(', '.join(['sorted by default'] + [axis_names[i-1] for i in sortedByIndices(displayInstances, onlyNonIdentical=True)]))
print(headerLine)
print( '\n'.join(''.join(v[1] for v in displayInstance) for displayInstance in displayInstances))

# print sorted by column:
for i in range(1, len(axis_names)+1):
	if i in alreadySorted:
		continue
	displayInstancesSorted = sorted(displayInstances, key=lambda item: item[i])
	newSortedByIndices = [s for s in sortedByIndices(displayInstancesSorted, onlyNonIdentical=True) if not s in alreadySorted]
	print('\n\nsorted by', ', '.join([axis_names[i-1] for i in newSortedByIndices]))
	print(headerLine)
	print( '\n'.join(''.join(v[1] for v in displayInstance) for displayInstance in displayInstancesSorted))
	alreadySorted += sortedByIndices(displayInstancesSorted)
