# encoding: utf-8

from __future__ import division, print_function, unicode_literals

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
import math, statistics

TEXT_OFFSET = 15
TEXT_HUE = 0.0
DEVIATION_STRICTNESS = 2.2
DEVIATION_GREEN_MAX = 0.85
DEVIATION_GREEN_FACTOR = 16.0
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

def relPositionDeviation(node, pathIndex, relPosition, layer, otherLayers):
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
		return 0.0
	else:
		try:
			deviationRel = max(relPosition / medianRelPos, medianRelPos / relPosition, (1.0-relPosition) / (1.0-medianRelPos), (1.0-medianRelPos) / (1.0-relPosition))
			deviation = DEVIATION_STRICTNESS * (deviationRel - 1.0)
			return min(1.0, deviation)
		except ZeroDivisionError:
			return 1.0

class HandleRelations(ReporterPlugin):

	@objc.python_method
	def settings(self):
		self.menuName = "Handle Relations"

	def conditionsAreMetForDrawing(self):
		# copied from https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
		currentController = self.controller.view().window().windowController()
		if currentController:
			tool = currentController.toolDrawDelegate()
			textToolIsActive = tool.isKindOfClass_(NSClassFromString("GlyphsToolText"))
			handToolIsActive = tool.isKindOfClass_(NSClassFromString("GlyphsToolHand"))
			if not textToolIsActive and not handToolIsActive: 
				return True
		return False

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
	def drawRelativePosition(self, node, pathIndex, layer, otherLayers):
		relPosition = relativePosition(node.prevNode, node, node.nextNode)
		textColor = NSColor.blackColor()
		textSize = TEXT_SIZE_SMALL
		if otherLayers:
			deviation = relPositionDeviation(node, pathIndex, relPosition, layer, otherLayers)
			red = deviation
			green = DEVIATION_GREEN_MAX - deviation * DEVIATION_GREEN_FACTOR
			green = max(0.0, green)
			textColor = NSColor.colorWithRed_green_blue_alpha_(red, green, 0.0, 1.0)
			textSize += deviation * TEXT_SIZE_DEVIATION_FACTOR;
		self.drawTextNearNode(node.prevNode, node, node.nextNode, text = "{:.2f}".format(relPosition).lstrip('0'), fontColor = textColor, fontSize = textSize)

	@objc.python_method
	def foreground(self, layer):
		if not self.conditionsAreMetForDrawing():
			return
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
				self.drawRelativePosition(node, pathIndex, layer, otherLayers)
			pathIndex += 1

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
