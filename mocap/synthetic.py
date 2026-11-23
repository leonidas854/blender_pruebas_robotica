"""Fixture analítico, NO captura humana ni salida de FreeMoCap."""
import math

def pose(t):
    p={i:(0.,0.,.6) for i in range(33)}
    p.update({0:(0,-.08,.75),7:(.08,0,.7),8:(-.08,0,.7),
              11:(.21,0,.48),12:(-.21,0,.48),23:(.1,0,0),24:(-.1,0,0)})
    for sign,ids,phase in [(1,(11,13,15,17,19,21,23,25,27,29,31),0),
                           (-1,(12,14,16,18,20,22,24,26,28,30,32),.7)]:
        sh,el,wr,pk,ix,th,hip,knee,ank,heel,toe=ids
        lift=.55+.4*math.sin(t*1.1+phase)
        flex=.65+.55*math.sin(t*1.4+phase)
        a=(sign*math.sin(lift),0,-math.cos(lift))
        b=(sign*math.sin(lift)*math.cos(flex),-math.sin(flex),-math.cos(lift)*math.cos(flex))
        p[el]=tuple(x+.25*y for x,y in zip(p[sh],a))
        p[wr]=tuple(x+.24*y for x,y in zip(p[el],b))
        for i in (pk,ix,th):p[i]=tuple(x+.07*y for x,y in zip(p[wr],b))
        p[knee]=(sign*.1,-.02,-.4);p[ank]=(sign*.1,0,-.8)
        p[heel]=(sign*.1,.02,-.84);p[toe]=(sign*.1,-.15,-.84)
    # Inversa exacta de (x,z,-y), sin reflexión lateral.
    return [dict(x=p[i][0],y=-p[i][2],z=p[i][1],visibility=1.) for i in range(33)]
