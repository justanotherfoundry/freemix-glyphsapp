#MenuTitle: Sort by Vertical Center

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
Outputs the selected glyphs (from Font or Edit view) in a new tab, sorted by vertical center.
'''

import GlyphsApp

font = Glyphs.font

# returns a list of GSLayer objects for the current selection
def get_selected_layers(f):
	if f.currentTab:
		# Edit View: selected layers
		return [l for l in f.currentTab.selectedLayers if not isinstance(l, GSControlLayer)]
	elif f.selection:
		# Font View: selected glyphs
		layers = []
		master_id = f.selectedFontMaster.id
		return [g.layers[master_id] for g in f.selection]
	return []

# computes bounding box center Y
def center_y(layer):
	bbox = layer.bounds
	if bbox.size.height == 0:
		return 0
	return bbox.origin.y + bbox.size.height / 2.0

# sort layers by their center y
layers_without_duplicates = list(dict.fromkeys(get_selected_layers(font)))
sorted_layers = sorted(layers_without_duplicates, key=center_y)

tab_text = ""
current_center = None

for layer in sorted_layers:
	cy = center_y(layer)
	if current_center is None:
		current_center = cy
	elif abs(cy - current_center) > 0.6:
		tab_text += "\n"
		current_center = cy
	tab_text += "/" + layer.parent.name

# Open in new tab
font.newTab(tab_text)
