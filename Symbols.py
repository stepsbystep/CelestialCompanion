# symbols 

# def moonPhases(loc, scale, phase, ax, rotate=0, alpha=1):
# def YinYang(loc, scale, ax, rotate=0):

# def Muladahara(loc, scale, ax, rotate=0, alpha=1):
# def Manipura(loc, scale, ax, rotate=0, alpha=1):
# def Anahata(loc, scale, ax, rotate=0, alpha=1):
# def Swadistana(loc, scale, ax, rotate=0, alpha=1):
# def Wishuddha(loc, scale, ax, rotate=0, alpha=1):

import matplotlib
# moom phasee shape with rotation
def moonPhases(loc, scale, phase, ax, rotate=0, alpha=1, lw=1):
    # returns a list of patches that constitute the yin yang symbol
    # create yin yang out shape pologon
    # places symbol in matplotlib figure with axis handle ax
    
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Polygon
    from matplotlib.patches import Ellipse

    # create outline of shape
    N=50
    LS=np.linspace(0,np.pi,N)
    X0=np.sin(LS)
    X1=np.cos(LS)
    
    left0=loc[0]-scale*X0
    left1=loc[1]+scale*X1
    right0=loc[0]+scale*X0
    right1=loc[1]+scale*X1

    leftA=np.vstack((left0,left1)).T
    rightA=np.vstack((right0,right1)).T

    if phase < 180:
        left0=loc[0]+np.cos(phase/360*2*np.pi)*scale*X0
        left1=loc[1]-scale*X1
        right0=loc[0]+np.cos(phase/360*2*np.pi)*scale*X0
        right1=loc[1]-scale*X1
        leftB=np.vstack((left0,left1)).T
        rightB=np.vstack((right0,right1)).T
    else:
        left0=loc[0]-np.cos(phase/360*2*np.pi)*scale*X0
        left1=loc[1]-scale*X1
        right0=loc[0]-np.cos(phase/360*2*np.pi)*scale*X0
        right1=loc[1]-scale*X1
        leftB=np.vstack((left0,left1)).T
        rightB=np.vstack((right0,right1)).T
    
    right=np.concatenate((rightA,rightB))
    left=np.concatenate((leftA,leftB))
    
    #left=[]
    #right=[]
    #for x,y in zip(X0,X1):
    #    left.append((loc[0]-scale*x, loc[1]+scale*y))
    #    right.append((loc[0]+scale*x, loc[1]+scale*y))
    #for x,y in zip(X0,X1):
    #    if phase < 180:
    #        left.append((loc[0]+np.cos(phase/360*2*np.pi)*scale*x, loc[1]-scale*y))
    #        right.append((loc[0]+np.cos(phase/360*2*np.pi)*scale*x, loc[1]-scale*y))
    #    else:
    #        left.append((loc[0]-np.cos(phase/360*2*np.pi)*scale*x, loc[1]-scale*y))
    #        right.append((loc[0]-np.cos(phase/360*2*np.pi)*scale*x, loc[1]-scale*y))

    # doing the rotation
    ts = ax.transData
    tr = matplotlib.transforms.Affine2D().rotate_deg_around(loc[0],loc[1], rotate)
    trans = tr + ts    
    
    if phase < 180:
        leftMoon=Polygon(left, closed=True, edgecolor='black', linewidth=lw, facecolor='black', transform=trans, alpha=alpha)
        rightMoon=Polygon(right, closed=True, edgecolor='black', linewidth=lw, facecolor='white', transform=trans, alpha=alpha)
    else:
        leftMoon=Polygon(left, closed=True, edgecolor='black', linewidth=lw, facecolor='white', transform=trans, alpha=alpha)
        rightMoon=Polygon(right, closed=True, edgecolor='black', linewidth=lw, facecolor='black', transform=trans, alpha=alpha)

    for pa in [leftMoon, rightMoon]:
    #, circ, circ2, circ3]:
        ax.add_patch(pa)

    return()


