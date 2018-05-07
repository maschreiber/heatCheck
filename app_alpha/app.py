from __future__ import print_function
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
from sqlalchemy import create_engine
from sqlalchemy.inspection import inspect
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from matplotlib.patches import Circle, Rectangle, Arc
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
import numpy as np
import models
import seaborn as sns
import matplotlib.pyplot as plt
import mpld3
import sys
import ast


plt.switch_backend('agg')


app = Flask(__name__)
app.secret_key = 's3cr3t'
app.config.from_object('config')
db = SQLAlchemy(app, session_options={'autocommit': False})

#cmap = plt.cm.Reds
#cdict = cmap._segmentdata
cdict = {
    'blue': [(0.0, 0.6313725709915161, 0.6313725709915161), (0.25, 0.4470588266849518, 0.4470588266849518), (0.5, 0.29019609093666077, 0.29019609093666077), (0.75, 0.11372549086809158, 0.11372549086809158), (1.0, 0.05098039284348488, 0.05098039284348488)],
    'green': [(0.0, 0.7333333492279053, 0.7333333492279053), (0.25, 0.572549045085907, 0.572549045085907), (0.5, 0.4156862795352936, 0.4156862795352936), (0.75, 0.0941176488995552, 0.0941176488995552), (1.0, 0.0, 0.0)],
    'red': [(0.0, 0.9882352948188782, 0.9882352948188782), (0.25, 0.9882352948188782, 0.9882352948188782), (0.5, 0.9843137264251709, 0.9843137264251709), (0.75, 0.7960784435272217, 0.7960784435272217), (1.0, 0.40392157435417175, 0.40392157435417175)]
}

mymap = LinearSegmentedColormap('my_colormap', cdict, 1024)


@app.route('/')
def home():
    games = db.session.query(models.Game).all()
    return render_template('home.html',x=[], y = [], shots_list=[], made = [])

def query_to_list(rset):
    """List of result
    Return: columns name, list of result
    """
    result = []
    for obj in rset:
        instance = inspect(obj)
        items = instance.attrs.items()
        result.append([x.value for _,x in items])
    return list(instance.attrs.keys()), result

def query_to_dict(rset):
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)
    return result


def find_shootingPcts(shot_df, gridNum):
    x = shot_df.x[shot_df['y']<50] #i want to make sure to only include shots I can draw
    y = shot_df.y[shot_df['y']<50]

    x_made = shot_df.x[(shot_df['made']==1) & (shot_df['y']<50)]
    y_made = shot_df.y[(shot_df['made']==1) & (shot_df['y']<50)]

    #compute number of shots made and taken from each hexbin location
    hb_shot = plt.hexbin(x, y, gridsize=3, extent=(0,50,47,0));
    plt.close() #don't want to show this figure!
    hb_made = plt.hexbin(x_made, y_made, gridsize=3, extent=(0,25,47,0),cmap=plt.cm.Reds);
    plt.close()

    #compute shooting percentage
    ShootingPctLocs = hb_made.get_array() / hb_shot.get_array()
    ShootingPctLocs[np.isnan(ShootingPctLocs)] = 0 #makes 0/0s=0
    return (ShootingPctLocs, hb_shot)

@app.route('/', methods=['POST'])
def home_post():

    gids = request.form['gids']
    periods = request.form['periods']
    clock_min = request.form['clock_min']
    clock_max = request.form['clock_max']
    dribbles_min = request.form['dribbles_min']
    dribbles_max = request.form['dribbles_max']
    made = request.form['made']
    shot_type = request.form['shot_type']
    names = request.form['names']    

    gids_disp = gids
    periods_disp = periods
    clock_min_disp = clock_min
    clock_max_disp = clock_max
    dribbles_min_disp = dribbles_min
    dribbles_max_disp = dribbles_max
    made_disp = made
    shot_type_disp = shot_type
    names_disp = names

    gids = gids.split(',')
    periods = periods.split(',')
    made = made.split(',')
    shot_type = shot_type.split(',')
    names = names.split(',') 
    names = [n.strip() for n in names]
   

    


    if gids == ['']:
        gids = db.session.query(models.Game.gid).all()
        gids_disp = "" 
    
    if periods == ['']:
        periods = [1,2,3]
        periods_disp = "" 

    if clock_min == '': 
        clock_min = 0

    if clock_max == '':
        clock_max = 1200    
    
    if dribbles_min == '': 
        dribbles_min = 0

    if dribbles_max == '':
        dribbles_max = 40   
    
    if made == ['']:
        made = [0, 1]

    if shot_type == ['']:
        shot_type = [2,3]

    all_names = [r.name for r in
            db.session.query(models.Shot.name).distinct()]
   
    print('**********************************')
    print(all_names)
    print(names)
    print('**********************************')

    if names == ['']:
        names = all_names
        names_disp = ''
    else:
        #This allows us not to have to type the complete name of the name
        #each time.
        complete_names = []
        for complete_name in all_names:
            for partial_name in names:
                if partial_name.lower() in complete_name.lower() and\
                partial_name != '':
                    complete_names.append(complete_name)

        print(complete_names)
        names_disp = ", ".join(complete_names)
        names = complete_names
        print(names_disp)

    shots = db.session.query(models.Shot)\
        .filter(models.Shot.gid.in_(gids))\
        .filter(models.Shot.period.in_(periods))\
        .filter(models.Shot.clock >= clock_min)\
        .filter(models.Shot.clock <= clock_max)\
        .filter(models.Shot.dribbles >= dribbles_min)\
        .filter(models.Shot.dribbles <= dribbles_max)\
        .filter(models.Shot.made.in_(made))\
        .filter(models.Shot.shot_type.in_(shot_type))\
        .filter(models.Shot.name.in_(names)).all()\
    
    gids_from_shots = [s.gid for s in shots] 


    games = db.session.query(models.Game)\
        .filter(models.Game.gid.in_(gids_from_shots)).all()
    print('&&&&&&&&&&&&&&&&&&')
    shotPercentage = percentageForTimeRange(0,0,1200,shots)
    firstHalfShotPercentage = percentageForTimeRange(0,0,600,shots)
    secondHalfShotPercentage= percentageForTimeRange(0,600,1200,shots)
    playerPercentages = percentagePerPlayer(0,shots)
    threePointPercentage = percentageForTimeRange(3,0,1200,shots)
    twoPointPercentage = percentageForTimeRange(2,0,1200,shots)
    playerThreePercentage = percentagePerPlayer(3,shots)
    playerTwoPercentage = percentagePerPlayer(2,shots)
    playerUsage = usagePerPlayer(shots)

    x = [s.x for s in shots]
    y = [s.y for s in shots]
    made =[s.made for s in shots]
    for index in range(0, len(x)-1):
        if x[index] > 47.5: 
            x[index] = 94 - x[index]
            y[index] = 50 - y[index] 
    x,y = y,x

    return render_template('home.html', shots = shots, games = games, 
            gids_disp = gids_disp,
            periods_disp = periods_disp,
            clock_min_disp = clock_min_disp, 
            clock_max_disp = clock_max_disp, 
            dribbles_min_disp = dribbles_min_disp, 
            dribbles_max_disp = dribbles_max_disp, 
            made_disp = made_disp,
            shot_type_disp = shot_type_disp,
            names_disp = names_disp,
            shotPercentage = shotPercentage,
            firstHalfShotPercentage = firstHalfShotPercentage,
            secondHalfShotPercentage = secondHalfShotPercentage,
            playerPercentages = playerPercentages,
            threePointPercentage = threePointPercentage,
            twoPointPercentage = twoPointPercentage,
            playerThreePercentage = playerThreePercentage,
            playerTwoPercentage = playerTwoPercentage,
            playerUsage = playerUsage,
            x=x, y=y, made = made)

