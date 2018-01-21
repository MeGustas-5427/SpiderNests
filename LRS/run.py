from LengyueRequestsService import LRS
app = LRS()


@app.controller()
async def recv(config, state):
    print("Here to change cfg ", config, state)
    return config

app.run(config="./config.json")