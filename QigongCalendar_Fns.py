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
from matplotlib import text as mtext
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder

# local code
from CurvedText import CurvedText
import QigongCalendar_base as QB
import Symbols as sy 

#from https://stackoverflow.com/questions/35771863/how-to-calculate-length-of-string-in-pixels-for-specific-font-and-size
def get_length(text, fontsize, fig):
    
    t = fig.text(0, 0, text, fontsize=fontsize, color='white', alpha=0)
    b=t.get_window_extent()
    #print(b.width, text)    
    return(b.width)

def to_string(*args, **kwargs):
    output = io.StringIO()
    print(*args, file=output,end="", **kwargs)
    contents = output.getvalue()
    output.close()
    return contents


def convertLocalTime(d,lTimeZone):
    tz_local = pytz.timezone(lTimeZone)
    return(d.astimezone(tz_local))   

def LocalTimeNow(lTimeZone):
    return(convertLocalTime(dtdt.now(pytz.timezone('UTC')), lTimeZone))
    

# read data files
SeasonalPoints= pd.read_csv('Seas-export.csv')
lunarCycle= pd.read_csv('lunarCycle.csv')
WeekDays= pd.read_csv('WeekDays.csv')
AcuPoints= pd.read_csv('acqupoints.csv')
PointDescriptions = pd.read_excel('PointDescriptions.xlsx', dtype=str)
PointDescriptions['Point']=PointDescriptions['Point Description'].str[:5].str.strip()
JointRings = pd.read_excel('JointRings.xlsx', dtype=str)
TimePoints=pd.read_csv('timepoints.csv')
TimePoints['pTime']=TimePoints['Time'].apply(lambda x: dtdt.strptime(x, '%H:%M'))
TextSegments0 = pd.read_excel('TextSegments.xlsx', dtype=str)
TextSegments = dict(zip(TextSegments0.KEY,TextSegments0.TEXT))
MeridiansDF = pd.read_excel('Meridians.xlsx', dtype=str)

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
    QS=[0,15,30,45]
    
    # main range around current time
    QH=int(quarterHours)
    H=int(QH/4)
    M=QH-4*H
    
    # code here deals with times near midnight
    time1=dt.datetime(1900,1,1,H,QS[M])-timedelta(hours=1)
    if time1 <= dt.datetime(1900,1,1,0,0):
        time1+=timedelta(hours=24)
    a=TimePoints['pTime']>=time1
    time2=dt.datetime(1900,1,1,H,QS[M])+timedelta(hours=1)
    if time2 >= dt.datetime(1900,1,2,0,0):
        time2-=timedelta(hours=24)
    #print("QH", QH, H, M, time2)
    b=TimePoints['pTime']<=time2
    if time1<time2:
        cR=TimePoints[a & b]
    else:
        cR=TimePoints[a | b]
        ix=cR.index.to_series()
        ixc=ix.where(ix>10,ix+108)
        cR['ix']=ixc
        cR=cR.set_index('ix').sort_index()    
    
    #a=TimePoints['pTime']>dt.datetime(1900,1,1,H,QS[M])-timedelta(hours=1) 
    #b=TimePoints['pTime']<dt.datetime(1900,1,1,H,QS[M])+timedelta(hours=1)
    #cR=TimePoints[a & b]
    
    # range around 12 hour shifted time
    QHp=QH+48
    if QHp>96:
        QHp-=96
    Hp=int(QHp/4)
    Mp=QHp-4*Hp
    if Hp==24:
        Hp=0
    #print("QHp", QHp, Hp, Mp)
    time1=dt.datetime(1900,1,1,Hp,QS[Mp])-timedelta(hours=1)
    if time1 <= dt.datetime(1900,1,1,0,0):
        time1+=timedelta(hours=24)
    c=TimePoints['pTime']>=time1
    time2=dt.datetime(1900,1,1,Hp,QS[Mp])+timedelta(hours=1)
    if time2 >= dt.datetime(1900,1,2,0,0):
        time2-=timedelta(hours=24)
    #print("QHp", QHp, Hp, Mp, time2)
    d=TimePoints['pTime']<=time2
    if time1<time2:
        cRp=TimePoints[c & d]
    else:
        cRp=TimePoints[c | d]
        ix=cRp.index.to_series().copy()
        ixc=ix.where(ix>10,ix+108)
        cRp['ix']=ixc.copy()
        cRp=cRp.set_index('ix').sort_index()
        
    return(cR, cRp)


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
    seasWeek=int((dtdt.today()-seasStart)/seasDaysWeek)+1
    nextSeasWeek=seasStart+seasWeek*seasDaysWeek
    if nFlag==None:
        return(seasWeek) #, nextSeasWeek)
    else:
        return(seasWeek, nextSeasWeek)

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
               [(0,-10),135], [(-61,45),70], [(61,45),70],  [(61,77),70],[(-61,77),70], [(-61,110),70], [(61,110),70]]
                #  [(0,30),135],
    #locIdx=13
    ellipse=Ellipse(positions[locIdx][0], width=positions[locIdx][1], height=40, edgecolor='r', fill=None, linewidth=3, angle=0)
    ax.add_patch(ellipse)    
    plt.axis('off')
    return(plt)
        
