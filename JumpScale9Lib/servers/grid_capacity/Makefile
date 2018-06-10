
generate:
	cp server/requirements.txt server/requirements.txt.back
	go-raml server -l python --kind flask --dir server --ramlfile api_spec/main.raml --no-main --no-apidocs
	raml2html -p api_spec/main.raml > server/templates/api.html
	sed -i "s/import handlers/from . import handlers/g" server/api_api.py
	mv server/requirements.txt.back server/requirements.txt