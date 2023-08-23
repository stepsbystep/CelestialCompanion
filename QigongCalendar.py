# to-do items:
#  - Add head locations (besides cervical) to vertical column graphical objects
#  - Day of week chakra on top of mind page
#  - Chakra description expander?
#  - permissions for point descriptions and body images
#  - heart and lung images?
#  - change face order to start with jaw ... then ears, eyes, nose

import pandas as pd
import io
import pytz
from streamlit_javascript import st_javascript
from backports.zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import ephem
import datetime as dt
from datetime import datetime as dtdt
from streamlit_js_eval import get_geolocation

import QigongCalendar_base as QB

def to_string(*args, **kwargs):
    output = io.StringIO()
    print(*args, file=output,end="", **kwargs)
    contents = output.getvalue()
    output.close()
    return contents

import datetime as dt
from datetime import datetime as dtdt

def convertLocalTime(d,lTimeZone):
    tz_local = pytz.timezone(lTimeZone)
    return(d.astimezone(tz_local))   

def LocalTimeNow(lTimeZone):
    return(convertLocalTime(dtdt.now(pytz.timezone('UTC')), lTimeZone))
    
DaysOfTheWeek=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']

# note short days of the week start with Monday to correspond to the weekday() method for datetitme!
ShortDaysOfTheWeek=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

seasons_big_list=['winter_solstice_last', 'vernal_equinox', 'summer_solstice', 'autumnal_equinox', 'winter_solstice', 'vernal_equinox_next']
seasons4=['Spring','Summer','Fall','Winter']

# read data files
SeasonalPoints= pd.read_csv('Seas-export.csv')
lunarCycle= pd.read_csv('lunarCycle.csv')
WeekDays= pd.read_csv('WeekDays.csv')
AcuPoints= pd.read_csv('acqupoints.csv')
PointDescriptions = pd.read_excel('PointDescriptions.xlsx', dtype=str)
PointDescriptions['Point']=PointDescriptions['Point Description'].str[:5].str.strip()
TimePoints=pd.read_csv('timepoints.csv')
TimePoints['pTime']=TimePoints['Time'].apply(lambda x: dtdt.strptime(x, '%H:%M'))


# need to calculate dayOftheWeek outside this function!
def dayOfTheWeekNum(lTimeZone):
    dw=LocalTimeNow(lTimeZone).isoweekday()
    if dw==7:
        dw=0
    return(dw)

def thisWeekDay(lTimeZone):
    return(WeekDays.loc[dayOfTheWeekNum(lTimeZone)])

def dayOfTheWeek(lTimeZone):
    return DaysOfTheWeek[dayOfTheWeekNum(lTimeZone)]

def todaysPoint(lTimeZone):
    d=LocalTimeNow(lTimeZone)
    dayOfYear=(dt.datetime(d.year,d.month,d.day)-dt.datetime(d.year-1,12,31)).days
    return(AcuPoints.loc[dayOfYear])

VerticalColumn= pd.read_csv('VerticalColumn.csv')

def todayVerticalColumn(lTimeZone):
    dayIndex=LocalTimeNow(lTimeZone).day-1
    return(VerticalColumn.loc[dayIndex][1])

def nowPoints(localTimeZone):
    # getting the current time points
    d=LocalTimeNow(localTimeZone)
    decHours=(dt.datetime(d.year,d.month,d.day,d.hour,d.minute, 0)-dt.datetime(d.year,d.month,d.day,0,0,0)).seconds/3600
    quarterHours=decHours/.25
    QH=int(quarterHours)
    H=int(QH/4)
    M=QH-4*H
    QS=[0,15,30,45]
    return(TimePoints[TimePoints['pTime']==dt.datetime(1900,1,1,H,QS[M])])

