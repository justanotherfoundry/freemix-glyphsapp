# MenuTitle: Round Kerning
# encoding: utf-8
from __future__ import division

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__ = """
Rounds the kerning values to a chosen number.

In addition, values smaller than MIN_VALUE are erased.
"""

import time
from GlyphsApp import Glyphs, MGOrderedDictionary


MIN_VALUE = 4
QUANTISATION = 1


font = Glyphs.font


def filterKern():
	kerning = font.kerning
	for master in font.masters:
		masterDict = kerning[master.id]
		newMasterDict = MGOrderedDictionary.new()
		firstKeys = masterDict.keys()
		for firstKey in firstKeys:
			rightDict = masterDict[firstKey]
			secondKeys = rightDict.keys()
			newRightDict = MGOrderedDictionary.new()
			for secondKey in secondKeys:
				value = rightDict[secondKey]
				value = round(value / QUANTISATION) * QUANTISATION
				if abs(value) >= MIN_VALUE:
					newRightDict[secondKey] = value
			if len(newRightDict) > 0:
				newMasterDict[firstKey] = newRightDict
		kerning[master.id] = newMasterDict
	font.kerning = kerning


start = time.time()

filterKern()

end = time.time()
print("time", end - start)
