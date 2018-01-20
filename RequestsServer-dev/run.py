from LengyueRequestsService import Controller
app = Controller()


@app.reciver()
async def recv(config, state):
    print("Here to change cfg ", config, state)
    return config

app.run(config="./config.json")