def clockRange(localTimeZone):
    # getting the current time points
    d=LocalTimeNow(localTimeZone)
    decHours=(dt.datetime(d.year,d.month,d.day,d.hour,d.minute, 0)-dt.datetime(d.year,d.month,d.day,0,0,0)).seconds/3600
    quarterHours=decHours/.25
    QH=int(quarterHours)
    H=int(QH/4)
    M=QH-4*H
    QS=[0,15,30,45]
    a=TimePoints['pTime']>dt.datetime(1900,1,1,H,QS[M])-timedelta(hours=1) 
    b=TimePoints['pTime']<dt.datetime(1900,1,1,H,QS[M])+timedelta(hours=1)
    cR=TimePoints[a & b]
    return(cR)

def todaysMoon():
    # position of moon in 30 day transit lunar month
    # stuck now on Chicago time!
    import ephem
    Chicago = ephem.city("Chicago")
    lastMoon=ephem.localtime(ephem.previous_new_moon(Chicago.date))
    nextMoon=ephem.localtime(ephem.next_new_moon(Chicago.date))
    length_Moon=nextMoon-lastMoon
    lengthLunzDay=(length_Moon)/30
    moonPos=int((dt.datetime.now()-lastMoon)/lengthLunzDay)
    nextPosDate=lastMoon+moonPos*lengthLunzDay
    #lunar cycle
    return(lunarCycle.loc[moonPos],nextMoon)

def get_seasons(year):
    import ephem
    import datetime as dt
    dates= []
    date = ephem.Date(dt.datetime(year-1,1,1))
    dates.append(ephem.next_winter_solstice(date))
    date = ephem.Date(dt.datetime(year,1,1))    
    dates.append(ephem.next_vernal_equinox(date))
    dates.append(ephem.next_summer_solstice(dates[1]))
    dates.append(ephem.next_autumnal_equinox(dates[2]))
    dates.append(ephem.next_winter_solstice(dates[3]))
    dates.append(ephem.next_vernal_equinox(dates[4]))
    return(dates)

def seasonNum():
    import ephem
    seasons=get_seasons(dtdt.today().year)
    for i in range(1,len(seasons)):
        if ephem.Date(dtdt.today())<seasons[i]:
            return(i-1)

def getSeasWeek(nFlag=None):
    import ephem
    seasons=get_seasons(dtdt.today().year)
    seasStart=ephem.localtime(seasons[seasonNum()])
    seasEnd=ephem.localtime(seasons[seasonNum()+1])
    seasDaysWeek=(seasEnd-seasStart)/13
    seasWeek=int((dtdt.today()-seasStart)/seasDaysWeek)
    nextSeasWeek=seasStart+(seasWeek+1)*seasDaysWeek
    if nFlag==None:
        return(seasWeek) #, nextSeasWeek)
    else:
        return(seasWeek, nextSeasWeek)