def writeClock(wAngle, radius, text, ax, *args, **kwargs):

    N = 100
    decAngle=wAngle/360
    curve = [
            -np.cos(np.pi/2+decAngle*2*np.pi+np.linspace(0,np.pi,N))*radius,
             np.sin(np.pi/2+decAngle*2*np.pi+np.linspace(0,np.pi,N))*radius
        ]
        
    #adding the text
    text = CurvedText(
        x = curve[0],
        y = curve[1],
        text=text,#'this this is a very, very long text',
        va = 'bottom',
        axes = ax, ##calls ax.add_artist in __init__
        *args,
        **kwargs
        )

# returns matched pie wedges
# angle system, center is (0,0), angle is relative to vertical, clockwise rotation
def pieWedge(loc=(0,0), radius=2, width=1, absStartAngle=0, relEndAngle=180, virtRelStartAngle=0, 
            virtSizeAngle=180, startClose=True, color1='green', color2='red', alpha1=1, alpha2=1,
            linewidth1=1, linewidth2=1):
    
    import numpy as np
    from numpy import pi
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Polygon

    startDec=-virtRelStartAngle/virtSizeAngle
    endDec=(-virtRelStartAngle+relEndAngle)/virtSizeAngle

    basePts=100

    angPts=int(basePts*radius*virtSizeAngle/360)
    
    arc=np.linspace((absStartAngle)/360*2*pi,(absStartAngle+relEndAngle)/360*2*pi,angPts)
    lin=np.linspace(0,1,angPts)
    
    x0=(radius-width)*np.sin(arc)
    y0=(radius-width)*np.cos(arc)

    x1=radius*np.sin(arc)
    y1=radius*np.cos(arc)

    inSide=np.vstack((x0,y0)).T
    outSide=np.vstack((x1,y1)).T
    
    # standard position is startClose=True
    if startClose==True:
        xtA=((radius-width)+(startDec+(endDec-startDec)*lin)*width)*np.sin(arc)
        ytA=((radius-width)+(startDec+(endDec-startDec)*lin)*width)*np.cos(arc)
        transSideA=np.flipud(np.vstack((xtA,ytA)).T)
        pieShape1=np.concatenate((transSideA, outSide))
        pieShape2=np.concatenate((inSide, transSideA))
    else:
        xtB=((radius-width)+(startDec+(endDec-startDec)*(1-lin))*width)*np.sin(arc)
        ytB=((radius-width)+(startDec+(endDec-startDec)*(1-lin))*width)*np.cos(arc)
        transSideB=np.flipud(np.vstack((xtB,ytB)).T)
        pieShape1=np.concatenate((outSide,transSideB))
        pieShape2=np.concatenate((inSide,transSideB))
    
    pie1=Polygon(pieShape1, closed=True, edgecolor='black', linewidth=linewidth1, ec='black', fc=color1, alpha=alpha1) #, 
    pie2=Polygon(pieShape2, closed=True, edgecolor='black', linewidth=linewidth2, ec='black', fc=color2, alpha=alpha2) #, 
    return(pie1, pie2)
