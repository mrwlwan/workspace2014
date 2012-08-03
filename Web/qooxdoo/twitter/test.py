import cherrypy

class TaoBao:
    @cherrypy.expose
    def index(self):
        return 'Hello world!'

cherrypy.quickstart(TaoBao(), '/', 'taobao.conf')