def BodyChart(SunRing, MoonRing, lTimeZone,  nowP, TP, tVC, sunPoint):
    from matplotlib import pyplot as plt
    from matplotlib.patches import Ellipse as Ellipse
    from matplotlib.figure import Figure
    
    #plt.rcParams["figure.autolayout"] = True
    if TP['Point'] not in ['TW-1', 'TW-2', 'TW-3', 'TW-4', 'TW-5', 'TW-6', 'TW-7', 'TW-8', 'TW-9']:
        bodies = plt.imread("images/FrontAndBack.png")
    else:
        bodies = plt.imread("images/FrontAndBack2.png")

    fig = Figure(figsize=(5.0,7.50))
    ax = fig.subplots()   

    im = ax.imshow(bodies, extent=[-100, 100,-125, 125])        

    dayRings = {
        0 : ['LA', 'RA'],
        1 : ['LK', 'RK'],
        2 : ['LH', 'RH'],
        3 : ['VC'],
        4 : ['LS', 'RS'],
        5 : ['LE', 'RE'],
        6 : ['LW', 'RW'],
    }

    # do joint rings
    dayOfWeek=dayOfTheWeekNum(lTimeZone)
    dayRing=dayRings[dayOfTheWeekNum(lTimeZone)]    
    for ring in dayRing:
        JJJ=QB.jointPOS[ring]
        joint1=Ellipse(JJJ[0], width=JJJ[1], height=JJJ[2], edgecolor='lightgreen', linewidth=4, fill=None) #, facecolor=None) #,alpha=0.65) 
        ax.add_patch(joint1) 
        joint1=Ellipse(JJJ[0], width=JJJ[1], height=JJJ[2], edgecolor='black', linewidth=0.5, fill=None) #, facecolor=None) #,alpha=0.65) 
        ax.add_patch(joint1) 

    # check for overlap
    MoveSun=0
    MoveMoon=0
    if SunRing==MoonRing:
        MoveSun=+5
        MoveMoon=-5
    elif SunRing in dayRing:
        MoveSun=+5
    elif MoonRing in dayRing:
        MoveMoon=-5
        
    # add Moon position
    moonP=QB.jointPOS[MoonRing] 
    moon=Ellipse((moonP[0][0]+MoveMoon,moonP[0][1]), width=moonP[1], height=moonP[2], edgecolor='blue', linewidth=4, facecolor='purple',alpha=0.4) 
    ax.add_patch(moon) 
    moon=Ellipse((moonP[0][0]+MoveMoon,moonP[0][1]), width=moonP[1], height=moonP[2], edgecolor='black', linewidth=0.5, fill=None) 
    ax.add_patch(moon) 

    # add Sun position
    sunP=QB.jointPOS[SunRing] 
    sun=Ellipse((sunP[0][0]+MoveSun,sunP[0][1]), width=sunP[1], height=sunP[2], edgecolor='red', linewidth=4, facecolor='orange',alpha=0.65) 
    ax.add_patch(sun) 
    sun=Ellipse((sunP[0][0]+MoveSun,sunP[0][1]), width=sunP[1], height=sunP[2], edgecolor='black', linewidth=0.5, fill=None) 
    ax.add_patch(sun) 
    
    vAlign=120
    ax.text(-100, vAlign, to_string(f"At {nowP.iloc[0]['Time']}"), fontsize=10)    
    
    # add time points
    #nowP=nowPoints(lTimeZone)
    #print(f"number of points: {len(nowP)}")
    for i in range(0, len(nowP)):
        # can be two time points
        # try because not all points are done yet
        #if True:
        try:
            pKey=nowP.iloc[i]['Point']
            RRR=QB.pointPOS[pKey] 
            # time point
            tp=Ellipse(RRR[0], width=RRR[1], height=RRR[2], edgecolor='black', linewidth=0.5, facecolor='red')#  fill=None) 
            ax.add_patch(tp)
            # surrounding 
            tp=Ellipse(RRR[0], width=15, height=15, edgecolor='green', linewidth=1, fill=None) 
            ax.add_patch(tp)
            # arrow to time point ... take out for now
            #ax.arrow(RRR[0][0]+RRR[3]*15, RRR[0][1]+RRR[4]*15,-RRR[3]*5,-RRR[4]*5,  head_width=2.5, head_length=10, fc='k', ec='k')
            vAlign-=9
            ax.text(-100, vAlign, to_string(f"{nowP.iloc[i]['Point']}:"), fontsize=10)
            vAlign-=7
            ax.text(-100, vAlign, to_string(f"{nowP.iloc[i]['English Name']}"), fontsize=10)
            #print(f"Code executed for point {pKey}")
        except:
            #print("Error")
            #print(pKey)
            pass

    # spine correction
    spineCOR=0
    
    # chakras!
    for i in range(0,len(QB.chakraPOS)):
        if i == dayOfWeek:
            chakraColor='gold'
            cWidth=5
            cHeight=5
            cAlpha=1
            cThick=5
        else:
            chakraColor='yellow'
            cWidth=2.5
            cHeight=2.5
            cAlpha=.5
            cThick=2
        for j in range(0, len(QB.chakraPOS[i])):
            RRR=QB.chakraPOS[i][j]
            if i == dayOfWeek:
                tp=Ellipse((RRR[0][0]+spineCOR,RRR[0][1]), width=10, height=10, color=chakraColor,  alpha=.35)  
                ax.add_patch(tp)
                tp=Ellipse((RRR[0][0]+spineCOR,RRR[0][1]), width=15, height=15, color=chakraColor,  alpha=.20)  
                ax.add_patch(tp)
                #ax.arrow(RRR[0][0]+RRR[3]*30, RRR[0][1]+RRR[4]*30,-RRR[3]*20,-RRR[4]*20,  head_width=2.5, head_length=10, fc='k', ec='k')
            tp=Ellipse((RRR[0][0]+spineCOR,RRR[0][1]), width=cWidth, height=cHeight, edgecolor='black', linewidth=0.5, facecolor=chakraColor, alpha=cAlpha) 
            ax.add_patch(tp)

    chakras=WeekDays['Chakra']
    tChakra=chakras.iloc[dayOfWeek]
    ax.text(-100, -30, to_string(f"Chakra:"), fontsize=10)
    ax.text(-100, -37, to_string(f"{tChakra}"), fontsize=10)

    # today's vertical column focus
    try:
        for RRR in QB.vcPOS[tVC]:
            #RRR=QB.vcPOS[tVC][0]
            tp=Ellipse((RRR[0][0]+spineCOR,RRR[0][1]), width=RRR[1], height=RRR[2], edgecolor='black', linewidth=0.5, facecolor='gold') 
            ax.add_patch(tp)
        #ax.arrow(RRR[0][0]+RRR[3]*30, RRR[0][1]+RRR[4]*30,-RRR[3]*20,-RRR[4]*20,  head_width=2.5, head_length=10, fc='k', ec='k')
    except:
        pass
    
    ax.text(-100, -50, to_string(f"Vertical column:"), fontsize=10)
    ax.text(-100, -57, to_string(f"{tVC}"), fontsize=10)
    
    # today's point
    try:
        RRR=QB.pointPOS[TP['Point']]
        ax.scatter(RRR[0][0], RRR[0][1], s=300, marker='*', facecolor='gold', edgecolor='black', linewidth=0.5) 
    except:
        pass

    # facial focus
    facialFoci=WeekDays['Face']
    tFacial=facialFoci.iloc[dayOfWeek]
    ax.text(-100, -70, to_string(f"Face:"), fontsize=10)
    ax.text(-100, -77, to_string(f"{tFacial}"), fontsize=10)

    RRR = QB.facialPOS[tFacial]
    tp=Ellipse((RRR[0][0]+spineCOR,RRR[0][1]), width=RRR[1], height=RRR[2], edgecolor='black', linewidth=1, facecolor='orange', alpha=0.7) 
    ax.add_patch(tp)    

    # sun point
    try:
        #print(sunPoint)
        RRR=QB.pointPOS[sunPoint]
        ax.scatter(RRR[0][0], RRR[0][1], s=150, marker='*', facecolor='gold', edgecolor='red', linewidth=0.5) 
    except:
        pass
    
    
    ax.text(-100, -7, to_string(f"Today"), fontsize=13)
    ax.text(-100, -17, to_string(f"Point: {TP['Point']}"), fontsize=10)

    # more time points
    lowSeq=nowP['Seq'].min()-1
    highSeq=nowP['Seq'].max()+1
    if lowSeq<1:
        lowSeq=108
    if highSeq>108:
        highSeq=1
    higherSeq=highSeq+1
    if higherSeq>108:
        higherSeq=1
        
    # anti-points!
    Anti=nowP.iloc[0]['Seq']+54
    Anti2=0
    if len(nowP)>1:
        Anti2=nowP.iloc[1]['Seq']+54
    lowAnti=lowSeq+54
    highAnti=highSeq+54
    higherAnti=higherSeq+54
    if Anti>108:
        Anti-=108
    if Anti2>108:
        Anti2-=108
    if lowAnti>108:
        lowAnti-=108
    if highAnti>108:
        highAnti-=108
    if higherAnti>108:
        higherAnti-=108
    
    lowP=TimePoints[TimePoints['Seq']==lowSeq]
    highP=TimePoints[TimePoints['Seq']==highSeq]
    higherP=TimePoints[TimePoints['Seq']==higherSeq]

    nowA=TimePoints[TimePoints['Seq']==Anti]
    nA=[nowA]
    counterString="Counterpoint: "
    if Anti2>0:
        nowA2=TimePoints[TimePoints['Seq']==Anti2]
        nA.append(nowA2)
        counterString="Counterpoints: "
    lowA=TimePoints[TimePoints['Seq']==lowAnti]
    highA=TimePoints[TimePoints['Seq']==highAnti]
    higherA=TimePoints[TimePoints['Seq']==higherAnti]
    nowA=TimePoints[TimePoints['Seq']==Anti]
    
    vAlign-=20
    ax.text(-100, vAlign, to_string(f"{counterString}"), fontsize=10)
    vAlign-=7
    ax.text(-100, vAlign, to_string(f"{nA[0].iloc[0]['Point']}"), fontsize=10)
    if Anti2>0:
        vAlign-=7
        ax.text(-100, vAlign, to_string(f"{nA[1].iloc[0]['Point']}"), fontsize=10)
    
    for Pt in [lowP, highP, higherP]:
        try:
            pKey=Pt.iloc[0]['Point']
            RRR=QB.pointPOS[pKey] 
            tp=Ellipse(RRR[0], width=3.5, height=3.5, edgecolor='black', facecolor='yellow', linewidth=0.5)
            ax.add_patch(tp)
        except:
            pass

    # main counterpoint(s)
    for Pt in nA:
        try:
            pKey=Pt.iloc[0]['Point']
            RRR=QB.pointPOS[pKey] 
            tp=Ellipse(RRR[0], width=3, height=3, edgecolor='black', facecolor='orange', linewidth=0.5) #, fill=None) 
            ax.add_patch(tp)
        except:
            pass
    
    # surrounding counterpoints
    for Pt, color, diam in zip([lowA, highA, higherA],['lightgrey','lightgrey','lightgrey'], [2.5, 2.5, 2.5]):
        try:
            pKey=Pt.iloc[0]['Point']
            RRR=QB.pointPOS[pKey] 
            tp=Ellipse(RRR[0], width=diam, height=diam, edgecolor='black', facecolor=color, linewidth=0.5) #, fill=None) 
            ax.add_patch(tp)
        except:
            pass
    
    import numpy as np
    np.vectorize(lambda ax:ax.axis('off'))(ax)
    return(fig)
    

