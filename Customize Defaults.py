#MenuTitle: Customize Defaults
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

'''
This is not a macro you would use daily but more of a documentation of
settings that can be accessed in Python via intDefaults.

Values that cannot be set via the Glyphs UI (this not commented out here)
are particularly interesting.

Feel free to contribute more if you find other values that may be useful 
to be set via Python scripts.
'''

from GlyphsApp import *

# see https://forum.glyphsapp.com/t/shifting-view-when-point-is-selected/4857
Glyphs.intDefaults["GSCenterSelectionOnMasterSwitch"] = 0

# see https://forum.glyphsapp.com/t/metrics-info-in-text-mode/5088
Glyphs.intDefaults["TextModeNumbersThreshold"] = 3000

Glyphs.intDefaults["showShadowPath"] = 0

# see https://forum.glyphsapp.com/t/kerning-steps-with-keyboard/4889
# Glyphs.intDefaults["GSKerningIncrementLow"] = 4
# Glyphs.intDefaults["GSKerningIncrementHigh"] = 20

# see https://forum.glyphsapp.com/t/request-dynamic-text-view-width/2939/9
# Glyphs.intDefaults["GSFontViewWidth"] = 8000
