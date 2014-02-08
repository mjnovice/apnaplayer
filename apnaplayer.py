#!/usr/bin/env python
import sip
sip.setapi('QString', 2)
from utube import youtube_search
import sys
from PyQt4 import QtCore, QtGui
import os

try:
    from PyQt4.phonon import Phonon
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "Music Player",
            "Your Qt installation does not have Phonon support.",
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
            QtGui.QMessageBox.NoButton)
    sys.exit(1)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(QtGui.QMainWindow, self).__init__()

        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.mediaObject = Phonon.MediaObject(self)
        #self.metaInformationResolver = Phonon.MediaObject(self)

        self.mediaObject.setTickInterval(1000)

        self.mediaObject.tick.connect(self.tick)
        self.mediaObject.stateChanged.connect(self.stateChanged)
        self.metaInformationResolver.stateChanged.connect(self.metaStateChanged)
        #self.mediaObject.currentSourceChanged.connect(self.sourceChanged)
        self.mediaObject.aboutToFinish.connect(self.aboutToFinish)


        self.setupActions()
        self.setupMenus()
        self.setupUi()
        Phonon.createPath(self.mediaObject, self.audioOutput)
        Phonon.createPath(self.mediaObject, self.videoWidget)
        self.timeLcd.display("00:00") 
        self.sources = []
        self.utuberesults = []

    def sizeHint(self):
        return QtCore.QSize(500, 300)

    def addFiles(self):
        files = QtGui.QFileDialog.getOpenFileNames(self, "Select Music Files",
                QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.MusicLocation))

        if not files:
            return

        index = len(self.sources)
        print self.sources
        print index
        print "bb44",self.mediaObject.currentSource()
        print "beforeb4",self.metaInformationResolver.currentSource(),self.metaInformationResolver.metaData()
        for string in files:
            self.sources.append(Phonon.MediaSource(string))
            CR=self.musicTable.rowCount()
            self.musicTable.insertRow(CR)
            songItem = QtGui.QTableWidgetItem(string)
            self.musicTable.setItem(CR,0,songItem)
        """  
        if self.sources:
            print "before",self.metaInformationResolver.currentSource(),self.metaInformationResolver.metaData()
            self.metaInformationResolver.setCurrentSource(self.sources[index])
            print "after",self.metaInformationResolver.currentSource(),self.metaInformationResolver.metaData()
        """
    def about(self):
        QtGui.QMessageBox.information(self, "About Music Player",
                "Music Player developed for Khula Maidan!")

    def stateChanged(self, newState, oldState):
        if newState == Phonon.ErrorState:
            if self.mediaObject.errorType() == Phonon.FatalError:
                QtGui.QMessageBox.warning(self, "Fatal Error",
                        self.mediaObject.errorString())
            else:
                QtGui.QMessageBox.warning(self, "Error",
                        self.mediaObject.errorString())

        elif newState == Phonon.PlayingState:
            self.playAction.setEnabled(False)
            self.pauseAction.setEnabled(True)
            self.stopAction.setEnabled(True)

        elif newState == Phonon.StoppedState:
            self.stopAction.setEnabled(False)
            self.playAction.setEnabled(True)
            self.pauseAction.setEnabled(False)
            self.timeLcd.display("00:00")

        elif newState == Phonon.PausedState:
            self.pauseAction.setEnabled(False)
            self.stopAction.setEnabled(True)
            self.playAction.setEnabled(True)

    def tick(self, time):
        displayTime = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)
        self.timeLcd.display(displayTime.toString('mm:ss'))

    def tableYTClicked(self,row,column):
        print self.utuberesults[row][1]
        os.system("youtube-dl "+str(self.utuberesults[row][1]))
        self.mediaObject.setCurrentSource(Phonon.MediaSource(str(self.utuberesults[row][1])+".mp4"))
        #self.mediaObject.setCurrentSource(Phonon.MediaSource("asd.mp4"))
        self.mediaObject.play()
        print row

    def tableClicked(self, row, column):
        wasPlaying = (self.mediaObject.state() == Phonon.PlayingState)

        self.mediaObject.stop()
        self.mediaObject.clearQueue()

        self.mediaObject.setCurrentSource(self.sources[row])

        if wasPlaying:
            self.mediaObject.play()
        else:
            self.mediaObject.stop()

    def sourceChanged(self, source):
        self.musicTable.selectRow(self.sources.index(source))
        self.timeLcd.display('00:00')
    """
    def metaStateChanged(self, newState, oldState):
        print "metaStateChanged"
        if newState == Phonon.ErrorState:
            QtGui.QMessageBox.warning(self, "Error opening files",
                    self.metaInformationResolver.errorString())

            while self.sources and self.sources.pop() != self.metaInformationResolver.currentSource():
                pass

            return

        if newState != Phonon.StoppedState and newState != Phonon.PausedState:
            return

        if self.metaInformationResolver.currentSource().type() == Phonon.MediaSource.Invalid:
            return

        metaData = self.metaInformationResolver.metaData()

        print self.metaInformationResolver.currentSource().fileName()
        title = metaData.get('TITLE', [''])[0]
        if not title:
            print "dsd"
            title = self.metaInformationResolver.currentSource().fileName()
            print title,self.metaInformationResolver.currentSource().fileName()
        titleItem = QtGui.QTableWidgetItem(title)
        titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)

        currentRow = self.musicTable.rowCount()
        print currentRow
        self.musicTable.insertRow(currentRow)
        self.musicTable.setItem(currentRow,0,titleItem)
  
        if not self.musicTable.selectedItems():
            self.musicTable.selectRow(0)
            self.mediaObject.setCurrentSource(self.metaInformationResolver.currentSource())


        source = self.metaInformationResolver.currentSource()
        print self.sources
        index = self.sources.index(source) + 1
        print index,"now"
        if len(self.sources) > index:
            self.metaInformationResolver.setCurrentSource(self.sources[index])
        else:
            self.musicTable.resizeColumnsToContents()
            if self.musicTable.columnWidth(0) > 300:
                self.musicTable.setColumnWidth(0, 300)
    """
    def aboutToFinish(self):
        index = self.sources.index(self.mediaObject.currentSource()) + 1
        if len(self.sources) > index:
            self.mediaObject.enqueue(self.sources[index])

    def customplay(self):
        """
        self.videoPlayer.show()
        media = Phonon.MediaSource(self.mediaObject.currentSource())
        self.videoPlayer.load(media)
        self.videoPlayer.play()
        self.videoPlayer.setVolume(0)
        """
        self.mediaObject.play()
        self.videoWidget.show()

    def setupActions(self):
        self.playAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaPlay), "Play",
                self, shortcut="Ctrl+P", enabled=False,
                triggered=self.customplay)

        self.pauseAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaPause),
                "Pause", self, shortcut="Ctrl+A", enabled=False,
                triggered=self.mediaObject.pause)

        self.replayAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_BrowserReload),
                "Replay", self, shortcut="Ctrl+L", enabled=False,
                triggered=self.mediaObject.pause)

        self.stopAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaStop), "Stop",
                self, shortcut="Ctrl+S", enabled=False,
                triggered=self.mediaObject.stop)

        self.nextAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaSkipForward),
                "Next", self, shortcut="Ctrl+N")

        self.previousAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaSkipBackward),
                "Previous", self, shortcut="Ctrl+R")

        self.addFilesAction = QtGui.QAction("Add &Files", self,
                shortcut="Ctrl+F", triggered=self.addFiles)

        self.exitAction = QtGui.QAction("E&xit", self, shortcut="Ctrl+X",
                triggered=self.close)

        self.aboutAction = QtGui.QAction("A&bout", self, shortcut="Ctrl+B",
                triggered=self.about)

        self.aboutQtAction = QtGui.QAction("About &Qt", self,
                shortcut="Ctrl+Q", triggered=QtGui.qApp.aboutQt)

    def setupMenus(self):
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(self.addFilesAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        aboutMenu = self.menuBar().addMenu("&Help")
        aboutMenu.addAction(self.aboutAction)
        aboutMenu.addAction(self.aboutQtAction)

    def fetchutubevdos(self):
        results=youtube_search(str(self.utubeinp.text()))
        while self.utubetbl.rowCount() > 0:
	    self.utubetbl.removeRow(0)
        self.utuberesults=results
        print results
        n=len(results)
        for i in xrange(0,n):
	    currentRow = self.utubetbl.rowCount()
	    self.utubetbl.insertRow(currentRow)
	    titleItem = QtGui.QTableWidgetItem(results[i][0])    
            self.utubetbl.setItem(currentRow,0,titleItem)
            print currentRow,results[i][0]
    
    def setupUi(self):
        bar = QtGui.QToolBar()

        bar.addAction(self.playAction)
        bar.addAction(self.pauseAction)
        bar.addAction(self.stopAction)
        bar.addAction(self.replayAction)

        self.seekSlider = Phonon.SeekSlider(self)
        self.seekSlider.setMediaObject(self.mediaObject)

        self.volumeSlider = Phonon.VolumeSlider(self)
        self.volumeSlider.setAudioOutput(self.audioOutput)
        self.volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum,
                QtGui.QSizePolicy.Maximum)

        volumeLabel = QtGui.QLabel()
        volumeLabel.setPixmap(QtGui.QPixmap('images/volume.png'))

        self.videoWidget = Phonon.VideoWidget()
        self.videoWidget.show()
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Light, QtCore.Qt.darkGray)

        self.timeLcd = QtGui.QLCDNumber()
        self.timeLcd.setPalette(palette)

        self.utubeinp = QtGui.QLineEdit()
        self.utubebtn = QtGui.QPushButton("Get Video!",self)
        self.utubebtn.clicked.connect(self.fetchutubevdos)
        self.utubemsg = QtGui.QLabel("",self)
        self.utubetbl = QtGui.QTableWidget(0,1)
        self.utubetbl.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.utubetbl.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.utubetbl.setHorizontalHeaderLabels(("Youtube Video"))
        self.utubetbl.cellPressed.connect(self.tableYTClicked)


        utubeLayout = QtGui.QVBoxLayout()
        utubeLayout.addWidget(self.utubeinp)
        utubeLayout.addWidget(self.utubebtn)
        utubeLayout.addWidget(self.utubemsg)
        utubeLayout.addWidget(self.utubetbl)

        headers = ("File")

        self.musicTable = QtGui.QTableWidget(0, 1)
        self.musicTable.setHorizontalHeaderLabels(headers)
        self.musicTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.musicTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.musicTable.cellPressed.connect(self.tableClicked)

        seekerLayout = QtGui.QHBoxLayout()
        seekerLayout.addWidget(self.seekSlider)
        seekerLayout.addWidget(self.timeLcd)

        playbackLayout = QtGui.QHBoxLayout()
        playbackLayout.addWidget(bar)
        playbackLayout.addStretch()
        playbackLayout.addWidget(volumeLabel)
        playbackLayout.addWidget(self.volumeSlider)

        tabandvidLayout = QtGui.QHBoxLayout()
        tabandvidLayout.addLayout(utubeLayout)
        tabandvidLayout.addWidget(self.musicTable)
        tabandvidLayout.addWidget(self.videoWidget)
        

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addLayout(tabandvidLayout)
        mainLayout.addLayout(seekerLayout)
        mainLayout.addLayout(playbackLayout)
        widget = QtGui.QWidget()
        widget.setLayout(mainLayout)

        self.setCentralWidget(widget)
        self.setWindowTitle("Apna Music Player")


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Music Player")
    app.setQuitOnLastWindowClosed(True)

    window = MainWindow()
    window.setFixedSize(1000,500)
    window.show()

    sys.exit(app.exec_())
