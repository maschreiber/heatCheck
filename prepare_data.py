# usage: python prepare_data.py
# must be in same directory as shots.csv
# will output game_prepared.csv, shot_prepared.csv
# will give a 'SettingWithCopyWarning' but this can be ignored
import pandas as pd

shot = pd.read_csv('shots.csv', sep = '|')

# Make column names normal
shot.columns = shot.columns.str.lower()
shot.columns = shot.columns.str.replace('-','_')


# Remove NaN's in all but the defender column
ok_for_nan = ['defender_first_name', 'defender_last_name']
not_ok_for_nan = [col for col in list(shot.columns) if col not in ok_for_nan]
bad_rows = shot[not_ok_for_nan].isnull().any(axis=1)
good_rows = ~bad_rows
shot = shot[good_rows]


# Select only shots by Duke players
shot = shot[((shot.team == 'home') & (shot.home_city == 'Duke')) |\
        ((shot.team == 'visitors') & (shot.vist_city == 'Duke'))]

# Date
shot.year  = shot.year .apply(str)
shot.month = shot.month.apply(str)
shot.date  = shot.date .apply(str)

single_digits = ['1','2','3','4','5','6','7','8','9']
shot.month[shot.month.isin(single_digits)] = '0' + shot.month
shot.date[shot.date.isin(single_digits)] = '0' + shot.date
shot['date_string'] = shot.year +'_' + shot.month + '_' + shot.date

shot = shot.drop('day', axis=1)
shot = shot.rename(columns = {'date_string':'day'})


# Clock
# Note we still have seperate time for each period
clock_split = shot.clock.str.split(':').apply(pd.Series)
shot.clock = (clock_split[0].astype(int) * 60) + clock_split[1].astype(int)


# Name
shot['name'] = shot.first_name + ' ' + shot.last_name
shot['def_name'] = shot.defender_first_name + ' ' + shot.defender_last_name


# Shot
shot['made']= (shot.result=='made').astype(int)
shot = shot.rename(columns={'points_type':'shot_type'})


# Opponent
shot['opponent'] = shot.vist_city
shot.opponent[shot.opponent == 'Duke'] = shot.home_city[shot.opponent == 'Duke']

# Rename x,y
shot = shot.rename(columns={'x_coordinate':'x', 'y_coordinate':'y'})


# Create game dataframe
game = shot[['day','opponent','city','state']].drop_duplicates()

game = game.sort_values(by =['day','opponent'])
game = game.reset_index().drop('index', axis=1)
game.index.name = 'gid'
game = game.reset_index()


# Reindex shot and reference game dataframe
shot = shot.sort_values(by = ['day','period','clock'], 
                    ascending = [True, True, False])
shot = shot.reset_index().drop('index', axis =1)
shot.index.name = 'sid'
shot = shot.reset_index()

shot['gid'] = shot.merge(game, on=['day', 'opponent']).gid


# Only take columns from shot we want
shot = shot[['sid', 'gid', 'name', 
         'period', 'clock', 
         'shot_type', 'made', 
         'dribbles', 'x', 'y', 'def_name']]


# Write to .csv
game.to_csv('game_prepared.csv', index= False)
shot.to_csv('shot_prepared.csv', index= False)
