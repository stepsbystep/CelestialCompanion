import pandas as pd
import io
import pytz
import matplotlib
from backports.zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import ephem
import datetime as dt
from datetime import datetime as dtdt
import re
from geopy.geocoders import Nominatim
import warnings

DaysOfTheWeek=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
ShortDaysOfTheWeek=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

def to_string(*args, **kwargs):
    output = io.StringIO()
    print(*args, file=output,end="", **kwargs)
    contents = output.getvalue()
    output.close()
    return contents

def dayOfTheWeekNum(lTimeZone):
    dw=LocalTimeNow(lTimeZone).isoweekday()
    if dw==7:
        dw=0
    return(dw)
 
def dayOfTheWeek(lTimeZone):
    return DaysOfTheWeek[dayOfTheWeekNum(lTimeZone)]

def dayOfTheWeek():
    return DaysOfTheWeek[dayOfTheWeekNum()]

def convertLocalTime(d,lTimeZone):
    try:
        tz_local = pytz.timezone(lTimeZone)
        lt=d.astimezone(tz_local)
    except:
        lt=d
    return(lt)   

def LocalTimeNow(lTimeZone):
    try:
        cDateTime=convertLocalTime(dtdt.now(pytz.timezone('UTC')), lTimeZone)
    except:
        cDateTime=dtdt.now()
    return(cDateTime)
    
def Celestial(lTimeZone, lat=0, long=0):

    from datetime import datetime, timedelta, timezone
    
    if lat != 0:
        LOC = ephem.Observer()
        try:
            LOC.lon = to_string(long)
            LOC.lat = to_string(lat)
        except:
            LOC = ephem.city("Chicago")
    else:
        LOC = ephem.city("Chicago")
        
    # compute next and previous risings and settings relative to 5 am local time
    LTN=LocalTimeNow(lTimeZone)
    localMorning=datetime(LTN.year,LTN.month,LTN.day,5)
        
    sun = ephem.Sun()
    moon = ephem.Moon()
    mars= ephem.Mars()
    venus= ephem.Venus()
    mercury=ephem.Mercury()
    jupiter=ephem.Jupiter()
    saturn=ephem.Saturn()
    uranus=ephem.Uranus()
    neptune=ephem.Neptune()
    pluto=ephem.Pluto()
    CelObjs=[sun,moon,mercury,venus,mars,jupiter,saturn,uranus,neptune,pluto]
    CelNames=['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']

    Celestial=pd.DataFrame(columns=['Rising Time', 'Setting Time', 'Position', 'Azimuth', 'Altitude'], index=CelNames)
    for cob in CelObjs:
        
        # get rising and setting times
        # next line questionable
        #LOC.date = localMorning
        LOC.date=LTN - timedelta(hours=4)
        cob.compute(LOC)
        rTime=LOC.next_rising(cob)
        sTime=LOC.next_setting(cob)
        
        if rTime> sTime:
            rTime=LOC.previous_rising(cob)
        # move from ephem time to datetime time
        # set naive time to utc timezone, then convert to local
        risingTime=rTime.datetime().replace(tzinfo=timezone.utc)
        settingTime=sTime.datetime().replace(tzinfo=timezone.utc)
        risingTime=convertLocalTime(risingTime, lTimeZone) 
        settingTime=convertLocalTime(settingTime, lTimeZone)
        pos=(LocalTimeNow(lTimeZone)-risingTime)/(settingTime-risingTime)
        if pos <0:
            pos=0
        elif pos>= 1:
            pos=.995           
        
        # get azmith and elevation -- get rising and setting times based on "now" four hours earlier
        # this allows the progress indicator to be full for four hours after object setting
        LOC.date = LTN 
        cob.compute(LOC)
        azideg=cob.az        
        azimuth=re.findall(r"(\d+):", to_string(azideg))[0]+u"\u00b0"
        altdeg=cob.alt
        altitude=re.findall(r"(-?\d+):", to_string(altdeg))[0]+u"\u00b0"
        Celestial.loc[cob.name]=pd.Series({
                                   'Rising Time': risingTime
                                  ,'Setting Time': settingTime
                                  ,'Position' : pos
                                  , 'Azimuth' : azimuth
                                  , 'Altitude' : altitude
                                     } )
    return(Celestial)
    

