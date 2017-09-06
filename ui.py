from diplomatist import *
import tkinter, thread


os.environ["LOOPBACK_CAPTURE"] = r"LoopbackCapture\win32\csharp\LoopbackCapture\LoopbackCapture\bin\Debug\LoopbackCapture.exe"

opt = get_options()
if opt.credential:
    if os.path.isfile(opt.credential):
        cred = open(opt.credential, "r").read()
    else:
        cred = opt.credential
    if opt.translate:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = opt.credential
    else:
        cred = None

diplomatist = Diplomatist()

diplomatist_ui = tkinter.Tk()
transc_str = tkinter.StringVar()
transc_label = tkinter.Label(diplomatist_ui, textvariable=transc_str).pack(side=tkinter.TOP)
transl_str = tkinter.StringVar()
transl_label = tkinter.Label(diplomatist_ui, textvariable=transl_str).pack(side=tkinter.BOTTOM)

def async_transcribe(api=0, audio_file=None, cred=None, language="en-US"):
    transc = diplomatist.transcribe(api, audio_file, cred, language)
    if transc == False:
        transc = "Cannot Be Transcribed!"
    transc_str.set(transc)

def async_transcribe_translate(api=0, audio_file=None, cred=None, transc_lan="en-US", transl_lan="zh"):
    transc = diplomatist.transcribe(api, audio_file, cred, transc_lan)
    if transc == False:
        transc = "Cannot Be Transcribed!"
    transc_str.set(transc)
    transl = diplomatist.translate(transc, transl_lan)
    transl_str.set(transl)

def dip_thread():
    init_time = 0
    records_folder = os.path.join(os.path.dirname(opt.audio_file), "records")
    if not os.path.isdir(records_folder):
        os.mkdir(records_folder)
    while True:
        start_time = time.time()
        if opt.use_mic:
            diplomatist.record(opt.audio_file)
        else:
            diplomatist.capture_loopback(opt.audio_file, opt.time_slice)
        end_time = time.time()
        print "{} -> {}".format(time.strftime("%H:%M:%S", time.gmtime(init_time)), time.strftime("%H:%M:%S", time.gmtime(end_time - start_time + init_time)))
        init_time = end_time - start_time + init_time
        saved_file_name = str(time.time()) + ".wav"
        saved_audio_file = os.path.join(records_folder, saved_file_name)
        os.rename(opt.audio_file, saved_audio_file)
        if opt.translate:
            thr = threading.Thread(target=async_transcribe_translate, args=([opt.api, saved_audio_file, cred, opt.language, opt.translate]), kwargs={})
            thr.start()
        else:
            thr = threading.Thread(target=async_transcribe, args=([opt.api, saved_audio_file, cred, opt.language]), kwargs={})
            thr.start()


thread.start_new_thread(dip_thread,())
diplomatist_ui.mainloop()