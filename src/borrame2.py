import threading

finished_threads = []
event = threading.Event()

def do_important_stuff():
    print("important stuff")

def func():
   do_important_stuff()

   thisthread = threading.current_thread()
   finished_threads.append(thisthread)
   if len(finished_threads) > 1 and finished_threads[1] == thisthread:
       #yay we are number two!
       event.set()

for i in range(5):
    threading.Thread(target=func).start()

event.wait()