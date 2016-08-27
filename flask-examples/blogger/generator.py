from flask import Flask, render_template
from werkzeug import cached_property

import markdown
import os
import yaml

POSTS_FILE_EXTENSION = ".md"

app = Flask(__name__)
# __name__ holds the name of the current file
# if running as the main file (main method), __name__ == __main__
# if being imported into another file, __name__ == __moduleName__

@app.template_filter('date')
def format_date(value, format="%B %d, %Y"):
	return value.strftime(format)

#first way to inject filters
#return render_template("post.html", format_date=format_date)
#second way to inject filters
#@app.context_processor
def inject_format_date():
	return {"format_date": format_date}

#third way to inject filters
#or this way (delcare a filter in the instance of jinja_env, and then you can just pipe text into the filter in templates
##app.jinja_env.filters['date'] = format_date

@app.route('/')
def index():
	return "Hello, world! Port 8000."


@app.route('/blog/<path:path>')
def post(path):	
	path = os.path.join('posts', path + POSTS_FILE_EXTENSION)
	post = Post(path)
	#import ipdb; ipdb.set_trace()
	#raise
	return render_template("post.html", post_content = post)


class Post(object):
	
	def __init__(self, path):
		self.path = path
		self._initialize_metadata()
		
	@cached_property
	def html(self):
		with open(self.path, 'r') as f:
			content = f.read().strip().split('=split=',1)[1]
			#print "Content:\n", content
			return markdown.markdown(content)
		
	def _initialize_metadata(self):
		content = ''
		with open(self.path,'r') as f:
			for line in f:
				if not line:
					break
				content += line
		
		content = content.split('=split=')[0].strip()
		
		#print "YAML test:\n"
		#print yaml.load(content)
		self.__dict__.update(yaml.load(content))
					
				
if __name__ == "__main__":
	app.run(port=8000, debug=True)