def lunarCyclePlot(locIdx):
    from matplotlib import pyplot as plt
    from matplotlib.patches import Ellipse as Ellipse
    
    im = plt.imread("images/lunarCycle.png")
    fig, ax = plt.subplots()
    im = ax.imshow(im, extent=[-100, 100,-125, 125])

    ellipse=Ellipse(QB.moonPOS[locIdx][0], width=QB.moonPOS[locIdx][1], height=20, edgecolor='r', fill=None, linewidth=2, angle=0)
    ax.add_patch(ellipse)    
    plt.axis('off')
    return(fig)

def solarCyclePlot(locIdx):
    from matplotlib import pyplot as plt 
    from matplotlib.patches import Ellipse as Ellipse
    
    #plt.rcParams["figure.figsize"] = [5, 10]
    plt.rcParams["figure.autolayout"] = True
    im = plt.imread("images/solarCycle.png")
    fig, ax = plt.subplots()
    xFac=.8
    fig.set_size_inches(xFac*5,5)
    im = ax.imshow(im, extent=[xFac*-125, xFac*125, -125, 125])
    positions=[[(-45,-104),90],[(45,-104),90], [(45,-74),90],[(-45,-74),90],[(-45,-38),90], [(45,-38),90],
               [(0,-10),135], [(0,30),135],  [(-61,45),70], [(61,45),70],  [(61,77),70],[(-61,77),70], [(-61,110),70], [(61,110),70]]
    #locIdx=13
    ellipse=Ellipse(positions[locIdx][0], width=positions[locIdx][1], height=40, edgecolor='r', fill=None, linewidth=3, angle=0)
    ax.add_patch(ellipse)    
    plt.axis('off')
    return(plt)


