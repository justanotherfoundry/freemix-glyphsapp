#MenuTitle: Make Quadratic Curve

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
Converts cubic curves to quadratic curves (if a BCP is selected).

This does not try to retain the shape, it does not add or remove nodes, it simply re-defines the cuve type.
'''

def samePosition(node1, node2):
	return node1.position.x == node2.position.x and node1.position.y == node2.position.y

for selectedLayer in Glyphs.currentDocument.selectedLayers():
	glyph = selectedLayer.parent
	glyph.beginUndo()
	for layer in glyph.layers:
		for path in layer.paths:
			for node in path.nodes:
				if not node.selected:
					continue
				if node.type != OFFCURVE:
					continue
				if node.nextNode.type == CURVE:
					# node is the second cubic BCP
					node.nextNode.type = QCURVE
				elif node.nextNode.nextNode.type == CURVE:
					# node is the first cubic BCP
					node.nextNode.nextNode.type = QCURVE
	glyph.endUndo()
