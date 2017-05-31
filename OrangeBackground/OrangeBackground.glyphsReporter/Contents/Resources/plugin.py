# encoding: utf-8

###########################################################################################################
#
#
#	Reporter Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################


from GlyphsApp.plugins import *

class OrangeBackgroundClass(ReporterPlugin):

	def settings(self):
		self.menuName = Glyphs.localize({'en': u'Orange Background'})
		
	def background(self, layer):
		try:
			Glyphs = NSApplication.sharedApplication()
			if ( Glyphs.currentDocument.windowController().toolDrawDelegate().isKindOfClass_(NSClassFromString("GlyphsToolSelect")) or Glyphs.currentDocument.windowController().toolDrawDelegate().isKindOfClass_(NSClassFromString("GSToolSelect")) ):
				# switch off the built-in background
				if Glyphs.defaults["showBackground"] != 0:
					Glyphs.defaults["showBackground"] = 0
				# determine "background" layer
				try:
					background = layer.foreground()
					# background is active
				except:
					# foreground is active
					background = layer.background
				# draw the "background" layer in orange
				NSColor.orangeColor().set()
				try:
					background.bezierPath.setLineWidth_( 1.0 / self.getScale() )
					background.bezierPath.stroke()
				except:
					# background.bezierPath() is None
					pass
				try:
					background.bezierPath().setLineWidth_( 1.0 / self.getScale() )
					background.bezierPath().stroke()
				except:
					# background.bezierPath() is None
					pass
				try:
					background.openBezierPath.setLineWidth_( 1.0 / self.getScale() )
					background.openBezierPath.stroke()
				except:
					# background.bezierPath() is None
					pass
				try:
					background.openBezierPath().setLineWidth_( 1.0 / self.getScale() )
					background.openBezierPath().stroke()
				except:
					# background.openBezierPath() is None
					pass
		except Exception as e:
			self.logToConsole( "OrangeBackground error: %s" % str(e) )
