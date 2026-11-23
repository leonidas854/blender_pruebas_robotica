"""Puente opcional: UDP 5006 -> sensor_msgs/msg/JointState o JSONL."""
import argparse
import json
import time
from pathlib import Path
from mocap.core import Receiver,joint_state

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port',type=int,default=5006)
    p.add_argument('--ros',action='store_true')
    p.add_argument('--output',type=Path)
    p.add_argument('--seconds',type=float,default=0)
    p.add_argument('--limits',type=Path,default=Path(__file__).parent/'mocap/joint_limits.json')
    args=p.parse_args();limits=json.loads(args.limits.read_text())['limits_rad']
    receiver=Receiver(args.port);node=None;writer=None
    try:
        if args.ros:
            import rclpy
            from sensor_msgs.msg import JointState
            rclpy.init();node=rclpy.create_node('viajero_mocap_bridge')
            publisher=node.create_publisher(JointState,'/joint_states',10)
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            writer=args.output.open('w',encoding='utf8')
        start=time.monotonic()
        while not args.seconds or time.monotonic()-start<args.seconds:
            packet=receiver.poll()
            if packet and packet['tracking']:
                payload=joint_state(packet,limits)
                if not payload['name']:continue
                if writer:writer.write(json.dumps(payload,allow_nan=False)+'\n');writer.flush()
                if node:
                    msg=JointState();stamp=payload['header']['stamp']
                    msg.header.stamp.sec=stamp['sec'];msg.header.stamp.nanosec=stamp['nanosec']
                    msg.header.frame_id='base_link';msg.name=payload['name'];msg.position=payload['position']
                    publisher.publish(msg)
                elif not writer:print(json.dumps(payload))
            if node:rclpy.spin_once(node,timeout_sec=0)
            time.sleep(.005)
    except KeyboardInterrupt:pass
    finally:
        receiver.close()
        if writer:writer.close()
        if node:node.destroy_node();rclpy.shutdown()

if __name__=='__main__':main()