## to display in streamlit: https://docs.streamlit.io/library/api-reference/charts/st.pyplot
def plotMoonPhase(lTimeZone, lat=0, long=0):
    import numpy as np
    from matplotlib import pyplot as plt
    from math import sin, cos, pi
    from datetime import datetime, timedelta, timezone
    
    if lat != 0:
        LOC = ephem.Observer()
        try:
            LOC.lon = to_string(long)
            LOC.lat = to_string(lat)
        except:
            LOC = ephem.city("Chicago")
    else:
        LOC = ephem.city("Chicago")
    
    lastNewMoon=ephem.previous_new_moon(LOC.date)
    nextNewMoon=ephem.next_new_moon(LOC.date)
    nextFullMoon=ephem.next_full_moon(LOC.date)
    decPhase=(LOC.date-lastNewMoon)/(nextNewMoon-lastNewMoon)
    phase=(-decPhase+.25)*2*pi
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    
    im = streamReadIm('images/'+"Moon_Phase_Diagram.gif")
    fig, ax = plt.subplots()
    im = ax.imshow(im, extent=[-150, 230,-150, 150])
    x = np.array(range(38, 50))
    rad=120
    siz=60
    moonPos = plt.Circle((sin(phase)*rad, cos(phase)*rad), siz, edgecolor="orange", linewidth=3, alpha=.5, fill=False, clip_on=False)
    ax.add_patch(moonPos)
    d=dtdt.now()
    nextFullDate=to_string(f"{DaysOfTheWeek[nextFullMoon.datetime().isoweekday()]}, {nextFullMoon.datetime().strftime('%B')} {nextFullMoon.datetime().day}")
    nextNewDate=to_string(f"{DaysOfTheWeek[nextNewMoon.datetime().isoweekday()]}, {nextNewMoon.datetime().strftime('%B')} {nextNewMoon.datetime().day}")
    ax.text(65, -33, nextNewDate, fontsize=8)
    ax.text(-160, -33, nextFullDate, fontsize=8)
    ax.plot(sin(phase)*x, cos(phase)*x, ls='solid', linewidth=7, color='orange', alpha=1)
    plt.axis('off')
    return(fig)    

# hovertext
# https://mplcursors.readthedocs.io/en/stable/
# https://github.com/anntzer/mplcursors/issues/23
from math import pi, sin, cos
def getXY(az, alt):
    R=0.5*pi+alt
    return((sin(pi+az)*R, cos(pi+az)*R))

def sCircle( xyLoc, radius, color, label=""):
        from matplotlib.patches import Polygon        
        import numpy as np
        th = np.linspace(0, 2 * np.pi, 100)
        pC=Polygon(radius * np.c_[np.cos(th), np.sin(th)] + np.array(xyLoc), closed=True, color=color, 
                label=label)
        return(pC)
    
def rCircle( xyLoc, radius, edgecolor, label=""):
        from matplotlib.patches import Polygon        
        import numpy as np
        th = np.linspace(0, 2 * np.pi, 100)
        pC=Polygon(radius * np.c_[np.cos(th), np.sin(th)] + np.array(xyLoc), closed=True,  
                   edgecolor=edgecolor, fill=False, label=label)
        return(pC)

