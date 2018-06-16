def getSampleRate(msg):
    print(msg)
    return (int)(msg.decode("utf-8").split(':')[1])