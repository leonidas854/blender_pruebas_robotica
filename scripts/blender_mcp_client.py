"""Local client for the installed MCP for Blender add-on socket protocol."""
import argparse
import json
import socket
from pathlib import Path


def execute(code, timeout=600):
    with socket.create_connection(('127.0.0.1', 9876), timeout=10) as connection:
        connection.settimeout(timeout)
        connection.sendall(json.dumps({'type': 'execute_code', 'params': {'code': code}}).encode())
        buffer = b''
        while len(buffer) < 32 * 1024 * 1024:
            chunk = connection.recv(65536)
            if not chunk:
                raise RuntimeError('Blender closed the connection without a complete response')
            buffer += chunk
            try:
                result = json.loads(buffer)
            except (ValueError, UnicodeDecodeError):
                continue
            if result.get('status') != 'success':
                raise RuntimeError(result)
            return result
        raise RuntimeError('Response exceeds 32 MiB')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', type=Path)
    parser.add_argument('--code')
    args = parser.parse_args()
    code = args.code or (args.file.read_text() if args.file else 'print(bpy.app.version_string, bpy.data.filepath)')
    print(json.dumps(execute(code), ensure_ascii=False, indent=2))