def usagePerPlayer(shotList):
    playerDict = {}
    totalshots = len(shotList)
    for s in shotList:
        keys = playerDict.keys()
        if not s.name in keys:
            playerDict[s.name] = 0
        playerDict[s.name]+=1
    percDict = []
    for player in playerDict:
        if(totalshots != 0):
            percDict.append((player, round(playerDict[player]*100/totalshots,1)))
    return percDict

def percentagePerPlayer(shotType,shotList):
    playerDict = {}
    for s in shotList:
        keys = playerDict.keys()
        if (shotType ==0 or s.shot_type==shotType):
            if not s.name in keys:
                playerDict[s.name] = [0,0]
            playerDict[s.name][0]+=1
            playerDict[s.name][1]+=s.made
    percDict = []
    for player in playerDict:
        if(playerDict[player][0] != 0):
            percDict.append((player, round(playerDict[player][1]*100/playerDict[player][0],1)))
    return percDict


def percentageForTimeRange(shotType, timestart, timeend, shotList):
    totalShots =0
    madeShots =0
    for s in shotList:
        if s.clock >= timestart and s.clock <=timeend and (shotType==0 or shotType==s.shot_type):
            totalShots+=1
            if(s.made==1):
                madeShots=madeShots+1
    percShots = 0
    if(totalShots!=0):
        percShots=round((madeShots*100)/(totalShots),1)
    return percShots

def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((25,5.5), radius=0.75, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((22, 4.75), 6, -0.75, linewidth=lw, color=color)

    # The paint
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((19, 0), 12, 20.25, linewidth=lw, color=color,
                          fill=False)

   # Create free throw top arc
    top_free_throw = Arc((25, 20.25), 12, 12, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
  
    # Three point line

    corner_three_a = Rectangle((4.25, 0), 0, 5.5, linewidth=lw,color=color)
    corner_three_b = Rectangle((45.75, 0), 0, 5.5, linewidth=lw, color=color)

    three_arc = Arc((25, 5.5), 41.5,41.5, theta1=0, theta2=180, linewidth=lw,
                    color=color)

    # Center Court
    center_outer_arc = Arc((25, 47), 12, 12, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((25, 47), 4, 4, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard,inner_box, corner_three_a, corner_three_b,top_free_throw, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((0, 0),50, 47, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax



@app.route('/fig/<x>/<y>/<made>')
def fig(x=[],y=[], made=[]):
    x = ast.literal_eval(x)
    y = ast.literal_eval(y)
    made = ast.literal_eval(made)
    print('###############################')
    #print(shots_list)
    # MAKE DATAFRAME
    #df = pd.DataFrame.from_records(shots_list)
    #print(df)
    shot_plot, ax = plt.subplots()
    for i in range(len(x)):
        if made[i] == 1:
            dot = 'b'
        if made[i] == 0:
            dot = 'r'
        ax.scatter(x=x[i],y=y[i],c=dot, s=20)
    draw_court(outer_lines=True)
    # Descending values along the axis from left to right
    ax.set_xlim(-5,55)
    ax.set_ylim(55,-5)
    shot_plot.savefig('shot_plot.png')
    return(mpld3.fig_to_html(shot_plot))

 



from werkzeug.routing import BaseConverter

class ListConverter(BaseConverter):

    def to_python(self, value):
        return value.split(',')

    def to_url(self, values):
        return ','.join(BaseConverter.to_url(value)
                        for value in values)

app.url_map.converters['list'] = ListConverter


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
