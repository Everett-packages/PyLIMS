sudo ln -s /home/everett/Projects/PyLIMS /var/www/html/PyLIMS

sudo nano /etc/apache2/apache2.conf 

add:
AddHandler cgi-script .cgi .pl
<Directory "/var/www/html/PyLIMS/cgi">
  AllowOverride None
  Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
  Order allow,deny
  Allow from all
</Directory>

sudo a2enmod cgi
sudo service apache2 restart

setenv PYCHARM_JDK /usr/local/jdk1.8.0_11/

create database pylims_dev

CREATE USER 'admin'@'%' IDENTIFIED BY 'admin1';
GRANT SELECT, INSERT, DELETE, UPDATE ON pylims_dev.* TO 'admin'@'%';

CREATE USER 'guest'@'%' IDENTIFIED BY 'guest1';
GRANT SELECT ON pylims_dev.* TO 'guest'@'%';

CREATE USER 'expression'@'%' IDENTIFIED BY 'expression1';
GRANT SELECT ON pylims_dev.expression TO 'expression'@'%';

create table construct (construct_id varchar(50) not null, primary key(construct_id));
create table expression (expression_id varchar(50) not null, primary key(expression_id));
create table purification (purification_id varchar(50) not null, primary key(purification_id));

