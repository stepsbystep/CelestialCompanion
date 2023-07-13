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
    
    #st.markdown(localTimeZone)
    #st.markdown(f"Latitude: {localLat}, Longitude: {localLong}")
    firstIt=True    
    st.title("Celestial Daily Companion")
    placeholder1=st.empty()
    placeholder2=st.empty()
    while True==True:
        while False==False:
            placeholder1.empty()
            with placeholder1.container():
                d=LocalTimeNow(localTimeZone)
                st.header(f"{DaysOfTheWeek[dayOfTheWeekNum(localTimeZone)]}, {d.strftime('%B')} {d.day}, {d.strftime('%H:%M:%S')}")
                znow=datetime.now()
                delay=1-(znow-datetime(znow.year,znow.month,znow.day,znow.hour,znow.minute, znow.second)).total_seconds()
                time.sleep(delay)
                if firstIt==True:
                    firstIt=False
                    break
                if LocalTimeNow(localTimeZone).minute in [0, 15, 30, 45]:
                    break

        COLZ=[.20,.15,.35,.15,.15]
        #COLZ=[.15,.15,.25,.15,.15,.15]
        
        with placeholder2.container():
            d2=LocalTimeNow(localTimeZone)
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
                    helpText="Azimuth is the clockwise position in degress from North. Azimuth is updated every 15 minutes. Directions correspond to azimuth as follows: East=90"+deg+", South=180"+deg+", West=270"+deg+", and North=360"+deg+" and 0"+deg+"."
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
#                    st.markdown(cob[1][3])
                     zspace=".........."
                     st.markdown(f"<div style='text-align: center'>{cob[1][3]}</div>",unsafe_allow_html=True)
                #with COL6:
                #    st.markdown(cob[1][4])
            st.divider()
            with st.expander("For more information about Celestial Daily Companion click here ..."):
                st.markdown(f"This is a table of the rising and setting times and the relative position in transit of the Sun, Moon, the planets, and the dwarf planet Pluto. The progress indicator for each celestial body indicates its relative transit from rising to setting as of {d2.strftime('%H:%M')}. Positions update on the quarter hour. Times are for your location if you give permission for the app to read your position, or for Chicago otherwise.")
                st.markdown(f"All times reported for the {localTimeZone} timezone ([IANA](https://www.iana.org/time-zones) classification) and are based on the browser-obtained position of {localLat} degrees latitude and {localLong} degress logitude, or if permission was not granted, location in Chicago is assumed.")
                st.write("This app was developed to promote celestial awareness, and most particularly, of the rising and setting times of the Sun and the Moon, as well as the phases of the moon. A page for phases of the Moon is planned be added at a future date.")
                st.write("Celestial Companion is distributed to the web using [Streamlit](https://streamlit.io), an open-source [Python](https://www.python.org/) package. Celestial positions are calcuated in Python with [PyEphem](https://rhodesmill.org/pyephem/index.html), another open-source Python pacakge. Rising and setting times are approximate, based on the latitude and longitude returned from the request to the user's browser or on PyEphem's Chicago coordinates.")
                st.image("https://upload.wikimedia.org/wikipedia/commons/1/19/Solar_System_true_color.jpg",caption="Source: Wikipedia")
    
if __name__ == '__main__':
    main()        
