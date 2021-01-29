from scipy.io import wavfile  


fs,data = wavfile.read('alarm.wav')

for i in range(10): 
    
    if i==5:
        sounddevice.stop()
    else:
        sounddevice.play(data,fs)
        time.sleep(1)
        