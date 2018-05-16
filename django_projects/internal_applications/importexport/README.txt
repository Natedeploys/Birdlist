# things you need to set in the settings.py file


INSTALLED_APPS = (
    ...
    'importexport',
)


# this url line needs to come before the admin line!
urlpatterns += patterns('',
    (r'^admin/import-export/', include('importexport.urls')),
)


# where is your mysqldump program?
MYSQLDUMP = "/usr/local/bin/mysqldump"