def YinYang(loc, scale, ax, rotate=0, alpha=1, lw=1):
    # returns a list of patches that constitute the yin yang symbol
    # create yin yang out shape pologon
    # places symbol in matplotlib figure with axis handle ax
    
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Polygon
    from matplotlib.patches import Ellipse

    # create outline of shape
    N=100
    LS=np.linspace(0,np.pi,N)
    X0=np.sin(LS)
    X1=np.cos(LS)

    z=[]
    for x,y in zip(X0,X1):
        z.append((-loc[0]-scale*x,loc[1]+scale*y))
    for k in range(0,int(N/2)):
        z.append((loc[0]+scale*.5*np.sin(2*LS[k]),-.5*scale+loc[1]+scale*-.5*np.cos(2*LS[k])))
    for k in range(int(N/2)+1,N):
        z.append((loc[0]+scale*.5*np.sin(2*LS[k]),.5*scale+loc[1]+scale*.5*np.cos(2*LS[k])))

    # doing the rotation
    ts = ax.transData
    tr = matplotlib.transforms.Affine2D().rotate_deg_around(loc[0],loc[1], rotate)
    trans = tr + ts    
        
    yinYangz=Polygon(z, closed=True, color='black', transform=trans)
    circ=Ellipse(loc,2*scale,2*scale,fill=None, linewidth=lw, transform=trans)
    circ2=Ellipse((loc[0],loc[1]+1/2*scale),1/4*scale,1/4*scale, color='black', transform=trans)
    circ3=Ellipse((loc[0],loc[1]-1/2*scale),1/4*scale,1/4*scale, color='white', transform=trans)

    for pa in [yinYangz, circ, circ2, circ3]:
        ax.add_patch(pa)

    return()


# Muladahara chakra simple symbol
def Muladahara(loc, scale, ax, rotate=0, alpha=1, lw=1):
    # returns a list of patches that constitute the yin yang symbol
    # create yin yang out shape pologon
    # places symbol in matplotlib figure with axis handle ax
    
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Polygon
    from matplotlib.patches import Ellipse
    
    outerCirc=Ellipse(loc, width=scale, height=scale, edgecolor='black', linewidth=lw, facecolor='black', fill=None)#  fill=None) 
    
    disp=1/8
    verticies= ([(disp+0.0)*2*np.pi, (disp+0.25)*2*np.pi, (disp+0.5)*2*np.pi, (disp+0.75)*2*np.pi])
    
    X0=np.sin(verticies)
    X1=np.cos(verticies)

    redFac=.90
    z=[]
    for x, y in zip(X0, X1):
        z.append((loc[0]+redFac*scale*1/2*x,loc[1]+redFac*scale*1/2*y))

    # doing the rotation
    ts = ax.transData
    tr = matplotlib.transforms.Affine2D().rotate_deg_around(loc[0],loc[1], rotate)
    trans = tr + ts    
    
    square=Polygon(z, closed=True, edgecolor='black', linewidth=lw, facecolor='black', fill=None, transform=trans, alpha=alpha)

    for pa in [outerCirc, square]:
        ax.add_patch(pa)

    return()

# Manipura
def Manipura(loc, scale, ax, rotate=0, alpha=1, lw=1):
    # returns a list of patches that constitute the yin yang symbol
    # create yin yang out shape pologon
    # places symbol in matplotlib figure with axis handle ax
    
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Polygon
    from matplotlib.patches import Ellipse
    
    outerCirc=Ellipse(loc, width=scale, height=scale, edgecolor='black', linewidth=lw, facecolor='black', fill=None)#  fill=None) 
    
    disp=np.pi
    verticies= [disp+0.0*2*np.pi, disp+1/3*2*np.pi, disp+2/3*2*np.pi]
    
    X0=np.sin(verticies)
    X1=np.cos(verticies)

    redFac=.90
    z=[]
    for x, y in zip(X0, X1):
        z.append((loc[0]+redFac*scale*1/2*x,loc[1]+redFac*scale*1/2*y))
    
    # doing the rotation
    ts = ax.transData
    tr = matplotlib.transforms.Affine2D().rotate_deg_around(loc[0],loc[1], rotate)
    trans = tr + ts    
    
    downTri=Polygon(z, closed=True, edgecolor='black', linewidth=lw, facecolor='black', fill=None, transform=trans, alpha=alpha)

    for pa in [outerCirc, downTri]:
        ax.add_patch(pa)

    return()


