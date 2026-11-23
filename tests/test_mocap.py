import copy
import json
import math
import random
import socket
import time
import unittest
from mocap.core import *
from mocap.synthetic import pose

class MathTests(unittest.TestCase):
    def test_angles(self):
        self.assertAlmostEqual(angle((1,0,0),(1,0,0)),0)
        self.assertAlmostEqual(angle((1,0,0),(0,1,0)),math.pi/2)
        self.assertAlmostEqual(angle((1,0,0),(-1,0,0)),math.pi)
        with self.assertRaises(ValueError):angle((0,0,0),(1,0,0))
    def test_quaternion_antiparallel(self):
        q=between((0,1,0),(0,-1,0))
        self.assertAlmostEqual(norm(q),1);self.assertAlmostEqual(q[0],0)
        self.assertEqual(between((0,1,0),(0,1,0)),(1,0,0,0))
    def test_coordinate_handedness(self):
        for transform in (mp_to_blender,blender_to_ros):
            self.assertEqual(cross(transform((1,0,0)),transform((0,1,0))),transform((0,0,1)))
        self.assertEqual(mp_to_blender((0,-1,0)),(0,0,1))
        self.assertEqual(blender_to_ros((0,-1,0)),(1,0,0))
    def test_known_synthetic_angles(self):
        p=PacketBuilder('synthetic_fixture').build(pose(0))
        a=joint_angles(points_blender(p))
        self.assertAlmostEqual(a['left_elbow_flex'],.65,places=6)
        self.assertAlmostEqual(a['left_shoulder_elevation'],.55,places=6)
    def test_filter_reduces_stationary_noise(self):
        rng=random.Random(12);f=OneEuro(beta=0);raw=[rng.gauss(0,.02) for _ in range(300)]
        out=[f(v,i/30) for i,v in enumerate(raw)]
        self.assertLess(sum(x*x for x in out[60:]),sum(x*x for x in raw[60:])*.4)
    def test_filter_adapts_and_resets(self):
        slow=OneEuro(beta=0);fast=OneEuro(beta=5)
        slow(0,0);fast(0,0)
        self.assertGreater(fast(1,1/30),slow(1,1/30))
        self.assertEqual(fast(5,2),5)
        with self.assertRaises(ValueError):fast(6,2)

class ProtocolTests(unittest.TestCase):
    def setUp(self):self.p=PacketBuilder('synthetic_fixture').build(pose(0))
    def test_roundtrip_and_jointstate(self):
        p=decode(encode(self.p));state=joint_state(p)
        self.assertEqual(len(state['name']),6);self.assertEqual(len(state['position']),6)
        self.assertLess(len(encode(p)),10000)
    def test_reject_invalid_data(self):
        for key,value in [('x',float('nan')),('visibility',2)]:
            p=copy.deepcopy(self.p);p['landmarks']['11'][key]=value
            with self.assertRaises(ValueError):encode(p)
        p=copy.deepcopy(self.p);p['landmarks'].pop('32')
        with self.assertRaises(ValueError):validate(p)
        with self.assertRaises(ValueError):decode(b'{invalid')
    def test_occlusion_omits_angle(self):
        self.p['landmarks']['13']['visibility']=.1
        self.assertNotIn('left_elbow_flex',joint_angles(points_blender(self.p)))
    def test_order_session_and_expiry(self):
        r=Receiver(0)
        try:
            now=self.p['timestamp_ms'];self.assertTrue(r.accept(self.p,now))
            self.assertFalse(r.accept(self.p,now))
            p=copy.deepcopy(self.p);p['frame_id']+=1
            self.assertFalse(r.accept(p,now+501))
            p['session_id']='new';p['frame_id']=0
            self.assertTrue(r.accept(p,now));self.assertFalse(r.accept(self.p,now))
        finally:r.close()
    def test_udp_real_loopback(self):
        r=Receiver(0);sender=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        try:
            sender.sendto(b'bad',r.sock.getsockname())
            sender.sendto(encode(self.p),r.sock.getsockname())
            deadline=time.monotonic()+1;packet=None
            while packet is None and time.monotonic()<deadline:packet=r.poll()
            self.assertIsNotNone(packet);self.assertFalse(r.stale)
            self.assertEqual(r.stats['rejected'],1)
            before=time.perf_counter();self.assertIsNone(r.poll());self.assertLess(time.perf_counter()-before,.05)
        finally:r.close();sender.close()

if __name__=='__main__':unittest.main()
