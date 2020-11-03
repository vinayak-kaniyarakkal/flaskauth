drop table if exists user;
CREATE TABLE IF NOT EXISTS user (
	id data_type INTEGER PRIMARY KEY,
   	name data_type TEXT NOT NULL,
	password data_type TEXT NOT NULL,
	table_constraints
);
drop table if exists valid_login;
CREATE TABLE IF NOT EXISTS valid_login (
	id data_type INTEGER PRIMARY KEY,
   	time data_type TEXT NOT NULL,
   	user_id data_type TEXT NOT NULL,
	table_constraints
);
drop table if exists invalid_login;
CREATE TABLE IF NOT EXISTS invalid_login (
	id data_type INTEGER PRIMARY KEY,
   	time data_type TEXT NOT NULL,
   	user_id data_type TEXT NOT NULL,
   	name data_type TEXT NOT NULL,
   	password data_type TEXT NOT NULL,
	table_constraints
);
