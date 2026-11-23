"""Unidades SI, cuaterniones wxyz, transporte validado y filtro One Euro."""
import json
import math
import socket
import time
import uuid

NAMES = ('NOSE LEFT_EYE_INNER LEFT_EYE LEFT_EYE_OUTER RIGHT_EYE_INNER RIGHT_EYE '
         'RIGHT_EYE_OUTER LEFT_EAR RIGHT_EAR MOUTH_LEFT MOUTH_RIGHT LEFT_SHOULDER '
         'RIGHT_SHOULDER LEFT_ELBOW RIGHT_ELBOW LEFT_WRIST RIGHT_WRIST LEFT_PINKY '
         'RIGHT_PINKY LEFT_INDEX RIGHT_INDEX LEFT_THUMB RIGHT_THUMB LEFT_HIP RIGHT_HIP '
         'LEFT_KNEE RIGHT_KNEE LEFT_ANKLE RIGHT_ANKLE LEFT_HEEL RIGHT_HEEL '
         'LEFT_FOOT_INDEX RIGHT_FOOT_INDEX').split()
SEGMENTS = {'upper_arm.L': (11, 13), 'forearm.L': (13, 15),
            'upper_arm.R': (12, 14), 'forearm.R': (14, 16),
            'thigh.L': (23, 25), 'shin.L': (25, 27),
            'thigh.R': (24, 26), 'shin.R': (26, 28),
            'foot.L': (29, 31), 'foot.R': (30, 32),
            'hand.L': (15, 19), 'hand.R': (16, 20)}