# Anahata
def Anahata(loc, scale, ax, rotate=0, alpha=1, lw=1):
    # returns a list of patches that constitute the yin yang symbol
    # create yin yang out shape pologon
    # places symbol in matplotlib figure with axis handle ax
    
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Polygon
    from matplotlib.patches import Ellipse
    
    outerCirc=Ellipse(loc, width=scale, height=scale, edgecolor='black', linewidth=lw, facecolor='black', fill=None)#  fill=None) 
    
    disp=np.pi
    verticies= [disp+0.0*2*np.pi, disp+1/3*2*np.pi, disp+2/3*2*np.pi]
    verticies2= [0.0*2*np.pi, 1/3*2*np.pi, 2/3*2*np.pi]
    
    X0=np.sin(verticies)
    X1=np.cos(verticies)

    Y0=np.sin(verticies2)
    Y1=np.cos(verticies2)

    redFac=.90
    z=[]
    for x, y in zip(X0, X1):
        z.append((loc[0]+redFac*scale*1/2*x,loc[1]+redFac*scale*1/2*y))

    redFac=.90
    zz=[]
    for x, y in zip(Y0, Y1):
        zz.append((loc[0]+redFac*scale*1/2*x,loc[1]+redFac*scale*1/2*y))
        

    # doing the rotation
    ts = ax.transData
    tr = matplotlib.transforms.Affine2D().rotate_deg_around(loc[0],loc[1], rotate)
    trans = tr + ts    
    
    downTri=Polygon(z, closed=True, edgecolor='black', linewidth=lw, facecolor='black', fill=None, transform=trans, alpha=alpha)
    upTri=Polygon(zz, closed=True, edgecolor='black', linewidth=lw, facecolor='black', fill=None, transform=trans, alpha=alpha)

    for pa in [outerCirc, downTri, upTri]:
        ax.add_patch(pa)

    return()


# Swadisthana
def Swadisthana(loc, scale, ax, rotate=0, alpha=1, lw=1):
    # returns a list of patches that constitute the yin yang symbol
    # create yin yang out shape pologon
    # places symbol in matplotlib figure with axis handle ax
    
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Polygon
    from matplotlib.patches import Ellipse
    
    outerCirc=Ellipse(loc, width=scale, height=scale, edgecolor='black', linewidth=lw, facecolor='black', fill=None)#  fill=None) 
        
    #XmoonPhases(loc, 0.4*scale, 50, ax, rotate=270, alpha=1)
    mRotate=rotate+270
    phase=50
    mScale=0.5*0.75*scale
    
    # create outline of shape
    N=100
    LS=np.linspace(0,np.pi,N)
    X0=np.sin(LS)
    X1=np.cos(LS)

    left=[]
    right=[]
    for x,y in zip(X0,X1):
        left.append((loc[0]-mScale*x,loc[1]+mScale*y))
        right.append((loc[0]+mScale*x,loc[1]+mScale*y))
    for x,y in zip(X0,X1):
        if phase < 180:
            right.append((loc[0]+np.cos(phase/360*2*np.pi)*mScale*x, loc[1]-mScale*y))
        else:
            right.append((loc[0]-np.cos(phase/360*2*np.pi)*mScale*x, loc[1]-mScale*y))

    from matplotlib.transforms import Affine2D
    # doing the rotation
    ts = ax.transData
    tr = Affine2D().rotate_deg_around(loc[0],loc[1], mRotate)
    trans = tr + ts    
    
    if phase < 180:
        leftMoon=Polygon(left, closed=True, edgecolor='black', linewidth=lw, fill=None, transform=trans, alpha=alpha)
        rightMoon=Polygon(right, closed=True, edgecolor='black', linewidth=lw, fill=None, transform=trans, alpha=alpha)
    else:
        leftMoon=Polygon(left, closed=True, edgecolor='black', linewidth=lw, fill=None, transform=trans, alpha=alpha)
        rightMoon=Polygon(right, closed=True, edgecolor='black', linewidth=lw, fill=None, transform=trans, alpha=alpha)

    for pa in [outerCirc, rightMoon]:
        ax.add_patch(pa)

    return()


def Wishuddha(loc, scale, ax, rotate=0, alpha=1, lw=1):
    
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Polygon
    from matplotlib.patches import Ellipse

    # redfac is the triangle size relative to the outer circle
    redFac=.925
    inCircScale=.48*redFac*scale
    outerCirc=Ellipse(loc, width=scale, height=scale, edgecolor='black', linewidth=lw, facecolor='black', fill=None)#  fill=None) 
    innerCirc=Ellipse(loc, width=inCircScale, height=inCircScale, edgecolor='black', linewidth=lw, facecolor='black', fill=None)#  fill=None) 
    
    disp=np.pi
    verticies= [disp+0.0*2*np.pi, disp+1/3*2*np.pi, disp+2/3*2*np.pi]
    
    X0=np.sin(verticies)
    X1=np.cos(verticies)

    z=[]
    for x, y in zip(X0, X1):
        z.append((loc[0]+redFac*scale*1/2*x,loc[1]+redFac*scale*1/2*y))
    
    # doing the rotation
    ts = ax.transData
    tr = matplotlib.transforms.Affine2D().rotate_deg_around(loc[0],loc[1], rotate)
    trans = tr + ts    
    
    downTri=Polygon(z, closed=True, edgecolor='black', linewidth=lw, facecolor='black', fill=None, transform=trans, alpha=alpha)

    for pa in [outerCirc, innerCirc, downTri]:
        ax.add_patch(pa)

    return()
