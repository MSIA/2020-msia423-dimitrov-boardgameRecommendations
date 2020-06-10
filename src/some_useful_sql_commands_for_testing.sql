# COUNT THE NUMBER OF GAMES IN EACH CLUSTER
SELECT COUNT(*) AS count, cluster FROM boardgames GROUP BY cluster

# VERIFY THE TOTAL NUMBER OF GAMES CHECKS OUT
SELECT SUM(count) FROM (SELECT COUNT(*) AS count, cluster FROM boardgames GROUP BY cluster)

# CHECK THE TOP 10 GAMES BY USER RATING FOR A GIVEN GAME_ID
SELECT game_id, name, average_user_rating, cluster FROM boardgames WHERE cluster==(SELECT cluster FROM boardgames WHERE game_id==1) ORDER BY average_user_rating DESC LIMIT 10

# CHECK THE TOP 10 GAMES BY USER RATING FOR A GIVEN CLUSTER ID
SELECT game_id, name, average_user_rating, cluster FROM boardgames WHERE cluster== 231 ORDER BY average_user_rating DESC LIMIT 10
