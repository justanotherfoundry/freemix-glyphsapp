#MenuTitle: Make Cubic Curve

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
Same as Path > Other > Convert to cubic
but it can be applied to individual curve segments
(i.e. respects the selection).

Careful: This script is always applied to all all layers.
'''

def samePosition(node1, node2):
	return node1.position.x == node2.position.x and node1.position.y == node2.position.y

for selectedLayer in Glyphs.currentDocument.selectedLayers():
	glyph = selectedLayer.parent
	glyph.beginUndo()
	for layer in glyph.layers:
		layer.saveHints()
		for path in layer.paths:
			for i in range(len(path.nodes)):
				node = path.nodes[i]
				if not node.selected:
					continue
				if node.type != OFFCURVE:
					continue
				if node.nextNode.type == QCURVE:
					# node is a quad BCP
					bcp1pos = node.position
					bcp2pos = node.position
					bcp1pos.x += (node.nextNode.position.x - bcp1pos.x) / 3
					bcp1pos.y += (node.nextNode.position.y - bcp1pos.y) / 3
					bcp2pos.x += (node.prevNode.position.x - bcp2pos.x) / 3
					bcp2pos.y += (node.prevNode.position.y - bcp2pos.y) / 3
					newNode = node.copy()
					node.position = bcp1pos
					newNode.position = bcp2pos
					path.nodes.insert(i, newNode)
					node.nextNode.type = CURVE
					break
		layer.restoreHints()
	glyph.endUndo()
