import pandas as pd
import io
import pytz
from streamlit_javascript import st_javascript
from backports.zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import ephem
import datetime as dt
from datetime import datetime as dtdt
from streamlit_js_eval import streamlit_js_eval, get_geolocation
import re
from geopy.geocoders import Nominatim

# to get city if coords are available
geolocator = Nominatim(user_agent="honoringthercelestial")

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
    tz_local = pytz.timezone(lTimeZone)
    return(d.astimezone(tz_local))   

def LocalTimeNow(lTimeZone):
    return(convertLocalTime(dtdt.now(pytz.timezone('UTC')), lTimeZone))
    
def Celestial(lTimeZone, lat=0, long=0):

    from datetime import datetime, timedelta, timezone
    
    if lat != 0:
        LOC = ephem.Observer()
        LOC.lon = to_string(long)
        LOC.lat = to_string(lat)
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
    neptune=ephem.Neptune()
    pluto=ephem.Pluto()
    CelObjs=[sun,moon,mercury,venus,mars,jupiter,saturn,neptune,pluto]
    CelNames=['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Neptune','Pluto']

    Celestial=pd.DataFrame(columns=['Rising Time', 'Setting Time', 'Position', 'Azimuth', 'Elevation'], index=CelNames)
    for cob in CelObjs:
        
        # get rising and setting times
        LOC.date = localMorning
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
        
        # get azmith and elevation
        LOC.date = LTN
        cob.compute(LOC)
        altdeg=cob.alt
        altitude=re.findall(r"(\d+):", to_string(altdeg))[0]+u"\u00b0"
        azideg=cob.az        
        azimuth=re.findall(r"(\d+):", to_string(azideg))[0]+u"\u00b0"
        Celestial.loc[cob.name]=pd.Series({
                                   'Rising Time': risingTime
                                  ,'Setting Time': settingTime
                                  ,'Position' : pos
                                  , 'Azimuth' : azimuth
                                  , 'Altitude' : altitude
                                     } )
    return(Celestial)

## to display in streamlit: https://docs.streamlit.io/library/api-reference/charts/st.pyplot
def plotMoonPhase(lTimeZone):
    import numpy as np
    from matplotlib import pyplot as plt
    from math import sin, cos, pi
    from datetime import datetime
    
    Chicago = ephem.city("Chicago")
    lastNewMoon=ephem.previous_new_moon(Chicago.date)
    nextNewMoon=ephem.next_new_moon(Chicago.date)
    nextFullMoon=ephem.next_full_moon(Chicago.date)
    decPhase=(Chicago.date-lastNewMoon)/(nextNewMoon-lastNewMoon)
    phase=(decPhase+.25)*2*pi
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    im = plt.imread("Moon_Phase_Diagram.gif")
    fig, ax = plt.subplots()
    im = ax.imshow(im, extent=[-150, 230,-150, 150])
    x = np.array(range(38, 50))
    rad=120
    siz=60
    moonPos = plt.Circle((sin(phase)*rad, cos(phase)*rad), siz, edgecolor="orange", linewidth=3, alpha=.5, fill=False, clip_on=False)
    ax.add_patch(moonPos)
    d=dtdt.now()
    nextFullDate=to_string(f"{DaysOfTheWeek[dayOfTheWeekNum(lTimeZone)]}, {nextFullMoon.datetime().strftime('%B')} {nextFullMoon.datetime().day}")
    nextNewDate=to_string(f"{DaysOfTheWeek[dayOfTheWeekNum(lTimeZone)]}, {nextNewMoon.datetime().strftime('%B')} {nextNewMoon.datetime().day}")
    ax.text(70, -33, nextNewDate)
    ax.text(-160, -33, nextFullDate)
    ax.plot(sin(phase)*x, cos(phase)*x, ls='solid', linewidth=7, color='orange', alpha=1)
    plt.axis('off')
    return(fig)    

def getCity(lat,long):
    if lat == 0 or long == 0:
        return(None)
    geostr=to_string(f"{lat}, {long}")
    location = geolocator.reverse(geostr)
    try:
        return(location.raw['address']['town'])
    except KeyError:
        return(location.raw['address']['city'])

