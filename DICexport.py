"""
GNU GPLv3 License
Copyright (c) 2021, Dr. Chaoyi Zhu 
Andrew Minor Research Group @ UC Berkeley
Contact Information: zchaoyi93@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QFileDialog, QApplication
from PyQt5 import uic
import numpy as np
import cv2


class videoPlayer:
    def __init__(self):
        # Initializing the UI file designed in Qt software
        # Loading the ui program designed by designer
        self.ui = uic.loadUi('DIC_GUI.ui')
        self.ui.setWindowTitle("DIC Video to Image Stack")  # title of the UI

        # player
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.ui.player)

        # Button
        self.ui.select_video.clicked.connect(self.open)
        self.ui.play_pause.clicked.connect(self.playPause)

        # Progress bar
        self.player.durationChanged.connect(self.getDuration)
        self.player.positionChanged.connect(self.getPosition)
        self.ui.sld_duration.sliderMoved.connect(self.updatePosition)

        self.ui.capture_start.clicked.connect(self.getStartTime)
        self.ui.capture_stop.clicked.connect(self.getStopTime)
        self.ui.export_stack.clicked.connect(self.exportImageStack)

    # Open the video file
    def open(self):
        global video_url, fps
        url = QFileDialog.getOpenFileUrl()[0]
        self.player.setMedia(QMediaContent(url))
        self.ui.video_path.setText("Video Path:" + url.toString())
        self.ui.video_path.adjustSize()
        self.player.play()
        path = url.toString()
        video_url = path[8::]

        video = cv2.VideoCapture(video_url)
        fps = video.get(cv2.CAP_PROP_FPS) 

    # Play video
    def playPause(self):
        if self.player.state() == 1:
            self.player.pause()
        else:
            self.player.play()

    # Total video time acquisition
    def getDuration(self, d):
        '''d Is the total length of video captured( ms)'''
        self.ui.sld_duration.setRange(0, d)
        self.ui.sld_duration.setEnabled(True)
        self.displayTime(d)

    # Video real-time location acquisition
    def getPosition(self, p):
        self.ui.sld_duration.setValue(p)
        self.displayTime(p)

    # Show time passed
    def displayTime(self, ms):
        minutes = int(ms/60000)
        seconds = int((ms-minutes*60000)/1000)
        self.ui.duration.setText('{}:{}'.format(minutes, seconds))

    # Update video location with progress bar
    def updatePosition(self, v):
        self.player.setPosition(v)
        self.displayTime(v)

    # Get starting time
    # (The value is the current playback position, since the beginning of the media.)
    def getStartTime(self):
        global start
        start = self.player.position()
        self.displayStartTime(start)

   # Show start time
    def displayStartTime(self, ms):
        minutes = int(ms/60000)
        seconds = int((ms-minutes*60000)/1000)
        self.ui.start_time.setText('{}:{}'.format(minutes, seconds))

    # Get stopping time
    # (The value is the current playback position, since the beginning of the media.)
    def getStopTime(self):
        global end
        end = self.player.position()
        self.displayStopTime(end)

    # Show stop time
    def displayStopTime(self, ms):
        minutes = int(ms/60000)
        seconds = int((ms-minutes*60000)/1000)
        self.ui.stop_time.setText('{}:{}'.format(minutes, seconds))

    # export image stack 
    def exportImageStack(self):
        url = QFileDialog.getExistingDirectory()
        print(url)
        start_frame = int(start/1000)*int(fps) # first frame
        end_frame= int(end/1000)*int(fps) # last frame
        count = 0
        vidcap = cv2.VideoCapture(video_url)
        for n in range(start_frame, end_frame+1, int(fps)):
            vidcap.set(cv2.CAP_PROP_POS_FRAMES, n)
            success, frame = vidcap.read()
            if success:
                cv2.imwrite(url+"/Frame_%d.png" % count, frame)     # save the frame as png file      
                count += 1
                self.ui.progressBar.setValue(100*(count/(len(range(start_frame, end_frame+1, int(fps))))))
                print('Exported video frame number: ', count)
            else :
                print(" Video Frame not found")
                break

# main program
if  __name__ == "__main__":
    app = QApplication([])
    myPlayer = videoPlayer()
    myPlayer.ui.show()
    app.exec()