def sub(a, b): return tuple(x-y for x, y in zip(a, b))
def dot(a, b): return sum(x*y for x, y in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(a): return math.sqrt(dot(a, a))
def unit(a):
    n = norm(a)
    if not math.isfinite(n) or n < 1e-8: raise ValueError('Vector degenerado')
    return tuple(v/n for v in a)

def angle(a, b): return math.acos(max(-1., min(1., dot(unit(a), unit(b)))))
def mp_to_blender(p): return (p[0], p[2], -p[1])
def blender_to_ros(p): return (-p[1], p[0], p[2])
def between(a, b):
    a, b = unit(a), unit(b)
    d = max(-1., min(1., dot(a, b)))
    if d > 1-1e-10: return (1., 0., 0., 0.)
    if d < -1+1e-8:
        axis = min(((1,0,0),(0,1,0),(0,0,1)), key=lambda v: abs(dot(a,v)))
        return (0., *unit(cross(a, axis)))
    return unit((1+d, *cross(a, b)))

class OneEuro:
    def __init__(self, min_cutoff=1., beta=.03, d_cutoff=1.):
        if min_cutoff <= 0 or beta < 0 or d_cutoff <= 0: raise ValueError('Parámetros de filtro inválidos')
        self.min_cutoff, self.beta, self.d_cutoff = min_cutoff, beta, d_cutoff
        self.t = self.raw = self.x = None
        self.dx = 0.

    @staticmethod
    def alpha(cutoff, dt): return 1 / (1 + 1/(2*math.pi*cutoff*dt))

    def __call__(self, x, t):
        if not math.isfinite(x) or not math.isfinite(t): raise ValueError('Dato no finito')
        if self.t is None or t-self.t > .5:
            self.t, self.raw, self.x, self.dx = t, x, x, 0.
            return x
        dt = t-self.t
        if dt <= 0: raise ValueError('Tiempo debe crecer')
        derivative = (x-self.raw)/dt
        ad = self.alpha(self.d_cutoff, dt)
        self.dx += ad*(derivative-self.dx)
        a = self.alpha(self.min_cutoff+self.beta*abs(self.dx), dt)
        self.x += a*(x-self.x)
        self.t, self.raw = t, x
        return self.x

def points_blender(packet, threshold=.6):
    return {int(k): mp_to_blender((v['x'],v['y'],v['z']))
            for k,v in packet['landmarks'].items() if v['visibility'] >= threshold}

def torso_axes(p):
    left = unit(sub(p[11], p[12]))
    shoulder = tuple((a+b)/2 for a,b in zip(p[11],p[12]))
    hip = tuple((a+b)/2 for a,b in zip(p[23],p[24]))
    back = unit(cross(sub(shoulder, hip), left))
    up = unit(cross(left, back))
    return left, back, up

def joint_angles(p):
    """Hombro: pitch adelante y roll hacia izquierda en marco del torso.

    d = (sin(roll)*cos(pitch), -sin(pitch), -cos(roll)*cos(pitch)).
    Pose vertical abajo=0. Twist no observado. Elevación también se exporta.
    """
    out = {}
    for label, ids in {'left_elbow':(11,13,15),'right_elbow':(12,14,16),
                       'left_knee':(23,25,27),'right_knee':(24,26,28)}.items():
        try:
            a,b,c = (p[i] for i in ids)
            out[label+'_flex'] = angle(sub(b,a),sub(c,b))
        except (KeyError,ValueError): pass
    try: axes = torso_axes(p)
    except (KeyError,ValueError): return out
    for side, a,b in [('left',11,13),('right',12,14)]:
        try:
            d = unit(sub(p[b],p[a]))
            x,y,z = (dot(d,v) for v in axes)
            out[side+'_shoulder_pitch'] = math.asin(max(-1.,min(1.,-y)))
            out[side+'_shoulder_roll'] = math.atan2(x,-z)
            out[side+'_shoulder_elevation'] = math.acos(max(-1.,min(1.,-z)))
        except (KeyError,ValueError): pass
    return out

def rotations(landmarks):
    p = points_blender({'landmarks': landmarks})
    out = {k+'_rad':v for k,v in joint_angles(p).items()}
    for side,a,b in [('left',11,13),('right',12,14)]:
        try: out[side+'_shoulder_quaternion'] = between((0,0,-1), sub(p[b],p[a]))
        except (KeyError,ValueError): pass
    return out

class PacketBuilder:
    def __init__(self, source, min_cutoff=1., beta=.03):
        self.source, self.session, self.frame = source, str(uuid.uuid4()), 0
        self.filters = [[OneEuro(min_cutoff,beta) for _ in range(3)] for _ in NAMES]

    def build(self, points, t=None, timestamp_ms=None):
        t = time.monotonic() if t is None else t
        landmarks = {}
        if points:
            if len(points)!=33: raise ValueError('Se requieren 33 landmarks')
            for i,p in enumerate(points):
                xyz = (p['x'],p['y'],p['z'])
                visibility = float(p.get('visibility',1.))
                if visibility >= .6:
                    xyz = [f(x,t) for f,x in zip(self.filters[i],xyz)]
                landmarks[str(i)] = dict(zip(('x','y','z'),xyz),name=NAMES[i],visibility=visibility)
        packet = dict(schema_version=1,session_id=self.session,frame_id=self.frame,
                      timestamp_ms=int(time.time()*1000) if timestamp_ms is None else timestamp_ms,
                      source=self.source,coordinate_space='mediapipe_world_m',
                      tracking=bool(points),landmarks=landmarks,joint_rotations=rotations(landmarks))
        self.frame += 1
        validate(packet)
        return packet

def finite(x): return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def validate(p):
    if not isinstance(p,dict) or p.get('schema_version')!=1: raise ValueError('Esquema desconocido')
    if p.get('coordinate_space')!='mediapipe_world_m': raise ValueError('Se requieren world landmarks')
    if not isinstance(p.get('session_id'),str) or not 1<=len(p['session_id'])<=100: raise ValueError('Sesión inválida')
    if not isinstance(p.get('source'),str) or len(p['source'])>200: raise ValueError('Fuente inválida')
    if type(p.get('frame_id')) is not int or p['frame_id']<0: raise ValueError('Frame inválido')
    if not finite(p.get('timestamp_ms')) or p['timestamp_ms']<0: raise ValueError('Timestamp inválido')
    if type(p.get('tracking')) is not bool: raise ValueError('Tracking inválido')
    lm = p.get('landmarks')
    if not isinstance(lm,dict) or (set(lm)!=set(map(str,range(33))) if p['tracking'] else bool(lm)):
        raise ValueError('Landmarks incompletos')
    for key,v in lm.items():
        if not isinstance(v,dict) or v.get('name')!=NAMES[int(key)]: raise ValueError('Nombre inválido')
        if not all(finite(v.get(k)) for k in ('x','y','z','visibility')): raise ValueError('Landmark no finito')
        if not 0<=v['visibility']<=1 or any(abs(v[k])>20 for k in ('x','y','z')): raise ValueError('Fuera de rango')
    if not isinstance(p.get('joint_rotations'),dict): raise ValueError('Rotaciones inválidas')
    for key,value in p['joint_rotations'].items():
        if key.endswith('_quaternion'):
            if not isinstance(value,(list,tuple)) or len(value)!=4 or not all(finite(v) for v in value) or abs(norm(value)-1)>.001:
                raise ValueError('Cuaternión inválido')
        elif not finite(value): raise ValueError('Rotación no finita')
    return p

def encode(p):
    validate(p)
    data = json.dumps(p,separators=(',',':'),allow_nan=False).encode('utf8')
    if len(data)>60000: raise ValueError('Datagrama demasiado grande')
    return data

def decode(data):
    if len(data)>60000: raise ValueError('Datagrama demasiado grande')
    return validate(json.loads(data))

class Receiver:
    def __init__(self, port=5005, host='127.0.0.1'):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        try:
            self.sock.bind((host,port))
            self.sock.setblocking(False)  # Línea que impide bloquear Blender.
        except Exception:
            self.sock.close(); raise
        self.session = None; self.frame = -1; self.retired = set()
        self.last_tracking = None
        self.stats = dict(received=0,rejected=0,applied=0)

    def accept(self,p,now_ms):
        if not -100 <= now_ms-p['timestamp_ms'] <= 500: return False
        if p['session_id'] in self.retired: return False
        if p['session_id']!=self.session:
            if self.session is not None: self.retired.add(self.session)
            # Cap memory; incoming sockets are intentionally localhost-only.
            if len(self.retired)>128: self.retired.pop()
            self.session,self.frame = p['session_id'],-1
        if p['frame_id']<=self.frame: return False
        self.frame = p['frame_id']
        return True

    def poll(self):
        newest=None; start=time.perf_counter()
        for _ in range(32):
            if time.perf_counter()-start > .004: break
            try: data,_ = self.sock.recvfrom(65535)
            except BlockingIOError: break
            self.stats['received']+=1
            try:
                p=decode(data)
                if not self.accept(p,time.time()*1000): raise ValueError('Viejo o duplicado')
                newest=p
            except (ValueError,UnicodeError,TypeError,KeyError,OverflowError): self.stats['rejected']+=1
        if newest and newest['tracking']:
            self.last_tracking=time.monotonic();self.stats['applied']+=1
        return newest

    @property
    def stale(self): return self.last_tracking is None or time.monotonic()-self.last_tracking>.5
    def close(self): self.sock.close()

def joint_state(packet, limits=None):
    values=joint_angles(points_blender(packet))
    order=['left_shoulder_pitch','left_shoulder_roll','left_elbow_flex',
           'right_shoulder_pitch','right_shoulder_roll','right_elbow_flex']
    names=[n for n in order if n in values]
    position=[values[n] for n in names]
    if limits:
        position=[max(limits[n][0],min(limits[n][1],v)) if n in limits else v for n,v in zip(names,position)]
    ms=int(packet['timestamp_ms'])
    return dict(header=dict(stamp=dict(sec=ms//1000,nanosec=(ms%1000)*1000000),frame_id='base_link'),
                name=names,position=position,velocity=[],effort=[])
