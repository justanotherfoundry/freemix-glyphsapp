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
OTHER_DIRECTION_PARALLELITY_TOLERANCE = 0.5
OTHER_DIRECTION_PARALLELITY_TOLERANCE_FACTOR = 1.0 / 64
OTHER_DIRECTION_DISPLAY_LENGTH = 0.75
SHALLOW_CURVE_THRESHOLD = 0.4
# ^ in radians

def samePosition(node1, node2):
	return node1.position.x == node2.position.x and node1.position.y == node2.position.y

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

def relPositionDeviation(prevNode, node, nextNode, pathIndex, relPosition, layer, otherLayers):
	relPositions = [relPosition]
	for otherLayer in otherLayers:
		try:
			otherPath = otherLayer.paths[pathIndex]
			otherNode = otherPath.nodes[node.index]
			otherPrevNode = otherPath.nodes[prevNode.index]
			otherNextNode = otherPath.nodes[nextNode.index]
		except IndexError:
			continue
		otherRelPosition = relativePosition(otherPrevNode, otherNode, otherNextNode)
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
	def drawRelativePosition(self, prevNode, node, nextNode, pathIndex, layer, otherLayers):
		relPosition = relativePosition(prevNode, node, nextNode)
		textColor = NSColor.blackColor()
		textSize = TEXT_SIZE_SMALL
		if otherLayers:
			deviation = relPositionDeviation(prevNode, node, nextNode, pathIndex, relPosition, layer, otherLayers)
			red = deviation
			green = DEVIATION_GREEN_MAX - deviation * DEVIATION_GREEN_FACTOR
			green = max(0.0, green)
			textColor = NSColor.colorWithRed_green_blue_alpha_(red, green, 0.0, 1.0)
			textSize += deviation * TEXT_SIZE_DEVIATION_FACTOR;
		self.drawTextNearNode(prevNode, node, nextNode, text = "{:.2f}".format(relPosition).lstrip('0'), fontColor = textColor, fontSize = textSize)

	@objc.python_method
	def drawLineFromNodeToPoint(self, node, line):
		myPath = NSBezierPath.alloc().init()
		myPath.moveToPoint_((node.position.x, node.position.y))
		myPath.relativeLineToPoint_(line)
		myPath.setLineWidth_(0.375 * self.getScale()**-0.9)
		myPath.stroke()

	@objc.python_method
	def lineWithDirection(self, node, handleLengthSq, otherNode, otherBCP):
		dx, dy = pointDiff(otherBCP, otherNode)
		otherHandleLengthSq = dx * dx + dy * dy
		if (otherHandleLengthSq == 0):
			return
		handleFactor = math.sqrt(handleLengthSq / otherHandleLengthSq)
		dx *= handleFactor
		dy *= handleFactor
		return dx, dy

	# returns True if the node is to be ignored
	@objc.python_method
	def drawOtherDirections(self, node, pathIndex, layer, otherLayers):
		NSColor.colorWithRed_green_blue_alpha_(0.0, 0.3, 1.0, 1.0).set() 
		inHandleX, inHandleY = pointDiff(node.prevNode, node)
		outHandleX, outHandleY = pointDiff(node.nextNode, node)
		inHandleLengthSq = inHandleX**2 + inHandleY**2
		outHandleLengthSq = outHandleX**2 + outHandleY**2
		inHandleParallelityToleranceSq = (OTHER_DIRECTION_PARALLELITY_TOLERANCE + math.sqrt(inHandleLengthSq) * OTHER_DIRECTION_PARALLELITY_TOLERANCE_FACTOR)**2
		outHandleParallelityToleranceSq = (OTHER_DIRECTION_PARALLELITY_TOLERANCE + math.sqrt(outHandleLengthSq) * OTHER_DIRECTION_PARALLELITY_TOLERANCE_FACTOR)**2
		endpoints = []
		allParallel = True
		for otherLayer in otherLayers:
			try:
				otherPath = otherLayer.paths[pathIndex]
				otherNode = otherPath.nodes[node.index]
			except IndexError:
				continue
			# inhandle
			lineX, lineY = self.lineWithDirection(node, inHandleLengthSq, otherNode, otherNode.prevNode)
			endpoints.append((lineX * OTHER_DIRECTION_DISPLAY_LENGTH, lineY * OTHER_DIRECTION_DISPLAY_LENGTH))
			deviationSq = (inHandleX - lineX)**2 + (inHandleY - lineY)**2
			if deviationSq > inHandleParallelityToleranceSq:
				allParallel = False
			# outhandle
			lineX, lineY = self.lineWithDirection(node, outHandleLengthSq, otherNode, otherNode.nextNode)
			endpoints.append((lineX * OTHER_DIRECTION_DISPLAY_LENGTH, lineY * OTHER_DIRECTION_DISPLAY_LENGTH))
			deviationSq = (outHandleX - lineX)**2 + (outHandleY - lineY)**2
			if deviationSq > outHandleParallelityToleranceSq:
				allParallel = False
		if allParallel and not node.selected and not node.prevNode.selected and not node.nextNode.selected:
			return True
		# draw the directions (but only for curve-curve connections):
		if node.prevNode.type == OFFCURVE and node.nextNode.type == OFFCURVE:
			for endpoint in endpoints:
				self.drawLineFromNodeToPoint(node, endpoint)

	@objc.python_method
	def foreground(self, layer):
		if not self.conditionsAreMetForDrawing():
			return
		otherLayers = [otherLayer for otherLayer in layer.parent.layers if not otherLayer is layer and otherLayer.isMasterLayer]
		pathIndex = 0
		for path in layer.paths:
			# smooth nodes:
			for node in path.nodes:
				if not node.smooth:
					continue
				if node.prevNode.type != OFFCURVE and node.nextNode.type != OFFCURVE:
					continue
				if layer.selection and not node.selected and (node.prevNode.type != OFFCURVE or not node.prevNode.selected) and (node.nextNode.type != OFFCURVE or not node.nextNode.selected):
					continue
				if isHoriVerti(node.prevNode, node.nextNode):
					continue
				ignoreNode = self.drawOtherDirections(node, pathIndex, layer, otherLayers)
				if ignoreNode:
					continue
				self.drawRelativePosition(node.prevNode, node, node.nextNode, pathIndex, layer, otherLayers)
			# shallow curves:
			for bcp1 in path.nodes:
				bcp2 = bcp1.nextNode
				if bcp1.type != OFFCURVE or bcp2.type != OFFCURVE:
					continue
				node1 = bcp1.prevNode
				node2 = bcp2.nextNode
				if layer.selection and not bcp1.selected and not bcp2.selected and not node1.selected and not node2.selected:
					continue
				angle1 = angle(node1, bcp1, node2)
				angle2 = angle(node1, bcp2, node2)
				threshold1 = SHALLOW_CURVE_THRESHOLD
				threshold2 = SHALLOW_CURVE_THRESHOLD
				if angle1 * angle2 < 0:
					# the curve has an s-shape so the BCPs are less likely to have redundancy
					threshold1 *= 0.5
					threshold2 *= 0.5
					if isHoriVerti(node1, bcp1):
						threshold1 = 0
					if isHoriVerti(node2, bcp2):
						threshold2 = 0
				if node1.smooth:
					# bcp1 is likely to be restricted
					threshold1 *= 0.5
					if isHoriVerti(node1, bcp1):
						threshold1 *= 0.25
				if node2.smooth:
					# bcp2 is likely to be restricted
					threshold2 *= 0.5
					if isHoriVerti(node2, bcp2):
						threshold2 *= 0.25
				if bcp1.selected:
					threshold1 += 1.0
					# this almost guarantees that the relation is displayed
				if bcp2.selected:
					threshold2 += 1.0
				if abs(angle1) > math.pi - threshold1 and not samePosition(bcp1, node1):
					self.drawRelativePosition(node1, bcp1, node2, pathIndex, layer, otherLayers)
				if abs(angle2) > math.pi - threshold2 and not samePosition(bcp2, node2) and not samePosition(bcp1, bcp2):
					self.drawRelativePosition(node2, bcp2, node1, pathIndex, layer, otherLayers)
			pathIndex += 1

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