def CelestialPicture(lTimeZone, lat=0, long=0):
    import matplotlib.pyplot as plt,numpy as np
    from math import pi, tan
    import ephem
    import mplcursors
    #%matplotlib inline
    #%matplotlib widget

    if lat != 0:
        LOC = ephem.Observer()
        try:
            LOC.lon = to_string(long)
            LOC.lat = to_string(lat)
        except:
            LOC = ephem.city("Chicago")
    else:
        LOC = ephem.city("Chicago")

    # LOC must be set with lat and long!
    LTN=dtdt.now()  #LocalTimeNow(lTimeZone)
    localMorning=datetime(LTN.year,LTN.month,LTN.day,5)
    
    sun = ephem.Sun()
    moon = ephem.Moon()
    LOC.date = ephem.Date(datetime.utcnow()) 
    sun.compute(LOC)
    rTime=LOC.next_rising(sun)
    sTime=LOC.next_setting(sun)
    if rTime> sTime:
        rTime=LOC.previous_rising(sun)
    
    sun = ephem.Sun()
    moon = ephem.Moon()
    mars= ephem.Mars()
    venus= ephem.Venus()
    mercury=ephem.Mercury()
    jupiter=ephem.Jupiter()
    saturn=ephem.Saturn()
    uranus=ephem.Uranus()
    neptune=ephem.Neptune()
    pluto=ephem.Pluto()
    CelObjs=[sun,moon,mercury,venus,mars,jupiter,saturn, uranus, neptune,pluto]
    CelNames=['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn', 'Uranus', 'Neptune','Pluto']
    
    # sun rising and setting
    LOC.date=rTime
    sun.compute(LOC)
    risingAz=sun.az
    risingAlt=sun.alt
    #print(sun.az, sun.alt)
    LOC.date=sTime
    sun.compute(LOC)
    settingAz=sun.az
    settingAlt=sun.alt
    #print(sun.az, sun.alt)
            
    # relative darkness
    riseFrac=(ephem.Date(datetime.utcnow())-rTime)/(sTime-rTime)
    relRise0=abs(riseFrac-0.5)
    relRise=min(1.1, 2*relRise0)/1.1
    darkness=relRise**2
    #print(riseFrac,relRise,darkness)
        
    xfac=1.01
    xr=[-xfac*pi,xfac*pi]
    yr=[-xfac*pi,xfac*pi]

    zLeg=[0.02, 0.22, 0.41, 0.61, 0.80]
    legX=[]
    for z in zLeg:
        legX.append(z*xr[1]+(1-z)*xr[0])
    legY=[.85*yr[0], .95*yr[0]]
    
    legendLocs={'Sun': (legX[0],legY[0]),'Moon': (legX[0],legY[1]),'Mercury': (legX[1],legY[0]),'Venus': (legX[1],legY[1]),'Mars': (legX[2],legY[0]),'Jupiter': (legX[2],legY[1]),'Saturn': (legX[3],legY[0]), 'Uranus': (legX[3],legY[1]), 'Neptune': (legX[4],legY[0]),'Pluto': (legX[4],legY[1])}

    legendColorsDay={'Sun': 'black','Moon': 'black','Mercury': 'black','Venus': 'black','Mars': 'black','Jupiter': 'black','Saturn': 'black', 'Uranus': 'black', 'Neptune': 'black','Pluto': 'black'}
    legendColorsNight={'Sun': 'black','Moon': 'black','Mercury': 'red','Venus': 'black','Mars': 'red','Jupiter': 'red','Saturn': 'red', 'Uranus': 'black', 'Neptune': 'black','Pluto': 'black'}
    
    # memory issues: https://stackoverflow.com/questions/28757348/how-to-clear-memory-completely-of-all-matplotlib-plots
    from matplotlib.figure import Figure
    fig = Figure(figsize=(5.0,5.0))
    ax = fig.subplots()   
    ax.set_xlim(xr)
    ax.set_ylim(yr)

    #plt.close(999)
    #fig, ax = plt.subplots(num=999,clear=True)
        
    if 1==1:
        nx, ny = 50.,50.
        xgrid, ygrid = np.mgrid[xr[0]:xr[1]:(xr[1]-xr[0])/nx,yr[0]:yr[1]:(yr[1]-yr[0])/ny]
        im = xgrid*0 + np.nan
        cmap = plt.cm.Blues
        cmap.set_bad('white')

        # set up chart
        plt.imshow(im.T, cmap=cmap, extent=xr+yr, vmin=0, vmax=1)
        
        from matplotlib.colors import Normalize
        norm = Normalize(0, 1)
        circle0 = sCircle((0, 0), .49*pi, color='black', label='Not visible in daytime because below the horizon')
        circle1 = sCircle((0, 0), 0.025*pi, color='r', label='origin')
        circle2 = rCircle((0, 0),.5*pi, edgecolor='r', label='This is the horizon')
        # https://stackoverflow.com/questions/51020192/circle-plot-with-color-bar
        circle2a = sCircle((0, 0), pi, color=cmap(norm(darkness)), label='This is the total vertical, looking straight up')
        if darkness < .75:
            circle3 = rCircle((0, 0),pi, edgecolor='r', label='This is the total vertical, looking straight up')
        else:
            circle3 = rCircle((0, 0),pi, edgecolor='black', label='This is the total vertical, looking straight up')

        ax.add_patch(circle2a)
        ax.add_patch(circle0)
        ax.add_patch(circle1)
        ax.add_patch(circle2)
        ax.add_patch(circle3)

        # set celestial objects
        doLegend=True
        from matplotlib.offsetbox import OffsetImage, AnnotationBbox
        LOC.date=ephem.Date(datetime.utcnow())
        zoomMag=1.5
        cobZoom={'Sun': 0.15,'Moon': 0.10,'Mercury': 0.10,'Venus': 0.10,'Mars': 0.03,'Jupiter': 0.15,'Saturn': 0.10, 'Uranus': 0.08, 'Neptune': 0.08,'Pluto': 0.075}
        moonPhasesSuf=['new','XC','FQ','XG','full','WG','3Q','WC']
        for cob in CelObjs:
            # curren positions
            cob.compute(LOC)
            xy=getXY(cob.az, cob.alt)
            if cob.name!='Moon':
                fName=cob.name
            else:
                lastNewMoon=ephem.previous_new_moon(LOC.date)
                nextNewMoon=ephem.next_new_moon(LOC.date)
                nextFullMoon=ephem.next_full_moon(LOC.date)
                decPhase=(LOC.date-lastNewMoon)/(nextNewMoon-lastNewMoon)
                numPhase=int(decPhase*7.999)
                fName='Moon-'+moonPhasesSuf[numPhase]
            #imtest = plt.imread('images/'+fName+'.png')
            imtest = streamReadIm('images/'+fName+'.png')
            soi = OffsetImage(imtest, zoom = zoomMag*cobZoom[cob.name])
            # set celestial object on chart 
            sbox = AnnotationBbox(soi, (xy[0], xy[1]), frameon=False, label=cob.name)   
            ax.add_artist(sbox)
            # set legend
            if doLegend==True:
                soi = OffsetImage(imtest, zoom = zoomMag*0.4*cobZoom[cob.name])
                sbox = AnnotationBbox(soi, legendLocs[cob.name], frameon=False, label=cob.name)   
                ax.add_artist(sbox)
                if darkness < .75:
                    tColor=legendColorsDay[cob.name]
                else: 
                    tColor=legendColorsNight[cob.name]
                ax.annotate(cob.name, legendLocs[cob.name], xytext=((7,-4)), textcoords='offset points', color=tColor, fontsize=10)
      
        cursor = mplcursors.cursor(ax.patches, hover=2) #mplcursors.HoverMode.Transient)
        cursor.connect('add', lambda sel: sel.annotation.set(text=sel.artist.get_label()))
        cursor2 = mplcursors.cursor(ax.artists, hover=2) #mplcursors.HoverMode.Transient)
        cursor2.connect('add', lambda sel: sel.annotation.set(text=sel.artist.get_label()))
        if darkness < .75:
            ax.annotate("South", xy=(0, xfac*pi-0.2), xytext=((0-0.375,xfac*pi-0.2)), color='black', weight='bold') 
        else: 
            ax.annotate("South", xy=(0, xfac*pi-0.2), xytext=((0-0.375,xfac*pi-0.2)), color='red', weight='bold') 
        #ax.annotate(f"rel: {relRise}, d: {darkness}", xy=(-pi, xfac*pi-0.2), xytext=((-pi+0.5,xfac*pi-0.2)), color='black') 
        #plt.axis('off')
        import numpy as np
        np.vectorize(lambda ax:ax.axis('off'))(ax)
        return(fig)
        #plt.show()
        
