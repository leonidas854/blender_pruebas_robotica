#!/usr/bin/env python3
"""
scripts/test_blender_mcp.py
Prueba de conectividad y comunicación socket con Blender MCP en localhost:9876.
"""

import socket
import json
import sys
import time

def test_connection(host: str = "127.0.0.1", port: int = 9876, timeout: float = 3.0):
    print(f"[*] Comprobando conexión con Blender MCP en {host}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        print("[+] Conexion socket establecida con Blender!")

        # Comando de prueba bpy
        test_payload = {
            "type": "execute_code",
            "code": "import bpy; result = f'Blender {bpy.app.version_string} activo con {len(bpy.data.objects)} objetos'; print(result); result"
        }

        message = json.dumps(test_payload) + "\n"
        sock.sendall(message.encode("utf-8"))

        sock.settimeout(5.0)
        response_data = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response_data += chunk
            if b"\n" in chunk:
                break

        sock.close()

        if response_data:
            print("[+] Respuesta recibida de Blender:")
            try:
                parsed = json.loads(response_data.decode("utf-8").strip())
                print(f"    {parsed}")
            except Exception:
                print(f"    {response_data.decode('utf-8').strip()}")
            print("\n[✓] El puente MCP con Blender está funcionando perfectamente.")
            return True
        else:
            print("[!] Se conectó al puerto, pero no se recibió respuesta.")
            return False

    except ConnectionRefusedError:
        print("[!] No se pudo conectar: Conexión rechazada en el puerto 9876.")
        print("[*] Asegúrate de que Blender esté abierto:")
        print("    1. Ejecuta: ./run_blender.sh")
        print("    2. En el Viewport 3D presiona 'N' para abrir el panel lateral.")
        print("    3. Ve a la pestaña 'MCP for Blender' y haz clic en 'Start MCP Server'.")
        return False
    except Exception as e:
        print(f"[!] Error durante la prueba: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
