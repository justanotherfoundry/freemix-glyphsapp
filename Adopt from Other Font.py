#MenuTitle: Adopt from Other Font
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__='''
Adopts glyph properties from the same-named glyph in a different font.
'''

import vanilla

try:
	props
	otherFontName
except NameError:
	props = {'LSB': 0, 'RSB': 0, 'Width': 0, 'Metrics Keys': 0, 'Glyph Color': 0, 'Add Anchors': 0, 'Replace Components': 0, '... in all masters': 0}
	otherFontName = ''

class AdoptDialog(object):

	def __init__(self):
		global otherFontName
		global props
		windowWidth = 300
		windowHeight = 284
		lineHeight = 22
		posX = 14
		posY = 15
		elementHeight = 20
		rightMargin = -10
		try:
			self.layer = doc.selectedLayers()[0]
		except TypeError:
			self.layer = None
			return
		self.w = vanilla.FloatingWindow((windowWidth, windowHeight), 'Adopt from Other Font', autosaveName='com.freemix.adopt_from.mainwindow')
		openedFonts = [font.filepath.split('/')[-1] for font in Glyphs.fonts if not font is Glyphs.font]
		if not openedFonts:
			self.w.descriptionText = vanilla.TextBox((posX, posY, rightMargin, 14), 'Please open another font.', selectable=True)
			return
		self.w.popUpButton = vanilla.PopUpButton((posX, posY, rightMargin, elementHeight), openedFonts, callback=self.popUpButtonCallback)
		if otherFontName in openedFonts:
			self.w.popUpButton.setItem(otherFontName)
		else:
			otherFontName = self.w.popUpButton.getItem()
		posY += 10
		for label, value in props.items():
			posY += lineHeight
			posXlocal = posX
			if label == '... in all masters':
				posY += lineHeight // 2
				posX += 20
			checkbox = vanilla.CheckBox((posX, posY, rightMargin, elementHeight), label, callback=self.checkBoxCallback, value=value)
			attrName = label.replace(' ', '_').replace('.', '') +'Checkbox' 
			setattr(self.w, attrName, checkbox)
		self.w.adoptButton = vanilla.Button((-100, -40, -10, -20), 'Adopt values', callback=self.buttonCallback)
		self.w.setDefaultButton(self.w.adoptButton)

	def popUpButtonCallback(self, sender):
		global otherFontName
		otherFontName = self.w.popUpButton.getItem()

	def checkBoxCallback(self, sender):
		global props
		props[sender.getTitle()] = sender.get()

	def buttonCallback(self, sender):
		global props
		global otherFontName
		for font in Glyphs.fonts:
			if font.filepath.split('/')[-1] == otherFontName:
				otherFont = font
				break
		else:
			return
		anySuccessful = False
		if props['... in all masters']:
			layers = []
			for layer in doc.selectedLayers():
				if not layer:
					continue
				glyph = layer.parent
				for master in glyph.parent.masters:
					layers.append(glyph.layers[master.id])
		else:
			layers = doc.selectedLayers()
		for layer in layers:
			glyph = layer.parent
			otherGlyph = otherFont.glyphs[glyph.name]
			if not otherGlyph:
				continue
			if len(otherFont.masters) == 1:
				otherLayer = otherGlyph.layers[0]
			else:
				for master in otherFont.masters:
					if master.name == layer.master.name:
						otherLayer = otherGlyph.layers[master.id]
						assert(otherLayer)
						break
				else:
					continue
			anySuccessful = True
			if props['LSB']:
				layer.LSB = otherLayer.LSB
			if props['RSB']:
				layer.RSB = otherLayer.RSB
			if props['Width']:
				layer.width = otherLayer.width
			if props['Metrics Keys']:
				glyph.leftMetricsKey = otherGlyph.leftMetricsKey
				glyph.rightMetricsKey = otherGlyph.rightMetricsKey
				glyph.widthMetricsKey = otherGlyph.widthMetricsKey
			if props['Glyph Color']:
				glyph.color = otherGlyph.color
			if props['Add Anchors']:
				for anchor in otherLayer.anchors:
					if not anchor.name in layer.anchors.keys():
						layer.anchors[anchor.name] = anchor
						print(otherLayer.parent.name, 'adding anchor', anchor.name)
			if props['Replace Components']:
				layer.shapes.clear()
				layer.shapes.extend(list(otherLayer.components))
# 				for component in otherLayer.components:
# 					layer.anchors[anchor.name] =anchor
		if not anySuccessful:
			return
		self.w.close()

dialog = AdoptDialog()
if dialog.layer is not None:
	dialog.w.open()
	dialog.w.makeKey()
