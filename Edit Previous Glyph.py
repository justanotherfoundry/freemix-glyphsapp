#MenuTitle: Edit Previous Glyph
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__="""
Activates the previous glyph in the tab for editing. You can give it a keyboard shortcut in the macOS system preferences.
"""

Font.currentTab.textCursor = (Font.currentTab.textCursor - 1) % len(Font.currentTab.layers)
