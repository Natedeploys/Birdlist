#!/bin/bash

apt-get -y install pwgen

MYSQL_ADMIN_PASS=$(pwgen -sy 16 1)
echo "$MYSQL_ADMIN_PASS" > /root/mysql-password.txt

debconf-set-selections <<__EOF__
mysql-server-5.5 mysql-server/root_password       password $MYSQL_ADMIN_PASS
mysql-server-5.5 mysql-server/root_password_again password $MYSQL_ADMIN_PASS
__EOF__

apt-get -y install mysql-server

django_db='db'
django_password='abcd'  # TODO: change this

# Recover data iff made accessible to container
if [ -d /home/db/mysql-backups/latest/ ] ; then
    cd /home/db/mysql-backups/latest/
    bzcat *.sql.bz2 | mysql --force --password="$MYSQL_ADMIN_PASS"
else
    # FIXME: create empty database
fi

mysql --verbose --force --password="$MYSQL_ADMIN_PASS" <<__EOF__
CREATE USER 'django'@'localhost' IDENTIFIED BY '${django_password}';
GRANT ALL ON django.* TO 'django'@'localhost';
FLUSH PRIVILEGES;
QUIT
__EOF__

mysql --verbose --force --password="$MYSQL_ADMIN_PASS" django <<__EOF__
DELIMITER //
CREATE FUNCTION django_password(
  pass VARCHAR(32)
) RETURNS VARCHAR(128)
DETERMINISTIC
BEGIN
        DECLARE salt char(5);
        DECLARE hash VARCHAR(40);
        SET salt = MID(RAND(), 3, 5);
        SET hash = SHA(CONCAT(salt, pass));
        RETURN CONCAT('sha1\$', salt, '$', hash);
END//
DELIMITER ;

UPDATE auth_user SET password=django_password('${django_password}') WHERE username='${django_db}';
__EOF__

apt-get -y install phpmyadmin python-mysqldb