from datetime import datetime, timedelta

# get lat/long to be able to update celectial data locally
#import geocoder
#g = geocoder.ip('me')
#print(g.latlng)
#----


MoonPhases={'NM' : 'New Moon', 'FM' : 'Full Moon', 'WG' : 'Waning Gibbous', 'XG' : 'Waxing Gibbous', 'FQ' : 'First Quarter',   
            'LQ' : 'Last Quarter', 'WC' : 'Waning Cresent', 'XC' : 'Waxing Crescent'}
Meridians={'LV' : 'Liver', 'LU' : 'Lungs', 'LI' : 'Large Intestine', 'ST' : 'Stomach', 'SP' : 'Spleen', 
           'HT' : 'Heart', 'SI' : 'Small Intestine', 'BL' : 'Bladder', 'KI' : 'Kidney', 'PC' : 'Pericardium',
           'TW' : 'Triple Warmer', 'GB' : 'Gall Bladder', 'CV' : 'Conception Vessel', 'GV' : 'Governing Vessel', 'DS' : 'Dan Tians'}
MainJoints={'RA' : 'Right Ankle', 'LA' : 'Left Ankle', 'LK' : 'Left Knee', 'RK' : 'Right Knee', 
            'LH' : 'Left Hip', 'RH' : 'Right Hip', 'LS' : 'Left Shoulder', 'RS' : 'Right Shoulder',
            'LE' : 'Left Elbow', 'RE' : 'Right Elbow', 'LW' : 'Left Wrist', 'RW': 'Right Wrist',
            'D1' : 'Lower Dan Tian', 'D2' : 'Middle Dan Tian', 'D3' : 'Upper Dain Tian'}
