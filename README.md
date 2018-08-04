# WebPageStatusCheck_django

### Screenshot

![Screenshot](https://s15.postimg.cc/yrd5czkez/IMG_0098.png "Screenshot")

Django rewrite of my Flask app by the same name. Works exactly the same but has an added sql db to monitor uptime. Uptime is displayed in the html templates.

Database ia only read from immediately after statuses are checked. Web page requests load all information from memory rather than reading the db on each request.

### Todo:
* Unittests
* Search input escaping - the field needs to be rewritten to use a django form class. In its current state the user input is not escaped so can be used as an attack vector.
