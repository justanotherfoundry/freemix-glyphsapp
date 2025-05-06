from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import Glyphs, WINDOW_MENU, DOCUMENTACTIVATED, DOCUMENTWILLCLOSE, UPDATEINTERFACE, CORNER, CAP
from GlyphsApp.plugins import GeneralPlugin
import vanilla
from Cocoa import NSMenuItem, NSImageNameLockLockedTemplate, NSImageNameLockUnlockedTemplate
import traceback

NUMBER_OF_FIELDS = 12
MULTIPLE_VALUES = -1024

# from https://forum.glyphsapp.com/t/vanilla-make-edittext-arrow-savvy/5894/2
GSSteppingTextField = objc.lookUpClass("GSSteppingTextField")


class ArrowEditText(vanilla.EditText):
	nsTextFieldClass = GSSteppingTextField

	def _setCallback(self, callback):
		super(ArrowEditText, self)._setCallback(callback)
		if callback is not None and self._continuous:
			self._nsObject.setContinuous_(True)
			self._nsObject.setAction_(self._target.action_)
			self._nsObject.setTarget_(self._target)


class CapsAndCorners(GeneralPlugin):

	@objc.python_method
	def settings(self):
		self.name = 'Caps and Corners'

	@objc.python_method
	def start(self):
		newMenuItem = NSMenuItem.new()
		newMenuItem.setTitle_(self.name)
		newMenuItem.setAction_(self.showWindow_)
		newMenuItem.setTarget_(self)
		Glyphs.menu[WINDOW_MENU].append(newMenuItem)

	def showWindow_(self, sender):
		try:
			self.margin = 13
			gutter = 6
			widthName = 128
			widthFitBox = 20
			widthDimensionBox = 58
			self.textFieldHeight = 23
			self.lineToLine = self.textFieldHeight + 5
			self.w = vanilla.HUDFloatingWindow((100, 100), title=self.name, autosaveName='FMXCapsAndCorners')
			posy = self.margin - 4
			posx = self.margin
			posx += widthName
			width = widthFitBox
			self.w.headerFit = vanilla.TextBox((posx, posy, width, self.textFieldHeight), text='fit')
			posx += width
			width = widthDimensionBox
			self.w.headerWidth = vanilla.TextBox((posx, posy, width, self.textFieldHeight), text='width')
			posx += width + gutter
			width = self.textFieldHeight - 10
			posx += width + gutter
			width = widthDimensionBox
			self.w.headerDepth = vanilla.TextBox((posx, posy, width, self.textFieldHeight), text='depth')
			posx += width
			dialogWidth = posx + self.margin
			posy += self.lineToLine - 8
			for i in range(NUMBER_OF_FIELDS):
				posx = self.margin
				width = widthName
				setattr(self.w, 'name' + str(i), vanilla.TextBox((posx, posy + 2, width, self.textFieldHeight), text='_cap.something'))
				posx += width
				width = widthFitBox
				setattr(self.w, 'fit_' + str(i), vanilla.CheckBox((posx, posy, width, self.textFieldHeight), callback=self.fitCallback, title='', sizeStyle='small'))
				posx += width
				width = widthDimensionBox
				setattr(self.w, 'widt' + str(i), ArrowEditText((posx, posy, width, self.textFieldHeight), callback=self.editTextCallback, continuous=True, readOnly=False, formatter=None, placeholder='multiple'))
				posx += width + gutter
				width = self.textFieldHeight - 10
				imageButton = vanilla.ImageButton((posx, posy + 1, width, self.textFieldHeight - 2), callback=self.lockWidthDepthCallback)
				imageButton.getNSButton().setBordered_(False)
				setattr(self.w, 'lock' + str(i), imageButton)
				posx += width + gutter
				width = widthDimensionBox
				setattr(self.w, 'dept' + str(i), ArrowEditText((posx, posy, width, self.textFieldHeight), callback=self.editTextCallback, continuous=True, readOnly=False, formatter=None, placeholder='multiple'))
				posy += self.lineToLine
			posSize = self.w.getPosSize()
			self.w.setPosSize((posSize[0], posSize[1], dialogWidth, posSize[3]))

			self.updateDocument(None)
			self.w.open()
			self.w.bind('close', self.windowClose_)
			Glyphs.addCallback(self.update, UPDATEINTERFACE)
			Glyphs.addCallback(self.updateDocument, DOCUMENTACTIVATED)
			Glyphs.addCallback(self.updateDocument, DOCUMENTWILLCLOSE)
		except:
			print(traceback.format_exc())

	@objc.python_method
	def updateDocument(self, sender):
		for i in range(NUMBER_OF_FIELDS):
			for prefix in ['name', 'fit_', 'widt', 'lock', 'dept']:
				getattr(self.w, prefix + str(i)).show(False)
		if not Glyphs.currentDocument:
			self.font = None
			return
		self.font = Glyphs.currentDocument.font
		if not self.font:
			return

		corners = set()
		caps = set()
		for glyph in self.font.glyphs:
			for layer in glyph.layers:
				for hint in layer.hints:
					if hint.isCorner:
						if hint.type == CORNER:
							corners.add(hint.name)
						else:
							assert hint.type == CAP
							caps.add(hint.name)
		caps = sorted(list(caps))
		corners = sorted(list(corners))
		self.cc = [(c, CAP) for c in caps]
		self.cc += [(c, CORNER) for c in corners]
		i = 0
		for cname, ctype in self.cc:
			if ctype == CAP:
				getattr(self.w, 'fit_' + str(i)).show(True)
			nameBox = getattr(self.w, 'name' + str(i))
			nameBox.set(cname)
			nameBox.show(True)
			getattr(self.w, 'widt' + str(i)).show(True)
			getattr(self.w, 'lock' + str(i)).show(True)
			getattr(self.w, 'dept' + str(i)).show(True)
			i += 1
			if i == NUMBER_OF_FIELDS:
				break
		newHeight = self.lineToLine + len(self.cc) * self.lineToLine + 2 * self.margin - 16
		posSize = self.w.getPosSize()
		self.w.setPosSize((posSize[0], posSize[1], posSize[2], newHeight))
		self.isLocked = [False] * NUMBER_OF_FIELDS
		self.update(None)

	@objc.python_method
	def updateLockButtonImage(self, lockButton, i):
		if self.isLocked[i]:
			lockButton.setImage(imageNamed=NSImageNameLockLockedTemplate)
		else:
			lockButton.setImage(imageNamed=NSImageNameLockUnlockedTemplate)

	@objc.python_method
	def update(self, sender):
		try:
			currentDocument = Glyphs.currentDocument
			if not currentDocument or not self.font or not self.font.selectedLayers:
				return
			self.details = {}
			for layer in self.font.selectedLayers:
				for hint in layer.hints:
					if hint.isCorner:
						scale = hint.pyobjc_instanceMethods.scale()
						depth = abs(scale.y)
						width = abs(scale.x)
						isFit = hint.options & 8
						if hint.name in self.details:
							if self.details[hint.name]['widt'] != width:
								self.details[hint.name]['widt'] = MULTIPLE_VALUES
							if self.details[hint.name]['dept'] != depth:
								self.details[hint.name]['dept'] = MULTIPLE_VALUES
							if hint.type == CAP and self.details[hint.name]['fit'] != isFit:
								self.details[hint.name]['fit'] = MULTIPLE_VALUES
						else:
							hintDetails = {'type': hint.type, 'widt': width, 'dept': depth}
							if hint.type == CAP:
								hintDetails['fit'] = isFit
							self.details[hint.name] = hintDetails
			i = 0
			for cname, ctype in self.cc:
				anyDetails = cname in self.details
				for dimension in ['widt', 'dept']:
					scaleField = getattr(self.w, dimension + str(i))
					if anyDetails:
						if self.details[cname][dimension] == MULTIPLE_VALUES:
							scaleField.set('')
						else:
							scaleField.set('{0:g}'.format(self.details[cname][dimension] * 100.0))
					scaleField.show(anyDetails)
				lockButton = getattr(self.w, 'lock' + str(i))
				if anyDetails:
					self.isLocked[i] = self.details[cname]['widt'] == self.details[cname]['dept']
					self.updateLockButtonImage(lockButton, i)
				lockButton.show(anyDetails)
				if ctype == CAP:
					fitBox = getattr(self.w, 'fit_' + str(i))
					if anyDetails:
						fitBox.set(self.details[cname]['fit'] != 0)
						getattr(self.w, 'widt' + str(i)).show(not fitBox.get())
						# ^ for now, let’s hide this as Glyphs 3 does not report a sensible figure
						getattr(self.w, 'widt' + str(i)).enable(not fitBox.get())
						getattr(self.w, 'lock' + str(i)).show(not fitBox.get())
					fitBox.show(anyDetails)
				i += 1
				if i == NUMBER_OF_FIELDS:
					break
		except:
			print(traceback.format_exc())

	@objc.python_method
	def updateHint(self, cname, ctype, dimension, newValue):
		self.font.disableUpdateInterface()
		for layer in self.font.selectedLayers:
			undoHasBegun = False
			for hint in layer.hints:
				if hint.type == ctype and hint.name == cname:
					scale = hint.pyobjc_instanceMethods.scale()
					if dimension == 'widt':
						if abs(scale.x - newValue) < 0.00001:
							# no change. let’s skip this hint in order to avoid “empty” undo steps
							continue
						if scale.x > 0:
							scale.x = newValue
						else:
							scale.x = -newValue
					else:
						if abs(scale.y - newValue) < 0.00001:
							continue
						if scale.y > 0:
							scale.y = newValue
						else:
							scale.y = -newValue
					if not undoHasBegun:
						layer.parent.beginUndo()
						undoHasBegun = True
					hint.setScale_(scale)
			if undoHasBegun:
				layer.parent.endUndo()
		self.font.enableUpdateInterface()
		Glyphs.redraw()

	@objc.python_method
	def editTextCallback(self, editText):
		try:
			i = 0
			for cname, ctype in self.cc:
				for dimension in ['widt', 'dept']:
					if editText == getattr(self.w, dimension + str(i)):
						try:
							newValue = 0.01 * float(editText.get().strip('%'))
						except:
							return
						if self.isLocked[i]:
							self.updateHint(cname, ctype, 'widt', newValue)
							self.updateHint(cname, ctype, 'dept', newValue)
						else:
							self.updateHint(cname, ctype, dimension, newValue)
						return
				i += 1
				if i == NUMBER_OF_FIELDS:
					break
		except AttributeError:
			pass

	@objc.python_method
	def fitCallback(self, fitBox):
		try:
			i = 0
			for cname, ctype in self.cc:
				if fitBox == getattr(self.w, 'fit_' + str(i)):
					for layer in self.font.selectedLayers:
						for hint in layer.hints:
							if hint.type == ctype and hint.name == cname:
								hint.options = hint.options ^ 8
					return
				i += 1
				if i == NUMBER_OF_FIELDS:
					break
		except AttributeError:
			pass

	@objc.python_method
	def lockWidthDepthCallback(self, lockButton):
		try:
			i = 0
			for cname, ctype in self.cc:
				if lockButton == getattr(self.w, 'lock' + str(i)):
					self.isLocked[i] = not self.isLocked[i]
					lockButton = getattr(self.w, 'lock' + str(i))
					self.updateLockButtonImage(lockButton, i)
					if self.isLocked[i]:
						cname, ctype = self.cc[i]
						details = self.details[cname]
						if details['widt'] != details['dept']:
							details['widt'] = (details['widt'] + details['dept']) / 2
							details['dept'] = details['widt']
							self.updateHint(cname, ctype, 'widt', details['widt'])
							self.updateHint(cname, ctype, 'dept', details['widt'])
					return
				i += 1
				if i == NUMBER_OF_FIELDS:
					break
		except AttributeError:
			pass

	@objc.python_method
	def __del__(self):
		Glyphs.removeCallback(self.update)
		Glyphs.removeCallback(self.updateDocument)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__

	def windowClose_(self, window):
		try:
			Glyphs.removeCallback(self.update)
			Glyphs.removeCallback(self.updateDocument)
			return True
		except:
			print(traceback.format_exc())