# to get city if coords are available
#@st.cache_resource
def geoloc():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        geolocator = Nominatim(user_agent="celestialgoingson")
    return(geolocator)
    
    #st.set_page_config(layout="centered")
    #localScreenWidth=streamlit_js_eval(js_expressions='screen.width', key = 'SCR')
        
    # https://discuss.streamlit.io/t/streamlit-geolocation/30796
    # https://github.com/aghasemi/streamlit_js_eval/tree/master
    # aghasemi Alireza Ghasemi

import streamlit as st
@st.cache_resource
def streamReadIm(fileLoc):
    import matplotlib.pyplot as plt
    return plt.imread(fileLoc)

def main():    
    import streamlit as st
    import time
    from streamlit_javascript import st_javascript
    from streamlit_js_eval import streamlit_js_eval, get_geolocation
    
    localTimeZone = st_javascript("""await (async () => {
            const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            console.log(userTimezone)
            return userTimezone
            })().then(returnValue => returnValue)""")

    geolocator=geoloc()

    @st.cache_resource
    def getCity(lat,long):
        if lat == 0 or long == 0:
            return(None)
        geostr=to_string(f"{lat}, {long}")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                location = geolocator.reverse(geostr)
            except:
                location=None
        try:
            x=location.raw['address']
        except:
            return(None)
        try:
            return(location.raw['address']['city'])
        except KeyError:
            return(location.raw['address']['town'])

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
    
    import contextlib
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with contextlib.suppress(TypeError):
            localLat=None
            localLong=None
            location=get_geolocation()
            localLat=to_string(location['coords']['latitude'])
            localLong=to_string(location['coords']['longitude'])

    # check city
    localCity=getCity(localLat,localLong)
 
    # Location Updating
    def Location_Update():
        with st.form("location_update"):
           st.write("Inside the form")
           slider_val = st.slider("Form slider")
           checkbox_val = st.checkbox("Form checkbox")
           # Every form must have a submit button.
           submitted = st.form_submit_button("Submit")
           if submitted:
               st.write("slider", slider_val, "checkbox", checkbox_val)

    def DT_Update():
        with st.form("location_update"):
           st.write("Inside the form")
           slider_val = st.slider("Form slider")
           checkbox_val = st.checkbox("Form checkbox")
           # Every form must have a submit button.
           submitted = st.form_submit_button("Submit")
           if submitted:
               st.write("slider", slider_val, "checkbox", checkbox_val)

    st.title("Celestial Companion")
    placeholderTime=st.empty()
    with placeholderTime.container():
        #with COLB1:
        d=LocalTimeNow(localTimeZone)
        if localCity!=None:
            st.subheader(f"{localCity}, {DaysOfTheWeek[dayOfTheWeekNum(localTimeZone)]}, {d.strftime('%B')} {d.day}, {d.strftime('%H:%M:%S')}")
        else:
            st.subheader(f"{DaysOfTheWeek[dayOfTheWeekNum(localTimeZone)]}, {d.strftime('%B')} {d.day}, {d.strftime('%H:%M:%S')}")
    
    TAB1, TAB2, TAB3, TAB4, TAB5 = st.tabs(["Celestial Globe", "Moon Phases", "Table", "Why", "About"])
    
    with TAB1:
        placeholder1=st.empty()
        
    with TAB2:
        placeholder2=st.empty()
    
    with TAB3:
        placeholder3=st.empty()
        
    with TAB4:
        placeholder4=st.empty()

    with TAB5:
        placeholder5=st.empty()

    firstIt=True
    lastMinute=-99
    while True==True:
        with TAB3:
            #st.markdown(localTimeZone)
            #st.markdown(f"Latitude: {localLat}, Longitude: {localLong}")
            while False==False:
                
                placeholderTime.empty()
                with placeholderTime.container():
                    d=LocalTimeNow(localTimeZone)
                    if localCity!=None:
                        st.subheader(f"{localCity}, {DaysOfTheWeek[dayOfTheWeekNum(localTimeZone)]}, {d.strftime('%B')} {d.day}, {d.strftime('%H:%M:%S')}")
                    else:
                        st.subheader(f"{DaysOfTheWeek[dayOfTheWeekNum(localTimeZone)]}, {d.strftime('%B')} {d.day}, {d.strftime('%H:%M:%S')}")
                    znow=datetime.now()
                    delay=1-(znow-datetime(znow.year,znow.month,znow.day,znow.hour,znow.minute, znow.second)).total_seconds()
                    time.sleep(delay)
                    if firstIt==True:
                        firstIt=False
                        break
                    # update charts every five minutes
                    period=5
                    dtMinute=LocalTimeNow(localTimeZone).minute
                    if dtMinute/period == int(dtMinute/period) and dtMinute != lastMinute:
                        lastMinute=LocalTimeNow(localTimeZone).minute
                        break
                        
            # check city in case app is travelling
            localCity=getCity(localLat,localLong)

            placeholder3.empty()
            with placeholder3.container():
                st.write('''<style>

                [data-testid="column"] {
                    width: calc(33.3333% - 1rem) !important;
                    flex: 1 1 calc(33.3333% - 1rem) !important;
                    min-width: calc(33% - 1rem) !important;
                }
                </style>''', unsafe_allow_html=True)

                d2=LocalTimeNow(localTimeZone)
                COLZ=[.20,.15,.20,.15,.15,.15]
                COL1, COL2, COL3, COL4, COL5, COL6 = st.columns(COLZ)
                if 1 == 1:
                    with COL1:
                        st.markdown("**Celestial Object**")
                    with COL2:
                        st.markdown("**Rising Time**")
                    with COL3:
                        st.markdown(f"<div style='text-align: center'> . <b>transit progress</b> . </div>",unsafe_allow_html=True)
                    with COL4:
                        st.markdown("**Setting Time**")
                    with COL5:
                        deg=u"\u00b0"
                        helpText="Azimuth is the clockwise position in degress from North. Azimuth is updated every 5 minutes. Directions correspond to azimuth as follows: East=90"+deg+", South=180"+deg+", West=270"+deg+", and North=360"+deg+" and 0"+deg+". A celestial body has azmith while risen and after setting."
                        st.markdown("**Azimuth**", help=helpText)              
                    with COL6:
                        helpTextAlt="Altitude is the elevation in degress relative to the horizon. Negative altitude indicates objects that have set. Altitude is updated every 5 minutes."
                        st.markdown("**Altitude**",help=helpTextAlt)
       
                for cob in Celestial(localTimeZone, localLat, localLong).iterrows():
                    COL1, COL2, COL3, COL4, COL5, COL6 = st.columns(COLZ)
                    with COL1:
                        st.markdown(f"**{cob[0]}**")
                    with COL2:
                        st.markdown(f"{ShortDaysOfTheWeek[cob[1][0].weekday()]} {cob[1][0].strftime('%H:%M')}")
                    with COL3:
                        st.progress(cob[1][2])
                    with COL4:
                        st.markdown(f"{ShortDaysOfTheWeek[cob[1][1].weekday()]} {cob[1][1].strftime('%H:%M')}")  
                    with COL5:
                         zspace=".........."
                         st.markdown(f"<div style='text-align: center'>{cob[1][3]}</div>",unsafe_allow_html=True)
                    with COL6:
                         st.markdown(f"<div style='text-align: center'>{cob[1][4]}</div>",unsafe_allow_html=True)
                st.divider()
                with st.expander("For more information this table of celestial objects click here ..."):
                    st.markdown(f"This is a table of the rising and setting times and the relative position in transit of the Sun, Moon, the planets, and the dwarf planet Pluto. The progress indicator for each celestial body indicates its relative transit from rising to setting as of {d2.strftime('%H:%M')}. Positions update on the quarter hour. Times are for your location if you give permission for the app to read your position, or for Chicago otherwise.")
                    st.markdown(f"All times reported for the {localTimeZone} timezone ([IANA](https://www.iana.org/time-zones) classification) and are based on the browser-obtained position of {localLat} degrees latitude and {localLong} degress logitude, or if permission was not granted, location in Chicago is assumed.")

        with TAB2:
            placeholder2.empty()
            with placeholder2.container():
                st.header("Current Phase of the Moon")
                st.pyplot(plotMoonPhase(localTimeZone, localLat, localLong))
                st.markdown("Dates are for the next new and full moons. The orange line and circle indicate the current moon phase. Illustration credit Wikipedia: Andonee - Own work [CC BY-SA 4.0](htps://commons.wikimedia.org/w/index.php?curid=38635547)")
        with TAB1:
            placeholder1.empty()
            with placeholder1.container():
                matplotlib.pyplot.close(999)
                CP=CelestialPicture(localTimeZone, localLat, localLong)
                st.pyplot(CP)
                with st.expander("For more information this chart of celestial objects click here ..."):
                    st.markdown(f"This chart shows the celestial objects oriented as an observer facing South would see them. Objects rise to East, which is on the left side of the chart, and set in the West, which is the right side of the chart. The South is at the top of the chart and North is at the bottom.")
                    st.markdown(f"An object's position is determined by its azimuth and altitude. Azimuths and altitudes for all charted celestial objects are shown on the main page of this app.") 
                    st.markdown(f"An object's azimuth is the angle moving to the object clockwise from North at the bottom of the chart.") 
                    st.markdown(f"An object's elevation is represented relative to the horizon, which is represented as the red ring surrounding the black central area of the chart. Objects above the horizon are shown in the region between the horizon ring and the outer red ring representing 90"+deg+" elevation. Objects that are below the horizon and cannot be seen are in the black area. Ninty degrees negative elevation is the dead center of the chart, in red.")
                    st.markdown(f"The region between the two red rings corresponds to the visible sky. This region is shown in light blue during the day and dark blue at night. Around sunrise and sunset intermediate colors are shown.")

                with st.expander("To update location ..."):
                    #blRez=st.button("Update location", disabled=False, key=11, type="primary", on_click=Location_Update) 
                    #btRez=st.button("Update date and or time", disabled=False, key=22, type="primary", on_click=DT_Update) 
                    #if blRez:
                    #    viz="visible"
                    #else:
                    #    viz="collapsed"
                    st.text_input("Enter new location for Celestical Companion.", label_visibility="visible")
                with st.expander("To update date or time ..."):
                    #btRez=st.button("Update Date or Time", disabled=False, key=222, type="primary", on_click=DT_Update) 
                    #btRez=st.button("Update date and or time", disabled=False, key=22, type="primary", on_click=DT_Update) 
                    #if btRez:
                    #    vizd="visible"
                    #else:
                    #    vizd="collapsed"
                    colE1, colE2 = st.columns([.5,.5])
                    with colE1:
                        newDate=LocalTimeNow(localTimeZone)
                        st.date_input("Enter new date", value=newDate, help=None, on_change=None, args=None, kwargs=None, format="YYYY/MM/DD", disabled=False, label_visibility="visible")
                    with colE2:
                        newTime=newDate
                        st.time_input("Enter new time", value=newTime, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible")
                #####
                    
        with TAB4:
            placeholder4.empty()
            with placeholder4.container():
                st.write("We all live under and share the same sky! We are all to disconnected from nature. We need to reconnect with the nature within ourselves. One way to reconnect with ourselves is to reconnect with nature. Awareness of the phases of the moon and the positions of the sun and planets ... and even the drarf planet Pluto ... can help us recoonect with our own natures. Celestial awareness can help us reconnect with our true nature by helping us step back from our intense engagements at work, in the news, with social media and in other places.")
            
            
        with TAB5:
            placeholder5.empty()
            with placeholder5.container():
                st.write("This app was developed to promote celestial awareness, and most particularly, of the rising and setting times of the Sun and the Moon and the phases of the Moon.")
                st.write("Celestial Companion is distributed to the web using [Streamlit](https://streamlit.io), an open-source [Python](https://www.python.org/) package. Celestial positions are calcuated in Python with [PyEphem](https://rhodesmill.org/pyephem/index.html), another open-source Python pacakge. Rising and setting times are approximate, based on the latitude and longitude returned from the request to the user's browser or on PyEphem's Chicago coordinates.")
                zImage = streamReadIm('images/'+"zimage.jpg")
                st.image(zImage,caption="Source: Wikipedia")

if __name__ == '__main__':
    main()        
