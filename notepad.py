import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QTextCursor
from PyQt5 import QtCore

form_class = uic.loadUiType("D:\\pyqttest\\2.notepad\\notepad.ui")[0]

class findWindow(QDialog):
    def __init__(self, parent):
        super(findWindow, self).__init__(parent)
        uic.loadUi("D:\\pyqttest\\2.notepad\\find.ui", self)
        self.show()

        self.parent = parent
        self.cursor = self.parent.plainTextEdit.textCursor()
        self.pe = parent.plainTextEdit

        self.pushButtonfindnext.clicked.connect(self.findNextFunction)
        self.pushButtoncancel.clicked.connect(self.close)

        self.radioButtonDown.clicked.connect(self.updownRadiobutton)
        self.radioButtonUp.clicked.connect(self.updownRadiobutton)
        self.up_down = "down"
#==================================================
    def findNextFunction(self):
        pattern = self.lineEdit.text()
        text = self.pe.toPlainText()

        reg = QtCore.QRegExp(pattern)
        self.cursor = self.parent.plainTextEdit.textCursor()

        if self.checkBoxignorecase.isChecked():
            cs = QtCore.Qt.CaseSensitive
        else:
            cs = QtCore.Qt.CaseInsensitive
        
        reg.setCaseSensitivity(cs)
        pos = self.cursor.position()

        if self.up_down == "down":
            index = reg.indexIn(text, pos)
        else:
            pos -= len(pattern) + 1
            index = reg.lastIndexIn(text, pos)
        
        print(index, pos)

        if (index != -1) and (pos > -1) : #검색 결과 O
            self.setCursor(index, len(pattern)+index)
        else:
            self.notFoundMsg(pattern)
        

    def notFoundMsg(self, pattern):
        msgBox = QMessageBox()
        msgBox.setWindowTitle('메모장')
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText('''"{}"을(를) 찾을 수 없습니다.'''.format(pattern))
        msgBox.addButton('확인', QMessageBox.YesRole)
        ret = msgBox.exec_()

    def keyReleaseEvent(self, event):
        if self.lineEdit.text():
            self.pushButtonfindnext.setEnabled(True)
        else:
            self.pushButtonfindnext.setEnabled(False)

    def setCursor(self, start, end):
        print(self.cursor.selectionStart(), self.cursor.selectionEnd())
        self.cursor.setPosition(start)
        self.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, end-start)  #커서를 뒤로 end-start 만큼 이동
        self.pe.setTextCursor(self.cursor)

    def updownRadiobutton(self):
        if self.radioButtonUp.isChecked():
            self.up_down = "up"
        elif self.radioButtonDown.isChecked():
            self.up_down = "down"

#==================================================

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

#==================================================
        self.actionload.triggered.connect(self.loadFunction)
        self.actionsave.triggered.connect(self.saveFunction)
        self.actionsave_as.triggered.connect(self.saveAsFunction)
        self.actionclose.triggered.connect(self.closeEvent)
#==================================================
        self.actionundo.triggered.connect(self.undoFunction)
        self.actioncut.triggered.connect(self.cutFunction)
        self.actioncopy.triggered.connect(self.copyFunction)
        self.actionpaste.triggered.connect(self.pasteFunction)
#==================================================
        self.actionfind.triggered.connect(self.findFunction)
#==================================================
        self.opened = False
        self.opened_file_path = ""

#==================================================
    def save_file(self, fname):
        data = self.plainTextEdit.toPlainText()
        with open(fname, 'w', encoding='UTF8') as f:
            f.write(data)

        self.opened = False
        self.opened_file_path = fname

    def load_file(self, fname):
        with open(fname, encoding='UTF8') as f:
            data = f.read()
        self.plainTextEdit.setPlainText(data)

        self.opened = True
        self.opened_file_path = fname

    def loadFunction(self):
        if self.ischanged(): #열린적 있고 변경사항 O
            ret = self.save_changed_data()

        fname = QFileDialog.getOpenFileName(self)
        if fname[0]:
            self.load_file(fname[0])

    def saveFunction(self):
        if self.opened:
            self.save_file(self.opened_file_path)
        else:
            self.saveAsFunction()

    def saveAsFunction(self):
        fname = QFileDialog.getSaveFileName(self)
        if fname[0]:
            self.save_file(fname[0])

    def closeEvent(self, event):
        if self.ischanged(): #열린적 있고 변경사항 O
            ret = self.save_changed_data()
            
            if ret == 2:
                event.ignore()
    
    def ischanged(self):
        if not self.opened: 
            if self.plainTextEdit.toPlainText().strip():    #열린적 X 에디터 내용 O
                return True
            return False

        current_data = self.plainTextEdit.toPlainText() #현재 데이터
        #파일에 저장된 데이터
        with open(self.opened_file_path, encoding='UTF8') as f:
            file_data = f.read()

        if current_data == file_data: #열린적 있고 변경사항 X
            return False
        else:   #열린적 있고 변경사항 O
            return True

    def save_changed_data(self):
        msgBox = QMessageBox()
        msgBox.setText("변경 내용을 저장하시겠습니까?")
        msgBox.addButton('저장', QMessageBox.YesRole)       #0
        msgBox.addButton('저장 안 함', QMessageBox.NoRole)  #1
        msgBox.addButton('취소', QMessageBox.RejectRole)    #2
        ret = msgBox.exec_()

        if ret == 0:
            self.saveFunction()
        else:
            return ret
#==================================================
    def undoFunction(self):
        self.plainTextEdit.undo()

    def cutFunction(self):
        self.plainTextEdit.cut()

    def copyFunction(self):
        self.plainTextEdit.copy()

    def pasteFunction(self):
        self.plainTextEdit.paste()
#==================================================
    def findFunction(self):
        findWindow(self)
#==================================================

app = QApplication(sys.argv)
mainWindows = WindowClass()
mainWindows.show()
app.exec_()