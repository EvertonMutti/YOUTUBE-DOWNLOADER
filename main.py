# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 17:33:49 2022

@author: Everton Castro
"""
from sys import argv, exit
from pytube import YouTube
from Design.Splash_Intro import *
from Design.Design import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5 import QtGui
from re import search
from threading import Thread


counter = 0

class ThreadWithReturnValue(Thread):
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

class NewWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        super().setupUi(self)
        self.setWindowIcon(QtGui.QIcon('Icon.png'))
        self.pb_Caminho.clicked.connect(self.abrir_pasta)
        self.pb_Download.clicked.connect(self.download_verify)
        self.cb_Video.clicked.connect(self.video)
        self.rb_Mp3.clicked.connect(self.mp3)
        
    def download_verify(self):
        self.progressBar.setProperty("value", 0)
        mensagem = QMessageBox()
        mensagem.setWindowTitle('Alerta')      
        mensagem.setWindowIcon(QtGui.QIcon('Icon.png'))
        mensagem.setIcon(QMessageBox.Information)
        mensagem.setStyleSheet ( "QLabel{AlignHCenter;}" )
        mensagem.setStandardButtons(QMessageBox.Ok)
        
        if not (self.rb_Mp3.isChecked()) and  not (self.rb_Mp4.isChecked()):
            mensagem.setText('Selectione a extensão')
            mensagem.setInformativeText("Escolha entre as opções de:\nmp3 ou mp4")
            mensagem.exec()
            
        elif (self.le_Link.text()) == '': 
            mensagem.setText('Digite algum link para Download')
            mensagem.setInformativeText("")
            mensagem.exec()
            
        elif search(r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$", 
                    self.le_Link.text()) == None:
            mensagem.setText('Isso não me parece um link do youtube')
            mensagem.setInformativeText("Copie e cole um link válido")        
            mensagem.exec()             
            
        elif (self.le_Caminho.text()) == '':
            mensagem.setText('Digite o local de download')
            mensagem.setInformativeText("Digite ou aperte no botão caminho para selecionar o diretório para download") 
            mensagem.exec()
            
        else:
            try:
                ThreadWithReturnValue(target = Download,
                       args=(self.le_Link.text(),self.le_Caminho.text()
                             ,self.rb_Mp4.isChecked(), self.rb_Mp3.isChecked(),
                             self.cb_Video.isChecked()), demon = True).start()
            except Exception:
                mensagem = QMessageBox()
                mensagem.setWindowTitle('Alerta')      
                mensagem.setWindowIcon(QtGui.QIcon('Icon.png'))
                mensagem.setIcon(QMessageBox.Information)
                mensagem.setStyleSheet ( "QLabel{AlignHCenter;}" )
                mensagem.setStandardButtons(QMessageBox.Ok)
                mensagem.setText('Ocorreu algum erro, verifique o link de download ou o caminho da pasta')
                mensagem.exec()    
            
        #if (self.le_Link.text()) != None and (self.le_Caminho.text()) != None:
            #self.Download()
            
    def video(self):
        if (self.cb_Video.isChecked()):
            self.rb_Mp4.setChecked(True)
    
    def mp3(self):
        if (self.rb_Mp3.isChecked()):
            self.cb_Video.setChecked(False)
            
    def abrir_pasta(self):
        path = QFileDialog.getExistingDirectory(
            self.centralwidget,
            'Procurando pastas',
            'C:/'
            #options = QFileDialog.DontUseNativeDialog
            )
        self.le_Caminho.setText(path)
        
   
class Intro(QMainWindow, Splash_Intro):
    def __init__(self, parent = None):
        super().__init__(parent)
        super().setupUi(self)
        self.setWindowIcon(QtGui.QIcon('Icon.png'))
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progresso)
        self.timer.start(18)
        
    def progresso(self):       
        
        global counter

        if counter > 100:
           self.timer.stop()
           self.close()
        counter += 1
        
def on_progress(vid, chunk, bytes_remaining):
    total_size = vid.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    percentage_of_completion = round(percentage_of_completion,2)
    main.progressBar.setProperty("value", percentage_of_completion)

def complete_callback( stream, file_handle):
    print("downloading finished")
        
def Download(link, path, mp4, mp3, video):
    yt = YouTube(link, on_progress_callback = on_progress, on_complete_callback=complete_callback)
    try:
        if (mp4):
            if (video):
                stream = yt.streams.filter(file_extension='mp4').get_highest_resolution()
            else:
                stream = yt.streams.filter(only_audio= True, file_extension='mp4').last() #order_by('resolution')
            stream.download(path)
        elif (mp3):
            stream = yt.streams.filter(only_audio= True, file_extension='mp4').last()
            stream.download(path, filename = f'{yt.title}.mp3')              
        return True
                
    except Exception:
        return False
            
if __name__ == '__main__':
    qt = QApplication(argv)
    window = Intro() 
    window.show()
    qt.exec_()
    main = NewWindow()
    main.show()
    exit(qt.exec_())