def main():    
    import streamlit as st
    import time
    #st.set_page_config(layout="centered")

    #localScreenWidth=streamlit_js_eval(js_expressions='screen.width', key = 'SCR')
    
    localTimeZone = st_javascript("""await (async () => {
            const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            console.log(userTimezone)
            return userTimezone
            })().then(returnValue => returnValue)""")
    
    # https://discuss.streamlit.io/t/streamlit-geolocation/30796
    # https://github.com/aghasemi/streamlit_js_eval/tree/master
    # aghasemi Alireza Ghasemi
    location=get_geolocation()
    localLat=to_string(location['coords']['latitude'])
    localLong=to_string(location['coords']['longitude'])
    #st.write(f"Screen width is {localScreenWidth}")
    # android screen width is 412
    # Legion screen width is 1536


    
    st.title("Celestial Daily Companion")
    TAB1, TAB2, TAB3, TAB4 = st.tabs(["Main", "Phases of the Moon", "Why", "About"])
    
    with TAB1:
        placeholder1=st.empty()
        placeholder1b=st.empty()
        
    with TAB2:
        placeholder2=st.empty()
    
    with TAB3:
        placeholder3=st.empty()
        
    with TAB4:
        placeholder4=st.empty()


    firstIt=True    
    while True==True:
        with TAB1:
            #st.markdown(localTimeZone)
            #st.markdown(f"Latitude: {localLat}, Longitude: {localLong}")
            localCity=getCity(localLat,localLong)
            while False==False:
                placeholder1.empty()
                with placeholder1.container():
                    d=LocalTimeNow(localTimeZone)
                    if localCity:
                        st.header(f"{localCity}, {DaysOfTheWeek[dayOfTheWeekNum(localTimeZone)]}, {d.strftime('%B')} {d.day}, {d.strftime('%H:%M:%S')}")
                    else:
                    #if 1==1:
                        st.header(f"{DaysOfTheWeek[dayOfTheWeekNum(localTimeZone)]}, {d.strftime('%B')} {d.day}, {d.strftime('%H:%M:%S')}")
                    znow=datetime.now()
                    delay=1-(znow-datetime(znow.year,znow.month,znow.day,znow.hour,znow.minute, znow.second)).total_seconds()
                    time.sleep(delay)
                    if firstIt==True:
                        firstIt=False
                        break
                    if LocalTimeNow(localTimeZone).minute in [0, 15, 30, 45]:
                        break
                        
            placeholder1b.empty()
            with placeholder1b.container():
                d2=LocalTimeNow(localTimeZone)
                COLZ=[.20,.15,.35,.15,.15]
                #COLZ=[.15,.15,.25,.15,.15,.15]
                #COL1, COL2, COL3, COL4, COL5, COL6 = st.columns(COLZ)
                COL1, COL2, COL3, COL4, COL5 = st.columns(COLZ)
                if 1 == 1:
                    with COL1:
                        st.markdown("**Celestial Object**")
                    with COL2:
                        st.markdown("**Rising Time**")
                    with COL3:
                        st.markdown(f"<div style='text-align: center'> ........ <b>transit progress</b> ............ </div>",unsafe_allow_html=True)
                    with COL4:
                        st.markdown("**Setting Time**")
                    with COL5:
                        deg=u"\u00b0"
                        helpText="Azimuth is the clockwise position in degress from North. Azimuth is updated every 15 minutes. Directions correspond to azimuth as follows: East=90"+deg+", South=180"+deg+", West=270"+deg+", and North=360"+deg+" and 0"+deg+". A celestial body has azmith while risen and after setting."
                        st.markdown("**Azimuth**", help=helpText)              
                
                    #with COL6:
                    #    st.markdown("**Elevation**")
       
                for cob in Celestial(localTimeZone, localLat, localLong).iterrows():
                    COL1, COL2, COL3, COL4, COL5 = st.columns(COLZ)
                    #COL1, COL2, COL3, COL4, COL5, COL6 = st.columns(COLZ)
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
                    #with COL6:
                    #    st.markdown(cob[1][4])
                st.divider()
                with st.expander("For more information this table of celestial objects click here ..."):
                    st.markdown(f"This is a table of the rising and setting times and the relative position in transit of the Sun, Moon, the planets, and the dwarf planet Pluto. The progress indicator for each celestial body indicates its relative transit from rising to setting as of {d2.strftime('%H:%M')}. Positions update on the quarter hour. Times are for your location if you give permission for the app to read your position, or for Chicago otherwise.")
                    st.markdown(f"All times reported for the {localTimeZone} timezone ([IANA](https://www.iana.org/time-zones) classification) and are based on the browser-obtained position of {localLat} degrees latitude and {localLong} degress logitude, or if permission was not granted, location in Chicago is assumed.")

        with TAB2:
            placeholder2.empty()
            with placeholder2.container():
                st.header("Phases of the Moon and the Current Phase")
                st.pyplot(plotMoonPhase(localTimeZone))
                st.markdown("Dates are for the next new and full moons. The orange line and circle indicate the current moon phase. Illustration credit Wikipedia: Andonee - Own work [CC BY-SA 4.0](htps://commons.wikimedia.org/w/index.php?curid=38635547)")

        with TAB3:
            placeholder3.empty()
            with placeholder3.container():
                st.write("We all live under and share the same sky!")
            
            
        with TAB4:
            placeholder4.empty()
            with placeholder4.container():
                st.write("This app was developed to promote celestial awareness, and most particularly, of the rising and setting times of the Sun and the Moon and the phases of the Moon.")
                st.write("Celestial Companion is distributed to the web using [Streamlit](https://streamlit.io), an open-source [Python](https://www.python.org/) package. Celestial positions are calcuated in Python with [PyEphem](https://rhodesmill.org/pyephem/index.html), another open-source Python pacakge. Rising and setting times are approximate, based on the latitude and longitude returned from the request to the user's browser or on PyEphem's Chicago coordinates.")
                st.image("https://upload.wikimedia.org/wikipedia/commons/1/19/Solar_System_true_color.jpg",caption="Source: Wikipedia")


    
if __name__ == '__main__':
    main()        
