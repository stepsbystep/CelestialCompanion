# to-do items:
#  - Day of week chakra on top of mind page
#  - Chakra description expander?
#  - permissions for point descriptions and body images
#  - add change of season to monthly, weekly, meridian, and hourly wedges

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

from QigongCalendar_base import *
from QigongCalendar_Fns import * 
import BodyChart as BC
import heClock as HEC

def main():    
    import streamlit as st
    import time

    # deal with connection error message
    # https://discuss.streamlit.io/t/suppressing-connection-error-message/28264
    hide = """
        <style>
        div[data-testid="stConnectionStatus"] {
        display: none !important;
        </style>
        """
    st.markdown(hide, unsafe_allow_html=True)    


    # https://discuss.streamlit.io/t/determine-users-local-timezone/24074/2
    # returns in IANA timezone format https://stackoverflow.com/questions/6939685/get-client-time-zone-from-browser
    localTimeZone = st_javascript("""await (async () => {
            const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            console.log(userTimezone)
            return userTimezone
            })().then(returnValue => returnValue)""")
    
    if type(localTimeZone) != str:
        #print(f"local time zone type: {type(localTimeZone)}, localTimeZone: {localTimeZone}")
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

    TAB1, TAB2, TAB3, TAB4, TAB5, TAB6 = st.tabs(["Top of Mind", "Weekly", "Body", "Clock", "More", "About" ])
    
    with TAB1:
        PlaceHolder1a=st.empty()
        PlaceHolder1b=st.empty()
    with TAB2:
        PlaceHolder2=st.empty()
    with TAB3:
        PlaceHolder3=st.empty()
    with TAB4:
        PlaceHolder4=st.empty()
    with TAB5:
        PlaceHolder5=st.empty()
    with TAB6:
        PlaceHolder6=st.empty()
    
    # done in the time loop at the end of TAB1
    #with TAB2:

    with TAB2:
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

    with TAB5:
        PlaceHolder5.empty()
        with PlaceHolder5.container():
        #if True:
            
            ZTAB1, ZTAB2, ZTAB3, ZTAB4, ZTAB5, ZTAB6, ZTAB7 = st.tabs(["Solar", "Lunar", "Time", "Rings", "Spine", "Days of Week", "Points"])
    
            #with ZTAB1:
            #    PlaceHolderZ1=st.empty()
            #with ZTAB2:
            #    PlaceHolderZ2=st.empty()
            #with ZTAB3:
            #    PlaceHolderZ3=st.empty()
            #with ZTAB4:
            #    PlaceHolderZ4=st.empty()
            #with ZTAB5:
            #    PlaceHolderZ5=st.empty()
            #with ZTAB6:
            #    PlaceHolderZ6=st.empty()


            # solar cycle
            with ZTAB1:
                SunPos=SeasonalPoints[(SeasonalPoints.Season==seasons4[seasonNum()-1]) & (SeasonalPoints.Week==getSeasWeek())].iloc[0]
                st.pyplot(solarCyclePlot(SunPos.Week-1))
                
            # lunar cycle
            with ZTAB2:
                tM, nxtM=todaysMoon()
                st.pyplot(lunarCyclePlot(tM.Day-1))
            
            with ZTAB3:
                st.markdown(" ")
                if "tMerid" not in st.session_state:
                    st.session_state.tMerid = "LU"
                st.markdown(" ")
                st.session_state.tMerid=st.selectbox("Select Meridian", meridDropList[:12], index=0, disabled=False,key="sdfgiouertu67")
                st.markdown(f"Time points associated with the {Meridians[st.session_state.tMerid[:2]]} meridian.")
                seltPts=TimePoints[TimePoints.Point.str[:2]==st.session_state.tMerid[:2]]
                st.dataframe(seltPts, hide_index=True, column_order=['Seq', 'Time', 'Point', 'English Name', 'Chinese Name'])
                with st.expander("Click for more information on time points ..."):
                    st.markdown(TextSegments['tPoints-1'])
                    st.markdown(TextSegments['tPoints-2'])

            # Time points
            with ZTAB4:
                if "tRing" not in st.session_state:
                    st.session_state.tRing = "Neck Ring"
                st.markdown(" ") 
                Rings=JointRings.Ring.unique().tolist()     
                st.session_state.tRing=st.selectbox("Select Ring", Rings, index=dayOfTheWeekNum(localTimeZone), disabled=False,key="eurW2rie5")
                selPts=JointRings[JointRings.Ring==st.session_state.tRing]
                st.dataframe(selPts, hide_index=True, column_order=['Point','English Name'])

            with ZTAB5:
                #PlaceHolderZ2.empty()
                st.markdown(" ") 
                st.dataframe(VerticalColumn, hide_index=True)
                                
            with ZTAB6:
                #PlaceHolderZ3.empty()
                st.markdown(" ")
                WeekDayz= WeekDays.set_index('Day of Week')
                st.dataframe(WeekDayz)

            with ZTAB7:

                tM=st.selectbox("Select Meridian", meridDropList[:14], index=0, key="ZXRRRJTZZZZZZ")
    
                selMerid=AcuPoints[AcuPoints.Point.str[:2]==tM[:2]]
                numPts=len(selMerid)
    
                # Configure grid options using GridOptionsBuilder
                builder = GridOptionsBuilder.from_dataframe(selMerid)
                if numPts<15:
                    builder.configure_pagination(enabled=False)
                else:
                    builder.configure_pagination(enabled=True)        
                    builder.configure_pagination(paginationAutoPageSize=False)
                    builder.configure_pagination(paginationPageSize = 15)
                builder.configure_selection(selection_mode='single', use_checkbox=False)
                builder.configure_default_column(flex=1,resizable=True)
                grid_options = builder.build()

                # Display AgGrid
                rv = AgGrid(selMerid, gridOptions=grid_options,key="pri4857GH")
                if rv['selected_rows']:
                    selPoint = rv['selected_rows'][0]['Point']
                    desc=PointDescriptions[PointDescriptions.Point==selPoint]
                    st.write(f"Description of {selPoint}:")
                    st.write(desc.iloc[0]['Point Description'])
                else:
                    st.write("No point selected.")
                    st.write("")            
               
    # About tab
    with TAB6:
        st.write(TextSegments['Abt-1'])
        st.write(TextSegments['Abt-2'])
        st.write(TextSegments['Abt-3'])
        st.image("https://upload.wikimedia.org/wikipedia/commons/1/19/Solar_System_true_color.jpg",caption="Source: Wikipedia")
        

    rAdj=-1
    lastQH=-1
    lastM=-1
    lastS=-100
    while True==True:
        
        # TRACK LARGE INTERVAL NOW 5 MIN
        d=LocalTimeNow(localTimeZone)
        qH=int(d.minute/5)

        # Time update ... now by second for testing
        if d.second != lastS:
            with TAB1:
                PlaceHolder1a.empty()
                with PlaceHolder1a.container():
                    st.header(f"{DaysOfTheWeek[dayOfTheWeekNum(localTimeZone)]}, {d.strftime('%B')} {d.day}, {d.strftime('%H:%M')}")

        # LARGE TIME INTERVAL
        if qH != lastQH:
            #if True:
            with TAB1:
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
                        else:
                            st.write("")
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
                        st.markdown("Based on Debra Kaatz's Characters of Wisdom - Taoist Tales of the Acupuncture Points, 2005, The Petite Bergerie Press.")
                
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
                        st.markdown("Based on Debra Kaatz's Characters of Wisdom - Taoist Tales of the Acupuncture Points, 2005, The Petite Bergerie Press.")

                    with st.expander("Click for seasonal point description ..."):
                        spDesc=PointDescriptions[sunPoint==PointDescriptions['Point']]
                        spDesc=spDesc['Point Description'].values 
                        st.markdown(f"{spDesc[0]}")
                        st.markdown("Based on Debra Kaatz's Characters of Wisdom - Taoist Tales of the Acupuncture Points, 2005, The Petite Bergerie Press.")

                            
        if qH != lastQH:
            #if True:
            with TAB3:
                #if True:
                with PlaceHolder3.container():
                    st.pyplot(BC.BodyChart(SunRing, MoonRing, localTimeZone, nowP, TP, tVC, sunPoint))
                    st.markdown("Based on images from the excellent [Tsubook](https://www.tsubook.net/en/) acupoint Shiatsu app")
                    #st.markdown("Tsubook is an excellent app for a 3d perspective of the body, its structure, and the location of acupoints in this context.")

                    with st.expander("Click for more information on this illustration ..."):
                        st.markdown(TextSegments['Body-1'])
                        st.markdown(TextSegments['Body-2'])
                        st.markdown(TextSegments['Body-3'])
                                        
                    timeDF, timeDFp=clockRange(localTimeZone)
                    timeDF=timeDF.drop(columns=['Seq', 'pTime'])
                    timeDFp=timeDFp.drop(columns=['Seq', 'pTime'])
                    st.divider()
                    st.subheader(f"Meridian Clock around {d.strftime('%H:%M')}")
                    st.dataframe(timeDF, hide_index=True)
                    st.subheader(f"Counterpoints")
                    st.dataframe(timeDFp, hide_index=True)
                    with st.expander("Click for more information on time points ..."):
                        st.markdown(TextSegments['tPoints-1'])
                        st.markdown(TextSegments['tPoints-2'])

                    st.divider()

        # HIGH FREQUENCY UPDATING
        with TAB4:
            with PlaceHolder4.container():
                st.subheader('Between Heaven and Earth Clock')
                d=LocalTimeNow(localTimeZone)
                if d.minute != lastM or rAdj==-1:
                    d0=LocalTimeNow(localTimeZone)
                    cfig, cax, cxfac, rAdj, degs, yearPhaseDeg, rainbowMap, yExtra, curMerid = HEC.heClock(timeDF, timeDFp, localTimeZone, localLat, localLong)
                    d1=LocalTimeNow(localTimeZone)
                    delta1=d1-d0
                    
                    #st.pyplot(cfig)
                lastM=d.minute
                    
                if d.second!=lastS:
                #if True:
                    from matplotlib.patches import Wedge
                        #for i in range(0,60):
                    s=d.second
                    cAdj=7/24*degs
                    # rotating color segments over the minute
                    for i in range(0,12):
                        zcxfac=.9975*cxfac
                        sWedge=Wedge((0,0), zcxfac*np.pi, rAdj+yearPhaseDeg+i/12*degs-s*6+cAdj, rAdj+yearPhaseDeg+(i+1)/12*degs-s*6+cAdj, width=(zcxfac-1)*np.pi, ec='black', fc=rainbowMap((11-i)/12), linewidth=1, alpha=1)
                        cax.add_patch(sWedge)
                    # vertical 
                    wedge0=Wedge( (0,0), yExtra*cxfac*np.pi, 89, 91, ec='black', fc='yellow', width=(yExtra*cxfac-1)*np.pi, alpha=0.5) #fill=None)
                    cax.add_patch(wedge0)
                    
                    #if d.second%10==0 or rAdj==-1:
                    ds0=LocalTimeNow(localTimeZone)                
                    st.pyplot(cfig)
                    lastS=d.second
                    #time.sleep(0.1)
                    ds1=LocalTimeNow(localTimeZone) 
                    delta2=ds1-ds0
                    
                   # print(delta1, delta2)

        lastS=d.second
        lastQH=qH

if __name__ == '__main__':
    main()        

