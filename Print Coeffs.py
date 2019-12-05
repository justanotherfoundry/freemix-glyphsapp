#MenuTitle: Print Coeffs
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

from __future__ import division, print_function, unicode_literals

__doc__='''
Prints the interpolation coefficients for each master in all instances.
'''

import re

abbreviations = {
	'Light': 'Lt',
	'Bold': 'Bd',
	'Text': 'Tx',
	'Banner': 'Bn',
	'Tall': 'Ta',
}
abbreviations = dict((re.escape(k), v) for k, v in abbreviations.iteritems())
pattern = re.compile("|".join(abbreviations.keys()))
master_names = [ pattern.sub(lambda m: abbreviations[re.escape(m.group(0))], master.name).replace(' ','') for master in  Glyphs.font.masters ]
longest_master_name = max( master_names, key = len )
master_column_width = max( 11, len( longest_master_name ) + 1 )

instance_names = [ instance.fullName for instance in Glyphs.font.instances ]
longest_instance_name = max( instance_names, key = len )
first_column_width = len( longest_instance_name ) + 5

print( ' ', ''.rjust( first_column_width ), ' '.join( [ n.rjust( master_column_width ) for n in master_names] ) )

for instance in Glyphs.font.instances:
	print( ' ' if instance.active else '*', end='' )
	print( instance.fullName.ljust( first_column_width ), end='' )
	for master in  Glyphs.font.masters:
		try:
			print( ('%10.2f%%' % ( instance.instanceInterpolations[master.id] * 100 ) ).rjust( master_column_width ), end='' )
		except KeyError:
			print( ''.rjust( master_column_width ), end='' )
	print()
