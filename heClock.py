from QigongCalendar_Fns import * 
from QigongCalendar_base import *

def heClock(timeDF, timeDFp, lTimeZone, lat=0, long=0):
    import matplotlib.pyplot as plt
    import numpy as np
    from math import pi, tan
    from matplotlib.patches import Wedge
    from matplotlib.patches import Ellipse as Ellipse
    import ephem
    from datetime import datetime, timedelta
    import Symbols as sy 

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
    LTN=LocalTimeNow(lTimeZone)
    localMorning=datetime(LTN.year,LTN.month,LTN.day,5)

    # day phase
    lLTN=datetime(LTN.year,LTN.month,LTN.day,LTN.hour,LTN.minute,LTN.second)
    dayStart=datetime(LTN.year,LTN.month,LTN.day,0,0)
    dayEnd=datetime(LTN.year,LTN.month,LTN.day,23,59,59)
    decDay=(lLTN-dayStart)/(dayEnd-dayStart)
    dayPhaseRad=decDay*2*pi
    dayPhaseDeg=decDay*360
    
    # season
    seasons=get_seasons(LTN.year)
    sN=seasonNum()
    startSeas=ephem.localtime(seasons[sN])
    # end of current season
    endSeas=ephem.localtime(seasons[sN+1])
    #print(startSeas, endSeas,lLTN)
    decSeas=(lLTN-startSeas)/(endSeas-startSeas)
    seasPhaseRad=decSeas*2*pi
    seasPhaseDeg=decSeas*360
    
    if decSeas > 0.5:
        indSeas=endSeas
    else:
        indSeas=startSeas

    # seasonal- daily switch
    # active +/- 11 hours from current time
    sD=datetime(LTN.year,LTN.month,LTN.day,LTN.hour,LTN.minute)-timedelta(hours=11)
    eD=datetime(LTN.year,LTN.month,LTN.day,LTN.hour,LTN.minute)+timedelta(hours=11)
    if sD <= indSeas <= eD:
        daySeasChDec=(indSeas-dayStart)/(dayEnd-dayStart)
        daySeasChIndRad=daySeasChDec*2*pi
        daySeasChIndDeg=daySeasChDec*360
    else:
        daySeasChDec=None
        daySeasChIndRad=None
        daySeasChIndDeg=None
    
    
    # moon phase
    lastNewMoon=ephem.previous_new_moon(LOC.date)
    nextNewMoon=ephem.next_new_moon(LOC.date)
    nextFullMoon=ephem.next_full_moon(LOC.date)
    decMoon=(LOC.date-lastNewMoon)/(nextNewMoon-lastNewMoon)
    moonPhaseRad=(-decMoon)*2*pi
    moonPhaseDeg=-decMoon*360
    
    # annual
    yearStart=datetime(LTN.year,1,1,0,0)
    yearEnd=datetime(LTN.year,12,31,23,59,59)
    decYear=(lLTN-yearStart)/(yearEnd-yearStart)
    yearPhaseRad=decYear*2*pi
    yearPhaseDeg=decYear*360
    seasons=get_seasons(LTN.year)
    seasDeg=[]
    for i in [0, 1, 2, 3]:
        dt=ephem.localtime(seasons[i])
        dtg=360*((dt-yearStart)/(yearEnd-yearStart))%360
        #print(i, dt, dtg)
        seasDeg.append(dtg)  
    
    #seasons deg
    
    # month
    import calendar
    cY=LTN.year
    cM=LTN.month
    st, mDays = calendar.monthrange(cY, cM)
    monthEnd=datetime(LTN.year,LTN.month,mDays,23,59,59)
    monthStart=datetime(LTN.year,LTN.month,1,0,0,0)
    decMonth = (lLTN-monthStart)/(monthEnd-monthStart)
    monthPhaseRad=decMonth*2*pi
    monthPhaseDeg=decMonth*360
    
    # deal with next and previous months
    if cM != 12:
        nM=cM+1
    else:
        nM=1
    if cM != 1:
        pM=cM-1
    else:
        pM=12
    st, pmDays = calendar.monthrange(cY, pM)
    st, nmDays = calendar.monthrange(cY, nM)     

    # month- week switch
    sM=datetime(LTN.year,LTN.month,LTN.day,LTN.hour)-timedelta(days=13)
    eM=datetime(LTN.year,LTN.month,LTN.day,LTN.hour)+timedelta(days=13)
    if sM <= indSeas <= eM:
        monthSeasChDec = (indSeas-monthStart)/(monthEnd-monthStart)
        monthSeasChRad=monthSeasChDec*2*pi
        monthSeasChDeg=monthSeasChDec*360
    else:
        monthSeasChDec=None
        monthSeasChRad=None
        monthSeasChDeg=None
    
    
    # meridian
    #if LTN.hour/2==int(LTN.hour/2):
    #    bHour=LTN.hour
    #else:
    #    bHour=LTN.hour-1
    #meridStart=datetime(LTN.year,LTN.month,LTN.day,bHour,0,0)
    mS=lLTN-timedelta(hours=1)
    mMin=15*int(mS.minute/15)
    meridStart=datetime(mS.year,mS.month,mS.day,mS.hour,mMin, 0, 0)
    meridEnd=meridStart+timedelta(hours=2)
    decMeridian = (lLTN-meridStart)/(meridEnd-meridStart)
    meridPhaseRad=decMeridian*2*pi
    meridPhaseDeg=decMeridian*360
    meridCycleLoc=int(LTN.hour)/2
    
    # week
    dayWeek=LTN.isoweekday()
    STX=LTN-timedelta(days=dayWeek)
    startWeek=datetime(STX.year, STX.month, STX.day, 0, 0, 0) 
    LTX=STX+timedelta(days=7)
    endWeek=datetime(LTX.year, LTX.month, LTX.day, 0, 0, 0)
    decWeek=(lLTN-startWeek)/(endWeek-startWeek)
    weekPhaseRad=decWeek*2*pi
    weekPhaseDeg=decWeek*360

    #sW=datetime(LTN.year, LTN.month, LTN.day, 0, 0, 0)-timedelta(days=2)
    #eW=datetime(LTN.year, LTN.month, LTN.day, 0, 0, 0)+timedelta(days=3)
    sW=datetime(LTN.year, LTN.month, LTN.day, LTN.hour, LTN.minute, LTN.second)-timedelta(days=3) 
    eW=datetime(LTN.year, LTN.month, LTN.day, LTN.hour, LTN.minute, LTN.second)+timedelta(days=3) 
    
    # seasonal- week switch
    #print("startWeek, indSeas, endWeek: ", startWeek, indSeas, endWeek, sW, eW)
    if (sW <= indSeas <= eW):
        weekSeasChDec=(indSeas-startWeek)/(endWeek-startWeek)
        weekSeasChIndRad=weekSeasChDec*2*pi
        weekSeasChIndDeg=weekSeasChDec*360
    else:
        weekSeasChDec=None
        weekSeasChIndRad=None
        weekSeasChIndDeg=None
        
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
        
    xfac=1.02
    yExtra=1.02
    xr=[-xfac*pi,xfac*pi]
    yr=[-xfac*pi*yExtra,xfac*pi*yExtra]

    zLeg=[0.02, 0.22, 0.41, 0.61, 0.80]
    legX=[]
    for z in zLeg:
        legX.append(z*xr[1]+(1-z)*xr[0])
    legY=[.85*yr[0], .95*yr[0]]
        
    # memory issues: https://stackoverflow.com/questions/28757348/how-to-clear-memory-completely-of-all-matplotlib-plots
    from matplotlib.figure import Figure
    fig = Figure(figsize=(5.0,yExtra*5.0))
    ax = fig.subplots()   
    ax.set_xlim(xr)
    ax.set_ylim(yr)

    #plt.close(999)
    #fig, ax = plt.subplots(num=999,clear=True)
        
    nx, ny = 50.,50.
    xgrid, ygrid = np.mgrid[xr[0]:xr[1]:(xr[1]-xr[0])/nx,yr[0]:yr[1]:(yr[1]-yr[0])/ny]
    im = xgrid*0 + np.nan
    cmap = plt.cm.Blues
    gmap = plt.cm.Greens
    rmap = plt.cm.Reds
    omap = plt.cm.Oranges
    rainbowMap = plt.cm.rainbow
    cmap.set_bad('white')

    # set up chart
    plt.imshow(im.T, cmap=cmap, extent=xr+yr, vmin=0, vmax=1)
        
    from matplotlib.colors import Normalize
    norm = Normalize(0, 1)

    # color bands 
    cAlpha=.5

    i=0
    vPad=.20*pi/8
    #aTime=weekPhaseRad/(2*pi)*360
    aTime=0
    rAdj=90
    # negative to deal with Wedge counterclockwise rotation framework
    degs=360
    
    
    monthHeight=1.825/8*pi
    monthWidth=0.4/8*pi
    seas1Height=2.25/8*pi
    for i in range(0,12):
        wedge1=Wedge( (0,0), monthHeight, rAdj+yearPhaseDeg+i/12*degs, rAdj+yearPhaseDeg+(i+1)/12*degs, 
                     width=monthWidth, ec='black', fc=rainbowMap(i/11), linewidth=0.25, alpha=.45)
        ax.add_patch(wedge1)
        # write abbreviated month
        ycp=0.68*get_length(mnAbb[i], 6, fig)
        # lengths 8-11
        #print(ycp, "length", mnAbb[i])
        writeClock(7+(9.5-ycp)/((11-8)*0.22)-yearPhaseDeg+(i-.25)/12*360, 1.27/8*pi+vPad, mnAbb[i], ax, fontsize=6) 

    wedge1=Wedge( (0,0), seas1Height, rAdj+yearPhaseDeg, rAdj+yearPhaseDeg, width=seas1Height-1/8*pi, 
                 ec='black', linewidth=0.5, alpha=0.75)
    ax.add_patch(wedge1)

    # write season and year in annual area
    for i in range(0,4):
        yearPhaseDegC=360-yearPhaseDeg
        yrProg=(yearPhaseDegC+i/4*degs)%360
        yr=lLTN.year
        # temporary
        if yrProg < 180 and yrProg>=yearPhaseDegC:
            yr+=1
        elif 180 <= yrProg <360 and yrProg < yearPhaseDegC <360: 
            yr-=1
        #print("yearPhaseDeg, yrProg:", yearPhaseDeg, yrProg)
        yr=to_string(yr)
        sl=0.7*get_length(seas[i], 6.5, fig)
        yl=0.5*get_length(yr, 6.5, fig)
        writeClock(45-sl-yearPhaseDeg+seasDeg[int((i)%4)], 1.77/8*pi+vPad-0.05, seas[i], ax, fontsize=6.5) 
        writeClock(15-yl+yrProg, 0.97/8*pi+vPad-0.05, yr, ax, fontsize=6.5) 

        # seasonal colors
        seasAlpha=0.45
        wedge1b1=Wedge( (0,0), seas1Height, rAdj+yearPhaseDeg-seasDeg[int((i+1)%4)], 
                       rAdj+yearPhaseDeg-seasDeg[int((i)%4)], width=seas1Height-monthHeight, 
                       ec='black', fc=seasColors[i], linewidth=0.25, alpha=seasAlpha)
        ax.add_patch(wedge1b1)
        wedge1b2=Wedge( (0,0), monthHeight-monthWidth, rAdj+yearPhaseDeg-seasDeg[int((i+1)%4)], 
                       rAdj+yearPhaseDeg-seasDeg[int((i)%4)], width=monthHeight-monthWidth-1/8*pi, ec='black', 
                       fc=seasColors[i], linewidth=0.25, alpha=seasAlpha)
        ax.add_patch(wedge1b2)
        wedge1c1=Wedge( (0,0), monthHeight, rAdj+yearPhaseDeg-seasDeg[int((i+1)%4)], rAdj+yearPhaseDeg-seasDeg[int((i)%4)], 
                       width=monthWidth, ec='black', fc=seasColors[i], linewidth=0.25, alpha=.15)
        ax.add_patch(wedge1c1)
        
    # season (approx)
    sWeek=getSeasWeek()
    angle=(seasPhaseDeg+i/13*degs)%360
    # angle runs counter-clockwise with 0 at the top
    for i in range(0,13):
        angle=(seasPhaseDeg+i/13*degs)%360
        #print("i, angle, seasPhaseDeg", i, angle, seasPhaseDeg) 
        #print("i, angle, seasPhaseDeg:", i, angle, seasPhaseDeg)
        if sWeek > 6:
            if angle < 180-1/26*360 or angle >= seasPhaseDeg:
                sColor=seasColors[sN]
            else:
                sColor=seasColors[(sN+1)%4]
        else:
            if angle < 180-(2+1/26*360):
                sColor=seasColors[(sN-1)%4]
            else:
                sColor=seasColors[sN]
        wedge2=Wedge( (0,0), 3/8*pi,rAdj+angle, rAdj+seasPhaseDeg+(i+1)/13*degs, 
                     width=0.75/8*pi, ec='black', fc=sColor, linewidth=0.25, alpha=cAlpha)  # rainbowMap(i/13)
        ax.add_patch(wedge2)

        offS=13.85
        # write joint pos and meridian
        mStr=sunJointList[i]+"/"+sunMeridianList[i]
        lPt=0.525*get_length(mStr, 6, ax)
        writeClock(offS-lPt-seasPhaseDeg+i/13*degs, 2.55/8*pi+vPad-0.05, mStr, ax, fontsize=6) 
        # write seasonal point
        #print("sWeek, i, sN", sWeek, i, sN)
        if sWeek > 6:
            if i < 6:
                sPt0=SeasonalPoints[(SeasonalPoints.Season==seasons4[(sN)%4]) & (SeasonalPoints.Week==i+1)].iloc[0]
                sPt=sPt0.Meridian+'-'+  to_string(sPt0.Point)
            else:
                sPt0=SeasonalPoints[(SeasonalPoints.Season==seasons4[(sN-1)%4]) & (SeasonalPoints.Week==i+1)].iloc[0]
                sPt=sPt0.Meridian+'-'+  to_string(sPt0.Point)
        else:
            if i < 7:
                sPt0=SeasonalPoints[(SeasonalPoints.Season==seasons4[(sN-1)%4]) & (SeasonalPoints.Week==i+1)].iloc[0]
                sPt=sPt0.Meridian+'-'+  to_string(sPt0.Point)
            else:
                sPt0=SeasonalPoints[(SeasonalPoints.Season==seasons4[(sN-2)%4]) & (SeasonalPoints.Week==i+1)].iloc[0]
                sPt=sPt0.Meridian+'-'+  to_string(sPt0.Point)
        lPt=0.6*get_length(sPt, 6, ax)
        writeClock(offS-lPt-seasPhaseDeg+i/13*degs, 2.27/8*pi+vPad-0.05, sPt, ax, fontsize=6) 
        
    # add wedges around season change
    wedge2=Wedge( (0,0), 3/8*pi, rAdj+180-0.5/(3*13)*degs, rAdj+180+0.5/(3*13)*degs, 
                 width=0.75/8*pi, ec='black', fc='black', linewidth=0.25, alpha=0.9)
    ax.add_patch(wedge2)
    wedge2=Wedge( (0,0), 3/8*pi, rAdj+180-1.5/(3*13)*degs, rAdj+180+1.5/(3*13)*degs, 
                 width=0.75/8*pi, ec='black', fc='black', linewidth=0.25, alpha=0.5)
    ax.add_patch(wedge2)
        
    # write season first place
    #writeClock(-28, 1.9/8*pi+vPad-0.05, seas[2], ax, fontsize=8) 

    
    # lunar month
    for i in range(0,30):
        mColor=abs(15-i)/15
        wedge3=Wedge((0,0), 4/8*pi, rAdj-moonPhaseDeg+i/30*degs, rAdj-moonPhaseDeg+(i+1)/30*degs, width=1/8*pi, ec='black', linewidth=0.5, fc=cmap(mColor), alpha=.4)
        ax.add_patch(wedge3)
        # lunar cycle number -- taken out of image
        #writeClock(moonPhaseDeg+i/30*degs, 3/8*pi+vPad-.1, ""+to_string(i+1), ax, fontsize=5) 
        # body pos
        bcp=0.68*get_length(moonSeq[i+1][0], 6, fig)
        writeClock(moonPhaseDeg-0.5+(8-bcp)/4*1.25+i/30*degs, 3/8*pi+vPad+.17, moonSeq[i+1][0], ax, fontsize=6) 
        # lunar meridian
        mcp=0.68*get_length(moonSeq[i+1][1], 6, fig)
        # lengths 6-10 # (8-mcp)/(4*1.0)
        #print(mcp, "length", moonSeq[i+1][1])
        writeClock(moonPhaseDeg-0.45+(8-mcp)/4*1.25+i/30*degs, 3/8*pi+vPad-.02, moonSeq[i+1][1], ax, fontsize=6) 
        # add moon phase graphics
        phase=i/30*degs
        lAngleRad=(-decMoon+i/30+6.25/360)*2*pi   
        lAngleDeg=lAngleRad/(2*pi)*360
        #print("i, decMoon, lAngle, phase:", i, decMoon, lAngleDeg, phase) 
        xLoc=np.sin(lAngleRad)*3.35/8*pi
        yLoc=np.cos(lAngleRad)*3.35/8*pi
        sy.moonPhases((xLoc, yLoc), 1/30*pi, phase, ax, -lAngleDeg, .25)

    # calendar month
    day_of_year = lLTN.timetuple().tm_yday
    mPD=(-monthPhaseDeg)%360
    vertPad=.40*pi/8
    # write current month
    # location changes around month change
    # regular in current month
    # month lengths ... current and next
    # current month needs to be redone with get_length
    cmLenAdj=15
    nmLenAdj=6
    pmLenAdj=25
    if 20 < mPD < 340: 
        writeClock(-cmLenAdj, 4.07/8*pi+vPad, months[LTN.month-1], ax, fontsize=7) 
    # just before change of month current month starts shifting to the left
    elif mPD < 20:
        writeClock(-cmLenAdj-(pmLenAdj-cmLenAdj)/20*(20-mPD), 4.07/8*pi+vPad, months[LTN.month-1], ax, fontsize=7) 
    # just after change of month next month turns into current month
    else: 
        writeClock(nmLenAdj-(cmLenAdj+nmLenAdj)/20*(360-mPD), 4.07/8*pi+vPad, months[LTN.month-1], ax, fontsize=7) 
        
    # current month
    for i in range(0,mDays):
        imAngle1=(-monthPhaseDeg+i/mDays*degs)%360
        imAngle2=(-monthPhaseDeg+(i+1)/mDays*degs)%360
        if imAngle1 < mPD or imAngle1 > 180:
            wedge4=Wedge( (0,0), 5/8*pi, rAdj-imAngle2, rAdj-imAngle1, width=1/8*pi, ec='grey', 
                fc=rainbowMap(i/(mDays-1)), linewidth=0.5, alpha=cAlpha) 
                # old fc= rainbowMap(i/(mDays-1)) # new cM/11
            ax.add_patch(wedge4)
            # write day
            if i+1<10:
                spx=2
            else:
                spx=0
            writeClock(spx+imAngle1, 3.65/8*pi+vertPad, to_string(i+1), ax, fontsize=5) 
            # write point of the day
            cix=day_of_year+i-lLTN.day+2
            cp=AcuPoints[AcuPoints.DaySeq==cix].Point.values[0]
            lcp=0.68*get_length(str(cp), 6, fig)
            #print(lcp, "length", cp)
            writeClock(-2+(18-lcp)/4+imAngle1, 4.15/8*pi+vertPad, cp, ax, fontsize=6)         
            #print("i-c, cp, mPD, imAngle1: ", i, cp, mPD, imAngle1) 

    # next month
    if mPD <= 180 - 1/(2*mDays)*degs:
        # write month
        writeClock(mPD+nmLenAdj, 4.07/8*pi+vPad, months[LTN.month-1+1], ax, fontsize=7) 
        for i in range(0,nmDays):
            imAngle1=(-monthPhaseDeg+i/nmDays*degs)%360
            imAngle2=(-monthPhaseDeg+(i+1)/nmDays*degs)%360
            if mPD <= imAngle1 <= 180-1/nmDays*degs:
                wedge4=Wedge( (0,0), 5/8*pi, rAdj-imAngle2, rAdj-imAngle1, width=1/8*pi, ec='grey', 
                    fc=rainbowMap(i/(mDays-1)), linewidth=0.5, alpha=cAlpha)
                ax.add_patch(wedge4)
                # write day
                if i+1<10:
                    spx=2
                else:
                    spx=0
                writeClock(spx+imAngle1, 3.65/8*pi+vertPad, to_string(i+1), ax, fontsize=5) 
                # write point of the day ... mDays is correct here!
                cix=day_of_year+i-lLTN.day+2+mDays
                cp=AcuPoints[AcuPoints.DaySeq==cix].Point.values[0]
                lcp=0.68*get_length(str(cp), 6, fig)
                #print(lcp, "length", cp)
                writeClock(-2+(18-lcp)/4+imAngle1, 4.15/8*pi+vertPad, cp, ax, fontsize=6)         
                #print("i-n, cp, mPD, imAngle1: ", i, cp, mPD, imAngle1)             

    # previous month
    # write month
    if mPD==0 or 180 < mPD: 
        writeClock(imAngle1-pmLenAdj, 4.07/8*pi+vPad, months[LTN.month-1-1], ax, fontsize=7) 
        for i in range(pmDays, 0, -1):
            imAngle1=(-monthPhaseDeg-(pmDays-1-i)/pmDays*degs)%360
            imAngle2=(-monthPhaseDeg-(pmDays-1-i+1)/pmDays*degs)%360
            if 180 < imAngle1 < mPD or (180 < imAngle1 < 360 and mPD==0):
                wedge4=Wedge( (0,0), 5/8*pi, rAdj-imAngle2, rAdj-imAngle1, width=1/8*pi, ec='grey', 
                    fc=rainbowMap(i/(pmDays-1)), linewidth=0.5, alpha=cAlpha)
                ax.add_patch(wedge4)
                # write day
                if i+1<10:
                    spx=2
                else:
                    spx=0
                writeClock(spx+imAngle1, 3.65/8*pi+vertPad, to_string(i+1), ax, fontsize=5) 
                # write point of the day
                cix=day_of_year+i-lLTN.day+2-pmDays
                cp=AcuPoints[AcuPoints.DaySeq==cix].Point.values[0]
                lcp=0.68*get_length(str(cp), 6, fig)
                #print(lcp, "length", cp)
                writeClock(-2+(18-lcp)/4+imAngle1, 4.15/8*pi+vertPad, cp, ax, fontsize=6)         
                #print("i-p, cp, mPD, imAngle1: ", i, cp, mPD, imAngle1)             

    # add wedges around month change
    wedge2=Wedge( (0,0), 5/8*pi, rAdj+180-0.33/nmDays*degs, rAdj+180+0.33/nmDays*degs, 
        width=1/8*pi, ec='black', fc='black', linewidth=0.25, alpha=0.9)
    ax.add_patch(wedge2)
    wedge2=Wedge( (0,0), 5/8*pi, rAdj+180-1/nmDays*degs, rAdj+180+1/nmDays*degs, 
        width=1/8*pi, ec='grey', fc='black', linewidth=0.25, alpha=0.5)
    ax.add_patch(wedge2)

    # month seas change
    if monthSeasChDec!=None:
        #print("month seas ch", monthSeasChDeg, )
        wedge4=Wedge((0,0), 5/8*pi, rAdj+monthPhaseDeg-monthSeasChDeg-1, rAdj+monthPhaseDeg-monthSeasChDeg+.1, 
                     width=1/8*pi, ec='black', fc='yellow', linewidth=0.5, alpha=.4) 
        ax.add_patch(wedge4)
        wedge4=Wedge((0,0), 5/8*pi, rAdj+monthPhaseDeg-monthSeasChDeg-.1, rAdj+monthPhaseDeg-monthSeasChDeg+.1, 
                     width=1/8*pi, ec='black', fc='black', linewidth=0.5, alpha=0.5) 
        ax.add_patch(wedge4)
        
        
    # week
    chakraFn=[sy.Muladahara, sy.Swadisthana, sy.Manipura, sy.Anahata, sy.Wishuddha, None, None]
    #chakraFn=[sy.Muladahara, sy.Muladahara, sy.Muladahara, sy.Muladahara, sy.Muladahara, sy.Muladahara, None]
    #chakraFn=[sy.Swadisthana, sy.Swadisthana, sy.Swadisthana, sy.Swadisthana, sy.Swadisthana, sy.Swadisthana, sy.Swadisthana]
    
    chakraColors = {0 : 'red' , 1 : 'orange', 2 : 'gold', 3 : 'green' , 4 : 'steelblue', 5 : 'indigo', 6 : 'violet'} 
    
    i=0
    for day in DaysOfTheWeek:
        wedge5=Wedge((0,0), 6/8*pi, rAdj+weekPhaseDeg+i/7*degs, 
                    rAdj+weekPhaseDeg+(i+1)%6/7*degs, width=1/8*pi, ec='black', fc=chakraColors[i], linewidth=0.5, alpha=.3) 
                    # rainbowMap(i/6)
        ax.add_patch(wedge5)
        # write Chakra name
        chakDayPosAdj={'Sunday' : 10.5,'Monday': 9.25,'Tuesday': 12.5,'Wednesday': 9.25,'Thursday': 11,'Friday': 19,'Saturday': 12}
        writeClock(-weekPhaseDeg+chakDayPosAdj[day]+i/7*degs, 5.2/8*pi+vPad, WeekDays.Chakra[i], ax, fontsize=9) 
        # write day of week
        dayPosAdj={'Sunday' : 15,'Monday': 11,'Tuesday': 14,'Wednesday': 11,'Thursday': 13,'Friday': 18,'Saturday': 14}
        writeClock(-weekPhaseDeg+dayPosAdj[day]+i/7*degs, 4.8/8*pi+vPad, day, ax, fontsize=8) 
        # chakra symbols
        inDent=6
        cFn=chakraFn[i]
        x=np.sin(-weekPhaseRad+i/7*2*np.pi+inDent/360*2*np.pi)*(5.3/8*pi+vPad) # 
        y=np.cos(-weekPhaseRad+i/7*2*np.pi+inDent/360*2*np.pi)*(5.3/8*pi+vPad)
        if cFn!=None:
            cFn((x,y), 1/10*np.pi, ax,(weekPhaseDeg-i/7*degs-inDent), alpha=1, lw=.5)
        x=np.sin(-weekPhaseRad+(i+1)%7/7*2*np.pi-inDent/360*2*np.pi)*(5.3/8*pi+vPad) # 
        y=np.cos(-weekPhaseRad+(i+1)%7/7*2*np.pi-inDent/360*2*np.pi)*(5.3/8*pi+vPad)
        if cFn!=None:
            cFn((x,y), 1/10*np.pi, ax,(weekPhaseDeg-(i+1)%7/7*degs+inDent), alpha=1, lw=.5)
        #print(i, (weekPhaseDeg+i/7*degs)%360)
        i+=1

    # season change
   #print("i, weekSeasChIndDeg, weekPhaseDeg: ", i, weekSeasChIndDeg, weekPhaseDeg)
    if weekSeasChDec!=None:
        wedge5=Wedge((0,0), 6/8*pi, rAdj+weekPhaseDeg-weekSeasChIndDeg-1, rAdj+weekPhaseDeg-weekSeasChIndDeg+1, 
                     width=1/8*pi, ec='black', fc='yellow', linewidth=0.5, alpha=.4) 
        ax.add_patch(wedge5)
        wedge5=Wedge((0,0), 6/8*pi, rAdj+weekPhaseDeg-weekSeasChIndDeg-.1, rAdj+weekPhaseDeg-weekSeasChIndDeg+.1, 
                     width=1/8*pi, ec='black', fc='black', linewidth=0.5, alpha=0.5) 
        ax.add_patch(wedge5)

    # day's hours
    for i in range(0, 24):
        wedge6=Wedge( (0,0), 7/8*pi, rAdj+dayPhaseDeg+i/24*degs, rAdj+dayPhaseDeg+(i+1)/24*degs, 
                     width=1/8*pi, ec='black', fill=False, linewidth=0.25, alpha=cAlpha)
        ax.add_patch(wedge6)
        #writeClock(-dayPhaseDeg+i/24*360, 6/8*pi+vPad, " "+to_string(i), ax, fontsize=10)
        if i < 10:
            writeClock(-5+-dayPhaseDeg+i/24*degs, 5.85/8*pi+vPad, to_string(i)+":00", ax, fontsize=7) 
        else:
            writeClock(-5.8+-dayPhaseDeg+i/24*degs, 5.85/8*pi+vPad, to_string(i)+":00", ax, fontsize=7) 
        # write meridians
        j=i/2
        if j==int(i/2):
            j=int(j)
            curMerid=Meridians[MeridianList[j]]
            lj=len(curMerid)
            splj=12-0.75*lj
            writeClock(splj+2/12*360-dayPhaseDeg+j/12*360, 6.25/8*pi+vPad, curMerid, ax, fontsize=7) 
            # meridian colors
            traditional=True
            if traditional==True:
                mColor=meridianColors[MeridianList[11-j]]
                merAdj=-60
            else:
                mColor=rainbowMap(j/11)
                merAdj=0
            wedge6=Wedge((0,0), 7/8*pi, rAdj+dayPhaseDeg+j/12*degs+merAdj, 
                         rAdj+dayPhaseDeg+(j+1)/12*degs+merAdj, width=1/8*pi, ec='black', fc=mColor, 
                         linewidth=0.5, alpha=cAlpha)
            ax.add_patch(wedge6)

    # day seas change
    if daySeasChDec!=None:
        wedge6=Wedge((0,0), 7/8*pi, rAdj+daySeasChIndDeg-1, rAdj+daySeasChIndDeg+1, 
                     width=1/8*pi, ec='black', fc='yellow', linewidth=0.5, alpha=.3) 
        ax.add_patch(wedge6)
        wedge6=Wedge((0,0), 7/8*pi, rAdj+daySeasChIndDeg-.1, rAdj+daySeasChIndDeg+.1, 
                     width=1/8*pi, ec='black', fc='black', linewidth=1, alpha=1) 
        ax.add_patch(wedge6)
    
    # first identify the :45 and :00 meridian change points
    meridz=[]
    jz=np.zeros(len(timeDF))
    for j in range(len(timeDF)):
        meridz.append(timeDF.iloc[j]['Point'][:2])
        cT=timeDF.iloc[j]['Time']
        sT=cT.split(':')
        if sT[1] in ['00','45']:
            sti=int(sT[0])
            if sti/2==int(sti/2):
                if sT[1]=='00':
                    jz[j]=2
            elif sT[1]=='45':
                jz[j]=1                    
    
    # meridians
    j=0
    lastM=timeDF.iloc[0]['Point'][:2]    
    for i in range(0,8):
        # write time
        writeClock(-5+-meridPhaseDeg+i/8*360, 6.85/8*pi+vPad, timeDF.iloc[j]['Time'], ax, fontsize=7)
        cT=timeDF.iloc[j]['Time']
        if j < len(timeDF):
            if timeDF.iloc[j]['Time']==timeDF.iloc[j+1]['Time']:
                writeClock(0.25-meridPhaseDeg+i/8*360, 7.32/8*pi+vPad, 
                           timeDF.iloc[j]['Point']+" "+timeDF.iloc[j]['English Name'], ax, fontsize=7)
                writeClock(3.5-meridPhaseDeg+i/8*360, 6.93/8*pi+vPad, 
                           timeDF.iloc[j+1]['Point']+" "+timeDFp.iloc[j+1]['English Name'], ax, fontsize=7.5)
                curM=timeDF.iloc[j+1]['Point'][:2]
            else:
                writeClock(.25-meridPhaseDeg+i/8*360, 7.2/8*pi+vPad, 
                           timeDF.iloc[j]['Point']+": "+timeDF.iloc[j]['English Name'], ax, fontsize=7.5)
                curM=timeDF.iloc[j]['Point'][:2]
        else:
            writeClock(0.25-meridPhaseDeg+i/8*360, 7.2/8*pi+vPad, 
                       timeDF.iloc[j]['Point']+": "+timeDF.iloc[j]['English Name'], ax, fontsize=8)
            lastM=curM
            curM=timeDF.iloc[j]['Point'][:2]
        
        # increment j and set time point cell colors
        if jz[j]==0:   #timeDF.iloc[j]['Time']!=timeDF.iloc[j+1]['Time'] and timeDF.iloc[j]['Time']!=timeDF.iloc[j-1]['Time']:
            # regular cells
            wedge7=Wedge((0,0), 8/8*pi, rAdj+meridPhaseDeg-(i+1)/8*degs, rAdj+meridPhaseDeg-(i)/8*degs, 
                         width=1/8*pi, ec='black', color=meridianColors[meridz[j]], linewidth=1/2, alpha=cAlpha)
            ax.add_patch(wedge7)             
            j+=1
        elif jz[j]==2:   #timeDF.iloc[j]['Time']==timeDF.iloc[j+1]['Time']:
            # fill of top half of box
            pie1, pie2 = pieWedge(loc=(0,0), radius=pi, width=1/8*pi, 
                    absStartAngle=-meridPhaseDeg+i/8*degs, relEndAngle=1/8*degs, virtRelStartAngle=-1/8*degs, 
                    virtSizeAngle=2/8*degs, startClose=True, 
                    color1=meridianColors[meridz[j]], color2=meridianColors[meridz[j+1]], 
                    alpha1=cAlpha, alpha2=cAlpha, linewidth1=1/3, linewidth2=1/3)
            ax.add_patch(pie1)
            ax.add_patch(pie2)
            j+=2
        else:
            # fill of top half of box
            if j<len(timeDF)-2:
                jj=j+2
            else:
                jj=len(timeDF)-1
            
            pie1, pie2 = pieWedge(loc=(0,0), radius=pi, width=1/8*pi, 
                    absStartAngle=-meridPhaseDeg+i/8*degs, relEndAngle=1/8*degs, virtRelStartAngle=0, 
                    virtSizeAngle=2/8*degs, startClose=True, 
                    color1=meridianColors[meridz[j]], color2=meridianColors[meridz[jj]], 
                    alpha1=cAlpha, alpha2=cAlpha, linewidth1=1/3, linewidth2=1/3)
            ax.add_patch(pie1)
            ax.add_patch(pie2)
            j+=1

        # dividing line wedges    
        wedge7=Wedge((0,0), 8/8*pi, rAdj+meridPhaseDeg-3, rAdj+meridPhaseDeg+3, width=1/8*pi, 
                     ec='black', facecolor='black', linewidth=1, alpha=1.0)
        ax.add_patch(wedge7)
        # dividing line wedges    
        wedge7=Wedge((0,0), 8/8*pi, rAdj+meridPhaseDeg-10, rAdj+meridPhaseDeg+10, width=1/8*pi, 
                     color='grey', linewidth=1, alpha=0.5)
        ax.add_patch(wedge7)

    # vertical 
    wedge0=Wedge( (0,0), yExtra*xfac*pi, 89, 91, ec='black', fc='yellow', width=(yExtra*xfac-1/8)*pi, alpha=0.5) 
    ax.add_patch(wedge0)
    
    # yin yang symbol
    yinyang=sy.YinYang((0,0), 1/8*pi, ax)
    
    np.vectorize(lambda ax:ax.axis('off'))(ax)
    twDay=LTN.isoweekday
    return(fig, ax, xfac, rAdj, degs, yearPhaseDeg, rainbowMap, yExtra, curM)

  