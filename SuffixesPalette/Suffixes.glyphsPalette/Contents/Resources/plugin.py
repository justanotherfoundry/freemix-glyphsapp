# encoding: utf-8

from GlyphsApp.plugins import *
from vanilla import *
from GlyphsApp import UPDATEINTERFACE


NUMBER_OF_FIELDS = 20
MINIMUM_NON_DOT_SUFFIX_LENGTH = 4

class SuffixesPalette( PalettePlugin ):

	# seems to be called whenever a new font is opened
	# careful! not called when the user switches to a different, already opened font
	def settings(self):
		self.name = Glyphs.localize({'en': u'Suffixes'})
		# Create Vanilla window and group with controls
		self.width = 150
		self.margin = 5
		self.gutter = 3
		self.textFieldHeight = 15
		self.height = 2 * self.margin + self.textFieldHeight + self.gutter * 2
		self.paletteView = Window( (self.width, self.height), minSize=(self.width, self.height - 10), maxSize=(self.width, self.height + 200 ) )
		self.paletteView.group = Group( (0, 0, self.width, self.height ) )
		posx = self.margin
		for i in xrange( NUMBER_OF_FIELDS ):
			setattr( self.paletteView.group, 'txt' + str( i ), EditText( ( 10+28*i, self.margin, 25, self.textFieldHeight ), callback=self.editTextCallback, continuous=False, readOnly=False, formatter=None, placeholder='multiple', sizeStyle='mini' ) )
		# Set dialog to NSView
		self.dialog = self.paletteView.group.getNSView()

	# splits a glyph nname into its base name and the dot suffixes, retaining the dots
	def dotSplit( self, glyphName ):
		ds = [ '.' + n if i != 0 else n for i, n in enumerate( glyphName.split('.') ) ]
		assert ds != []
		if not ds[0]:
			# this happens for .notdef
			del ds[0]
		return ds

	# changes the index'th suffix of all selected glyphs.
	# in simulationMode this returns ( oldName, newName ) if newName already exists
	def changeDotSuffix( self, newSuffix, index, simulationMode = False ):
		for glyph in self.selectedGlyphs:
			split = self.dotSplit( glyph.name )
			try:
				split[index] = newSuffix
				newName = ''.join( split )
			except IndexError:
				newName = glyph.name + newSuffix
			if glyph.name != newName:
				if simulationMode:
					if self.font.glyphs[newName]:
						return ( glyph.name, newName )
				else:
					glyph.name = newName
					glyph.updateGlyphInfo()
		return ( None, None )

	# removes the last n characters and appends newSuffix
	# for all selected glyphs
	def changeNameEnding( self, newSuffix, n ):
		for glyph in self.selectedGlyphs:
			glyph.name = glyph.name[:-n] + newSuffix

	# captures changes to the text fields
	def editTextCallback( self, editText):
		for i in xrange( NUMBER_OF_FIELDS ):
			if editText.getPosSize() == getattr( self.paletteView.group, 'txt' + str( i ) ).getPosSize():
				# we have found the right text field
				if editText.get() != self.nameSplit[i]:
					if self.suffixLength == 0:
						errorNameBefore, errorNameAfter = self.changeDotSuffix( editText.get(), i, simulationMode = True )
						if errorNameBefore:
							editText.enable( False )
							Message( 'Existing name', 'This would change ' + errorNameBefore + ' to ' + errorNameAfter + ', which already exists.\nNo glyphs were renamed.' )
							editText.enable( True )
						else:
							self.changeDotSuffix( editText.get(), i )
					else:
						self.changeNameEnding( editText.get(), self.suffixLength )
				return

	# returns a list of dot split for all glyphs, replacing inconsistent suffixes with '.'
	def determineSharedDotSplit( self, selectedNames ):
		sharedNames = []
		for selectedName in selectedNames:
			glyphNameSplit = self.dotSplit( selectedName )
			# for the first selected glyph, this is triggered:
			if not sharedNames:
				sharedNames = glyphNameSplit
				continue
			lengthDiff = len( glyphNameSplit ) - len( sharedNames )
			# glyph longer than shared: compare then pad
			if lengthDiff > 0:
				for i in xrange( ( len( sharedNames ) ) ):
					if sharedNames[i] != glyphNameSplit[i]:
						sharedNames[i] = '.'
				sharedNames += ['.'] * lengthDiff
			# shared longer than glyph: compare then set rest to '.'
			if lengthDiff < 0:
				for i in xrange( ( len( glyphNameSplit ) ) ):
					if sharedNames[i] != glyphNameSplit[i]:
						sharedNames[i] = '.'
				sharedNames[lengthDiff:] = ['.'] * (-lengthDiff)
			# same length: compare
			else:
				for i in xrange( ( len( glyphNameSplit ) ) ):
					if sharedNames[i] != glyphNameSplit[i]:
						sharedNames[i] = '.'
		return sharedNames

	# tries to find shared string ending, i.e. non-dot suffix
	# returns the shared ending or ' ' (note: this is a space)
	# if no sufficiently long suffix was found.
	def determineSharedSuffix( self, selectedNames, minimumLength = MINIMUM_NON_DOT_SUFFIX_LENGTH ):
			self.suffixLength = 0
			# shortcut if we have only one name
			if len( selectedNames ) == 1:
				return ' '
			name0 = selectedNames[0]
			self.suffixLength = len( name0 )
			for selectedName in selectedNames[1:]:
				if self.suffixLength > len( selectedName ):
					self.suffixLength = len( selectedName )
				for i in xrange( self.suffixLength ):
					if name0[-i-1] != selectedName[-i-1]:
						if i < minimumLength:
							self.suffixLength = 0
							return ' '
						self.suffixLength = i
						break
			return name0[-self.suffixLength:]

	def updateTextFields( self ):
		for i in xrange( ( self.fieldCount ) ):
			try:
				editText = getattr( self.paletteView.group, 'txt' + str( i ) )
			except IndexError:
				continue
			if self.nameSplit[i] == '.':
				editText.set( '' )
			else:
				editText.set( self.nameSplit[i] )

	# re-sizes and re-positions the fields
	# according to the number of suffixes
	def updateLayout( self ):
		suffixFieldWidth = 1.0 * ( self.width - self.margin - ( self.fieldCount - 1 ) * self.gutter ) / ( self.fieldCount + 1 )
		x = self.margin
		if self.fieldCount == 0:
			x = self.width + 1
		w = round( suffixFieldWidth * 2 + self.gutter )
		for i in xrange( NUMBER_OF_FIELDS ):
			editText = getattr( self.paletteView.group, 'txt' + str( i ) )
			if x > self.width:
				editText.show( False )
			else:
				editText.show( True )
				editText.setPosSize( ( x, self.margin, w, self.textFieldHeight ) )
			x += w + self.gutter
			# set the width to suffixFieldWidth (this only has an effect in the first iteration)
			w = suffixFieldWidth

	# the main update function called by Glyphs
	def update( self, sender=None ):
		# do not update in case the palette is collapsed
		if self.dialog.frame().origin.y != 0:
			return
		if sender:
			self.font = sender.object()
		sharedNames = []
		# self.suffixLength is used to store whether the second field
		# represents the last suffixLength characters in the glyph name
		self.suffixLength = 0
		if self.font.selectedLayers:
			self.selectedGlyphs = [ layer.parent for layer in self.font.selectedLayers ]
		else:
			self.selectedGlyphs = []
		selectedNames = [ selectedGlyph.name for selectedGlyph in self.selectedGlyphs ]
		self.nameSplit = self.determineSharedDotSplit( selectedNames )
		self.fieldCount = len( self.nameSplit )
		if self.fieldCount == 1:
				# no suffixes found yet: append another element
				# that may be a space if no non-dot suffix was found
				# so the user can add a suffix
				self.nameSplit.append( self.determineSharedSuffix( selectedNames ) )
				self.fieldCount = 2
		self.updateTextFields()
		self.updateLayout()

	def start(self):
		# Adding a callback for the 'GSUpdateInterface' event
		Glyphs.addCallback(self.update, UPDATEINTERFACE)
	
	def __del__(self):
		Glyphs.removeCallback(self.update)

	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
	
	# Temporary Fix
	# Sort ID for compatibility with v919:
	_sortID = 0
	def setSortID_(self, id):
		try:
			self._sortID = id
		except Exception as e:
			self.logToConsole( "setSortID_: %s" % str(e) )
	def sortID(self):
		return self._sortID
	