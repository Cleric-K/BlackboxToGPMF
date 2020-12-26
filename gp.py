from tkinter import * 
from tkinter.filedialog import askopenfilename
import process as p
import threading, os
import queue 
import time
import tkinter as tk

thread_queue = queue.Queue();
top = Tk()
top.geometry("620x500")
top.title("GPMF Emulation 2020.12.26.1")

def loadVideoCallBack():
   video_path = askopenfilename()
   txVideoPath.set(video_path)
   txVideoFile.set(os.path.basename(video_path))
   
def loadBlBoxCallBack():
   blbox_path = askopenfilename()
   txBlBoxPath.set(blbox_path)
   txBlBoxFile.set(os.path.basename(blbox_path))
   
def processVideoCallBack():

    if validateInputs() == False:
        return False
        
    thread = threading.Thread(target=p.processVideo, 
        args=(txVideoPath.get(),txBlBoxPath.get(),txOffset1.get(),txOffset2.get(), txTime1.get(), txTime2.get(), profile.get(), thread_queue))
    
    thread.daemon = 1
    thread.start()
    txStatus.delete("1.0",tk.END)
    readThreadQueue()
    
def readThreadQueue():
    try:
        res = str(thread_queue.get(0))
        #print(res)
        txStatus.insert(tk.END,res + '\n')
    except queue.Empty:
        pass
    finally:
        top.after(100, readThreadQueue)
        
def validateInputs():
    is_valid = True
    txStatus.delete("1.0",tk.END)
    
    if len(txVideoPath.get()) == 0:
        txStatus.insert(tk.END,'! Please select a video file (.mp4)\n')
        is_valid = False
        
    if len(txBlBoxPath.get()) == 0:
        txStatus.insert(tk.END,'! Please select a BetaFlight blackbox file (.csv)\n')
        is_valid = False
    
    return is_valid


txVideoPath = StringVar()
txBlBoxPath = StringVar()
txVideoFile = StringVar()
txBlBoxFile = StringVar()

btLoadVideo = Button(top, width=15, text = "Load video file", command = loadVideoCallBack).place(x = 20, y = 20)
btLoadBlBox = Button(top, width=15, text = "Load blackbox file", command = loadBlBoxCallBack).place(x = 20, y = 60)
lbVideoPath = Label(top, textvariable = txVideoFile).place(x = 150, y = 20)
lbBlBoxPath = Label(top, textvariable = txBlBoxFile).place(x = 150, y = 60)
lbStatus = Label(top, text = "Status").place(x = 20, y = 254)
lbProfile = Label(top, text = "Profile").place(x = 20, y = 175)

profiles = [
    'Hero5 FHD Wide 16:9 1920x1080',
    'Hero5 2K7 Wide 16:9 2704x1520',
    'Hero5 2K7 Wide 4:3 2704x2032',
    'Hero5 4K  Wide 16:9 3840x2160',
]

profile = StringVar(top)
profile.set(profiles[0])

ddProfiles = OptionMenu(top, profile, *profiles)
ddProfiles.place(x = 87, y = 170)

lbStartOffset1 = Label(top, text = "Start offset" ).place(x = 20, y = 105)
txOffset1 = Entry(top, width=7)
txOffset1.place(x = 90, y = 105)
txOffset1.insert(0, "0:0")

lbEndOffset1 = Label(top, text = "End offset" ).place(x = 150, y = 105)
txOffset2 = Entry(top, width=7)
txOffset2.place(x = 220, y = 105)
#txOffset2.insert(0, "0:0")

lbStartTime = Label(top, text = "Start time" ).place(x = 20, y = 140)
txTime1 = Entry(top, width=7)
txTime1.place(x = 90, y = 140)
#txTime1.insert(0, "0:0")

lbEndTime = Label(top, text = "End time" ).place(x = 150, y = 140)
txTime2 = Entry(top, width=7)
txTime2.place(x = 220, y = 140)
#txTime2.insert(0, "0:0")

btProcess = Button(top, width=15, text ="Process video", command = processVideoCallBack).place(x = 20, y = 215)

frm = Frame(top)
frm.pack( side = BOTTOM, padx=20, pady=20 )

txStatus = Text(frm,height=12, width=70)
#lbStatus.place(x = 20, y = 170)
txStatus.pack(side=tk.LEFT, fill=tk.Y)
txStatus.insert(tk.END,'Please load video and blackbox file...\n')
#txStatus.insert(tk.END,'\nTerms and Conditions\n')
#txStatus.insert(tk.END,'1.By using this tool you agree to use it on your own risk\n')
#txStatus.insert(tk.END,'2.Nothing is guaranteed to work, this is free application\n')
#txStatus.insert(tk.END,'3.The authors of this app are not liable for the actions of it\'s users\n')
#txStatus.insert(tk.END,'4.This application does not collect user informations\n')
#txStatus.insert(tk.END,'5.Be polite if you need help, nobody get\'s payed to develop this app\n')
#txStatus.insert(tk.END,'6.Support group: https://www.facebook.com/groups/fpvtools\n')

Scroll = tk.Scrollbar(frm)
Scroll.pack(side=tk.RIGHT, fill=tk.Y)
#Scroll.place(x = 580, y = 170)
Scroll.config(command=txStatus.yview)
txStatus.config(yscrollcommand=Scroll.set)


top.mainloop()
sys.exit()


