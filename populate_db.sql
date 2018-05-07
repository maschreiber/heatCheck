-- This is just the database creation part of test-sample.sql 
-- First create the heathcek db, then run
-- psql -d heatcheck -a -f populate_db.sql
CREATE TABLE game(
	gid INTEGER NOT NULL PRIMARY KEY UNIQUE,
	day VARCHAR(256) NOT NULL,
	opponent VARCHAR(256) NOT NULL,
	city VARCHAR(256) NOT NULL,
	state VARCHAR(256) NOT NULL
	--duke_score INTEGER NOT NULL CHECK(duke_score>-1),
	--opp_score INTEGER NOT NULL CHECK(opp_score>-1),
);


CREATE TABLE shot(
	sid INTEGER NOT NULL PRIMARY KEY UNIQUE,
	gid INTEGER NOT NULL,
	name VARCHAR(256) NOT NULL,
	period INTEGER NOT NULL CHECK(period IN (1,2,3,4)),
	clock INTEGER NOT NULL,
	shot_type INTEGER NOT NULL CHECK(shot_type IN (2,3)),
	made INTEGER NOT NULL,
	dribbles INTEGER NOT NULL CHECK(dribbles > -1),
 	x INTEGER NOT NULL CHECK(x<=100),
	y INTEGER NOT NULL CHECK(y<=50),
	def_name VARCHAR(256)
);






\COPY shot FROM 'shot_prepared.csv' WITH CSV HEADER DELIMITER ',' NULL '';

-- SELECT * FROM shot;


\COPY game FROM 'game_prepared.csv' WITH CSV HEADER DELIMITER ',' NULL '';