MeridianList=['LU','LI','ST','SP','HT','SI','BL','KI','PC','TW','BG','LV','CV','GV', 'DS']
sunJointList =['LA', 'RA', 'RK', 'LK', 'LH', 'RH', 'D1', 'D2', 'LS', 'RS', 'RE', 'LE', 'LW', 'RW']

def main():    
    import streamlit as st
    import time

    # https://discuss.streamlit.io/t/determine-users-local-timezone/24074/2
    # returns in IANA timezone format https://stackoverflow.com/questions/6939685/get-client-time-zone-from-browser
    localTimeZone = st_javascript("""await (async () => {
            const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            console.log(userTimezone)
            return userTimezone
            })().then(returnValue => returnValue)""")
    
    if type(localTimeZone) != str:
        print(f"local time zone type: {type(localTimeZone)}, localTimeZone: {localTimeZone}")
        localTimeZone='America/Chicago'
        
    # https://discuss.streamlit.io/t/streamlit-geolocation/30796
    # https://github.com/aghasemi/streamlit_js_eval/tree/master
    # aghasemi Alireza Ghasemi
    location=get_geolocation()
    if location != None:
        localLat=location['coords']['latitude']
        localLong=location['coords']['longitude']
    else:
        localLat='46'
        localLong='-80'

    st.markdown(
        """
            <style>
                .appview-container .main .block-container {{
                    padding-top: {padding_top}rem;
                    padding-bottom: {padding_bottom}rem;
                    }}

            </style>""".format(
            padding_top=0, padding_bottom=20
            ),
        unsafe_allow_html=True,
        )

    st.title("EZ Qigong Companion")

    TAB1, TAB3, TAB8, TAB4, TAB5, TAB6, TAB7 = st.tabs(["Top of Mind", "Weekly", "Body", "Solar", "Lunar", "Tables", "About" ])
    
    with TAB1:
        PlaceHolder1a=st.empty()
        PlaceHolder1b=st.empty()
    with TAB3:
        PlaceHolder3=st.empty()
    with TAB8:
        PlaceHolder8=st.empty()
    with TAB4:
        PlaceHolder4=st.empty()
    with TAB5:
        PlaceHolder5=st.empty()
    with TAB6:
        PlaceHolder6=st.empty()
    with TAB7:
        PlaceHolder7=st.empty()
    
    # done in the time loop at the end of TAB1
    #with TAB2:

    with TAB3:
        with PlaceHolder3.container():
            st.write('''<style>
                [data-testid="column"] {
                    width: calc(16.6666% - 1rem) !important;
                    flex: 1 1 calc(16.6666% - 1rem) !important;
                    min-width: calc(16.6666% - 1rem) !important;
                }
                </style>''', unsafe_allow_html=True)
            st.header(f"{DaysOfTheWeek[dayOfTheWeekNum(localTimeZone)]} practice foci")
            i=0
            tab=thisWeekDay(localTimeZone)
            for focus in tab:
                if i==0:
                    i+=1
                    continue
                COL1, COL2 = st.columns([.3,.7])
                with COL1:
                    st.markdown(f"{tab.index[i]}:")
                with COL2:
                    st.markdown(f"**{focus}**")
                i+=1

    with TAB4:
        PlaceHolder4.empty()
        with PlaceHolder4:
            SunPos=SeasonalPoints[(SeasonalPoints.Season==seasons4[seasonNum()-1]) & (SeasonalPoints.Week==getSeasWeek())].iloc[0]
            st.pyplot(solarCyclePlot(SunPos.Week-1))
            
    with TAB5:
        PlaceHolder5.empty()
        with PlaceHolder5:
            tM, nxtM=todaysMoon()
            st.pyplot(lunarCyclePlot(tM.Day-1))

    with TAB6:
        PlaceHolder6.empty()
        with PlaceHolder6:

            ZTAB1, ZTAB2, ZTAB3, ZTAB4, ZTAB5 = st.tabs(["Time Points", "Vertical Column", "Days of Week", "Acupuncture Points", "Point Descriptions"])
    
            with ZTAB1:
                PlaceHolderZ1=st.empty()
            with ZTAB2:
                PlaceHolderZ2=st.empty()
            with ZTAB3:
                PlaceHolderZ3=st.empty()
            with ZTAB4:
                PlaceHolderZ4=st.empty()
            with ZTAB5:
                PlaceHolderZ5=st.empty()
            
            with ZTAB1:
                PlaceHolderZ1.empty()
                st.markdown(" ")
                st.dataframe(TimePoints)

            with ZTAB2:
                PlaceHolderZ2.empty()
                st.markdown(" ") 
                st.dataframe(VerticalColumn)
                                
            with ZTAB3:
                PlaceHolderZ3.empty()
                st.markdown(" ") 
                st.dataframe(WeekDays)
                
            with ZTAB4:
                PlaceHolderZ4.empty()
                st.markdown(" ") 
                st.dataframe(AcuPoints)            

            with ZTAB5:
                PlaceHolderZ5.empty()
                st.markdown(" ") 
                st.dataframe(PointDescriptions)


    with TAB7:
        PlaceHolder7.empty()
        #st.markdown(f"User time zone: {localTimeZone}.")
        #st.markdown(f"User provided location: {localLat} latitude, {localLong} longitude.")
        st.write("Qigong Companion is distributed to the web using [Streamlit](https://streamlit.io), an open-source [Python](https://www.python.org/) package. Celestial times are calcuated in Python with [PyEphem](https://rhodesmill.org/pyephem/index.html), another open-source Python pacakge. Rising and setting times are approximate, based on the latitude and longitude returned from the request to the user's browser or on PyEphem's Chicago coordinates.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/1/19/Solar_System_true_color.jpg",caption="Source: Wikipedia")

    # ***** #
    #with TAB8:
    #    PlaceHolder8.empty()
    #    with PlaceHolder8:
    #        #tM, nxtM=BodyChart()
    #        st.pyplot(BodyChart(SunRing, MoonRing, localTimeZone))
        

    lastQH=-1
    while True==True:
        with TAB1:
            PlaceHolder1a.empty()
            with PlaceHolder1a.container():
                d=LocalTimeNow(localTimeZone)
                st.header(f"{DaysOfTheWeek[dayOfTheWeekNum(localTimeZone)]}, {d.strftime('%B')} {d.day}, {d.strftime('%H:%M')}")

            # track quarter hours
            qH=int(d.minute/15)            
            if qH != lastQH:
                PlaceHolder1b.empty()
                with PlaceHolder1b.container():
                
                    nowP=nowPoints(localTimeZone)
                    COL1, COL2 = st.columns([.5,.5])
                    with COL1:
                        st.subheader(f"Meridian Clock at {nowP.iloc[0]['Time']}:")
                    with COL2:
                        st.subheader(f"{nowP.iloc[0]['Point']} - {nowP.iloc[0]['English Name']}", help=f"Chinese name: {nowP.iloc[0]['Chinese Name'].title()}")
                        if len(nowP)>1:
                            st.subheader(f"{nowP.iloc[1]['Point']} - {nowP.iloc[1]['English Name']}", help=f"Chinese name: {nowP.iloc[1]['Chinese Name'].title()}")
                    TP=todaysPoint(localTimeZone)
                    tDesc=PointDescriptions[TP['Point']==PointDescriptions['Point']]
                    tDesc=tDesc['Point Description'].values 
                    st.subheader(f"Daily Point: {TP['Point']} - {TP['English']}", help=f"Chinese name: {to_string(TP['Pinyin']).title()}")
                    tVC=todayVerticalColumn(localTimeZone)
                    st.subheader(f"Vertical Column focus: {tVC}")
                    SunPos=SeasonalPoints[(SeasonalPoints.Season==seasons4[seasonNum()-1]) & (SeasonalPoints.Week==getSeasWeek())].iloc[0]
                    tS,nxtS=getSeasWeek(True)
                    SunRing=sunJointList[SunPos.Week-1]
                    sunPoint=SunPos.Meridian+'-'+to_string(SunPos.Point)
                    st.subheader(f"Sun: {seasons4[seasonNum()-1]}, {MainJoints[SunRing]}, {Meridians[MeridianList[SunPos.Week-1]]} meridian, Seasonal Point {sunPoint}, Week {SunPos.Week}", help=f"Next sun transition {nxtS.strftime('%B')} {nxtS.day}, {nxtS.strftime('%H:%M')}.")
                    tM,nxtM=todaysMoon()
                    MoonRing=tM.JointRing
                    st.subheader(f"Moon: {MainJoints[MoonRing]},  {Meridians[tM['Meridian']]} meridian, {MoonPhases[tM['Moon Phase']]}", help=f"It has been {tM.Day} days since new moon, next moon trasition: {nxtM.strftime('%B')} {nxtM.day}, {nxtM.strftime('%H:%M')}.")
                    st.divider()
                    with st.expander("Click for daily point description ..."):
                        st.markdown(f"{tDesc[0]}")
                
                    t1Desc=['']
                    t2Desc=['']
                    t1Desc=PointDescriptions[nowP.iloc[0]['Point']==PointDescriptions['Point']]
                    t1Desc=t1Desc['Point Description'].values 
                    if len(nowP)>1:
                        t2Desc=PointDescriptions[nowP.iloc[1]['Point']==PointDescriptions['Point']]
                        t2Desc=t2Desc['Point Description'].values 

                    with st.expander("Click for time point(s) description(s) ..."):
                        st.markdown(f"{t1Desc[0]}")
                        if len(nowP)>1:
                            st.markdown(f"{t2Desc[0]}")

        if qH != lastQH:
            with TAB8:  
                #PlaceHolder8.empty()
                with PlaceHolder8.container():
                    st.pyplot(BodyChart(SunRing, MoonRing, localTimeZone, nowP, TP, tVC, sunPoint))
                    st.divider()
                    st.subheader(f"Meridian Clock around {d.strftime('%H:%M')}")
                    timeDF=clockRange(localTimeZone)
                    timeDF=timeDF.drop(columns=['Seq', 'pTime'])
                    st.dataframe(timeDF)
                    st.divider()
                
        lastQH=qH
                
        time.sleep(5)

if __name__ == '__main__':
    main()        

