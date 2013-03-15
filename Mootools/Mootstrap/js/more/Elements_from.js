// MooTools: the javascript framework.
// Load this file's selection again by visiting: http://mootools.net/more/fa5d2958be95347119c21f8e64f99d8e 
// Or build this file again with packager using: packager build More/Elements.From
/*
---
copyrights:
  - [MooTools](http://mootools.net)

licenses:
  - [MIT License](http://mootools.net/license.txt)
...
*/
Elements.from=function(e,d){if(d||d==null){e=e.stripScripts();}var b,c=e.match(/^\s*<(t[dhr]|tbody|tfoot|thead)/i);
if(c){b=new Element("table");var a=c[1].toLowerCase();if(["td","th","tr"].contains(a)){b=new Element("tbody").inject(b);if(a!="tr"){b=new Element("tr").inject(b);
}}}return(b||new Element("div")).set("html",e).getChildren();};
