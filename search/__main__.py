"""
启动服务
"""
import os
from .WEBUI.MrkWeb import app

def main():
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)

if __name__ == '__main__':
    main()
