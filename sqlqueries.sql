
SELECT name, COUNT(SELECT shot_type FROM shot WHERE shot_type = 3), COUNT(SELECT shot_type FROM shot WHERE shot_type = 2) 
	FROM shot s, game g 
	WHERE g.gid=s.gid AND period = 4
	GROUP BY name;
	--How many threes vs how many twos in the 4th quarter by name
SELECT name, x, y 
	FROM shot
	WHERE made = 1
	GROUP BY name;
SELECT name, x, y
	FROM shot
	WHERE made = 0
	GROUP BY name;
SELECT name, x, y, shot_type
	FROM shot
	WHERE period = 4
	GROUP BY name;
SELECT name, gid, day, opponent, ((SELECT COUNT(*) FROM shot WHERE made = 1)/(SELECT COUNT(*) FROM shot)) AS shotpercent
	FROM shot s, game g
	WHERE shotpercent > .35
	GROUP BY name;
	--game where shot percentage made > 35% - can parameterize this to take in any percentage