# encoding: utf-8

from __future__ import division, print_function, unicode_literals

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
import math, statistics

TEXT_OFFSET = 15
TEXT_HUE = 0.0
DEVIATION_STRICTNESS = 2.2
DEVIATION_ALPHA_FACTOR = 25.0
DEVIATION_ALPHA_MIN = 0.05
HORIZONTAL_OFFSET_FACTOR = 0.4
TEXT_SIZE_SMALL = 10.0
TEXT_SIZE_DEVIATION_FACTOR = 8.0

def isHoriVerti(node1, node2):
	return node1.position.x == node2.position.x or node1.position.y == node2.position.y

def pointDiff(node1, node2):
	return node1.position.x - node2.position.x, node1.position.y - node2.position.y

def vectorLength(dx, dy):
	return math.sqrt(dx * dx + dy * dy)

def dist(node1, node2):
	dx, dy = pointDiff(node1, node2)
	return vectorLength(dx, dy)

def relativePosition(node1, node2, node3):
	outerLength = dist(node3, node1)
	firstLength = dist(node2, node1)
	return firstLength / outerLength

class HandleRelations(ReporterPlugin):

	@objc.python_method
	def settings(self):
		self.menuName = "Handle Relations"

	@objc.python_method
	def drawTextNearNode(self, prevNode, node, nextNode, text, fontColor, fontSize):
		textAlignment = 'center'
		offsetLength = TEXT_OFFSET * self.getScale()**-0.9
		bothHandlesX, bothHandlesY = pointDiff(node.prevNode, node.nextNode)
		if bothHandlesY < - abs(bothHandlesX):
			textAlignment = 'left'
			offsetLength *= HORIZONTAL_OFFSET_FACTOR
		elif bothHandlesY > abs(bothHandlesX):
			textAlignment = 'right'
			offsetLength *= HORIZONTAL_OFFSET_FACTOR
		bothHandlesLength = vectorLength(bothHandlesX, bothHandlesY)
		offsetX = - bothHandlesY / bothHandlesLength * offsetLength
		offsetY = bothHandlesX / bothHandlesLength * offsetLength
		self.drawTextAtPoint(text, NSPoint(node.position.x + offsetX, node.position.y + offsetY), align = textAlignment, fontColor = fontColor, fontSize = fontSize)

	@objc.python_method
	def foreground(self, layer):
		otherLayers = [otherLayer for otherLayer in layer.parent.layers if not otherLayer is layer and otherLayer.isMasterLayer]
		pathIndex = 0
		for path in layer.paths:
			for node in path.nodes:
				if not node.smooth:
					continue
				if node.prevNode.type != OFFCURVE and node.nextNode.type != OFFCURVE:
					continue
				if layer.selection and not node.selected and not node.prevNode.selected and not node.nextNode.selected:
					continue
				if isHoriVerti(node.prevNode, node.nextNode):
					continue
				relPosition = relativePosition(node.prevNode, node, node.nextNode)
				textColor = NSColor.blackColor()
				textSize = TEXT_SIZE_SMALL
				if otherLayers:
					relPositions = [relPosition]
					for otherLayer in otherLayers:
						try:
							otherPath = otherLayer.paths[pathIndex]
							otherNode = otherPath.nodes[node.index]
						except IndexError:
							continue
						otherRelPosition = relativePosition(otherNode.prevNode, otherNode, otherNode.nextNode)
						relPositions.append(otherRelPosition)
					medianRelPos = statistics.median(relPositions)
					if medianRelPos == relPosition:
						deviation = 0.0
					else:
						try:
							deviationRel = max(relPosition / medianRelPos, medianRelPos / relPosition, (1.0-relPosition) / (1.0-medianRelPos), (1.0-medianRelPos) / (1.0-relPosition))
							deviation = DEVIATION_STRICTNESS * (deviationRel - 1.0)
							deviation = min(1.0, deviation)
						except ZeroDivisionError:
							deviation = 1.0
					alpha = DEVIATION_ALPHA_MIN + deviation * DEVIATION_ALPHA_FACTOR
					alpha = min(1.0, alpha)
					textColor = NSColor.colorWithCalibratedHue_saturation_brightness_alpha_(TEXT_HUE, 1.0, deviation, alpha)
					textSize += deviation * TEXT_SIZE_DEVIATION_FACTOR;
				self.drawTextNearNode(node.prevNode, node, node.nextNode, text = "{:.2f}".format(relPosition).lstrip('0'), fontColor = textColor, fontSize = textSize)
			pathIndex += 1

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
