# Copyright (c) 2012 Web Notes Technologies Pvt Ltd (http://erpnext.com)
# 
# MIT License (MIT)
# 
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

from __future__ import unicode_literals
import webnotes

class DocType:
	def __init__(self, d, dl):
		self.doc, self.doclist = d,dl

	def autoname(self):
		"""
			Creates a url friendly name for this page.
			Will restrict the name to 30 characters, if there exists a similar name,
			it will add name-1, name-2 etc.
		"""
		from webnotes.utils import cint
		if (self.doc.name and self.doc.name.startswith('New Page')) or not self.doc.name:
			self.doc.name = self.doc.page_name.lower().replace('"','').replace("'",'').\
				replace(' ', '-')[:20]
			if webnotes.conn.exists('Page',self.doc.name):
				cnt = webnotes.conn.sql("""select name from tabPage 
					where name like "%s-%%" order by name desc limit 1""" % self.doc.name)
				if cnt:
					cnt = cint(cnt[0][0].split('-')[-1]) + 1
				else:
					cnt = 1
				self.doc.name += '-' + str(cnt)

	# export
	def on_update(self):
		"""
			Writes the .txt for this page and if write_content is checked,
			it will write out a .html file
		"""
		import conf
		from webnotes.modules.import_file import in_import
		if not in_import and getattr(conf,'developer_mode', 0) and self.doc.standard=='Yes':
			from webnotes.modules.export_file import export_to_files
			from webnotes.modules import get_module_path, scrub
			import os
			export_to_files(record_list=[['Page', self.doc.name]])
	
			# write files
			path = os.path.join(get_module_path(self.doc.module), 'page', scrub(self.doc.name), scrub(self.doc.name))
								
			# js
			if not os.path.exists(path + '.js'):
				with open(path + '.js', 'w') as f:
					f.write("""wn.pages['%s'].onload = function(wrapper) { 
	wn.ui.make_app_page({
		parent: wrapper,
		title: '%s',
		single_column: true
	});					
}""" % (self.doc.name, self.doc.title))

	def get_from_files(self):
		"""
			Loads page info from files in module
		"""
		from webnotes.modules import get_module_path, scrub
		import os
		
		path = os.path.join(get_module_path(self.doc.module), 'page', scrub(self.doc.name))

		# script
		fpath = os.path.join(path, scrub(self.doc.name) + '.js')
		if os.path.exists(fpath):
			with open(fpath, 'r') as f:
				self.doc.script = f.read()

		# css
		fpath = os.path.join(path, scrub(self.doc.name) + '.css')
		if os.path.exists(fpath):
			with open(fpath, 'r') as f:
				self.doc.style = f.read()
		
		# html
		fpath = os.path.join(path, scrub(self.doc.name) + '.html')
		if os.path.exists(fpath):
			with open(fpath, 'r') as f:
				self.doc.content = f.read()
				
		if webnotes.lang != 'en':
			from webnotes.translate import update_lang_js
			self.doc.script = update_lang_js(self.doc.script, path)
