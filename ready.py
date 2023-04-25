import time
import pandas as pd
import os
import select
import numpy


#import timerfd
import sys



from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets


def old():
    BoardShim.enable_dev_board_logger()

    print("Running!")
    params = BrainFlowInputParams()
    params.serial_port = "/dev/ttyUSB0"

    board = BoardShim(BoardIds.CYTON_DAISY_BOARD, params)
    board.prepare_session()
    board.start_stream ()
    time.sleep(10)
    # data = board.get_current_board_data (256) # get latest 256 packages or less, doesnt remove them from internal buffer
    data = board.get_board_data()  # get all data and remove it from internal buffer
    board.stop_stream()
    board.release_session()
    
    print(data)
    df = pd.DataFrame(data);
    df.head();
    
def new():
    
    if (len(sys.argv) != 2):
        sys.exit("Usage: python3 reader.py COMPORT")
    
    
    
    
    BoardShim.enable_dev_board_logger()
 
    params = BrainFlowInputParams()
    params.serial_port = sys.argv[1]
    print("Reading from port " + sys.argv[1])
    
    board = BoardShim(BoardIds.CYTON_DAISY_BOARD, params)
    board.prepare_session()
    board.start_stream ()
    
    
    data = board.get_board_data()
    data = numpy.transpose(data)
    print(data.shape)
    # Create epoll object
    ep = select.epoll()
    ep.register(sys.stdin.fileno(), select.EPOLLIN)
    
    
    
    #Register timer
    #tracker_update_timer = timerfd.create(timerfd.CLOCK_REALTIME,0)
    #timerfd.settime(tracker_update_timer,0,5,0) # 5 second timer
    #ep.register(tracker_update_timer, select.EPOLLIN) #Register tracker update timer
    
    
    
    # poll (stdin, timer5s):
    #    if stdin:
    #        read commands
    #    else:
    #        read the stream from the board and store it.
    stopped = False
    while (stopped == False):
        for fileno, eventmask in ep.poll(1): #Listen to Epoll
            if fileno == sys.stdin.fileno(): #Read std in
                l = sys.stdin.readline()
                if (l == "stop\n"):
                    board.stop_stream()
                    board.release_session()
                    print(data)
                    df = pd.DataFrame(data)
                    df.head()
                    stopped = True;
                    print(data.shape)
                elif(int(l) != None):
                    print("Setting flag to " + str(int(l)))
                    val = int(l)
        if (stopped == False):
            temp =  numpy.transpose(board.get_board_data())
            data = numpy.concatenate((data, temp), axis=0)
            print(data.shape)
            print("READ DATA")
            #elif fileno == tracker_update_timer:
                #Read data
            #    data = numpy.concatenate(data, board.get_board_data())
            #    timerfd.settime(tracker_update_timer,0,5,0)
    

new()
 
