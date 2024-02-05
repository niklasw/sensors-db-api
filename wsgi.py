
from app import app, CFG

if __name__ == "__main__":
    app.run(host=CFG.path('server/ip'), port=CFG.path('server/port'), debug=debug)
