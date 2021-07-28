from server import Server

if __name__ == '__main__':
    s = Server('bcb-ptax')
    s.server.app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )