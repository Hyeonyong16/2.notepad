import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QTextCursor
from PyQt5 import QtCore

form_class = uic.loadUiType("D:\\pyqttest\\2.notepad\\notepad.ui")[0]

#찾기 열었을때 나오는 창
class findWindow(QDialog):
    def __init__(self, parent):
        super(findWindow, self).__init__(parent)
        uic.loadUi("D:\\pyqttest\\2.notepad\\find.ui", self)
        self.show()

        self.parent = parent
        self.cursor = self.parent.plainTextEdit.textCursor()    #커서 위치를 부모(WindowClass)의 PlainText에서 가져옴
        self.pe = parent.plainTextEdit

        self.pushButtonfindnext.clicked.connect(self.findNextFunction)  #찾기 버튼
        self.pushButtoncancel.clicked.connect(self.close)               #취소 버튼

        self.radioButtonDown.clicked.connect(self.updownRadiobutton)    #라운드 버튼(아래로: 오른쪽으로)
        self.radioButtonUp.clicked.connect(self.updownRadiobutton)      #라운드 버튼(위로: 왼쪽으로)
        self.up_down = "down"                                           #라운드 버튼은 하나만 선택되니 현재 어느 방향으로 찾을지 상태
#==================================================
    #찾기 버튼 눌렀을때 실행될 함수
    def findNextFunction(self):
        pattern = self.lineEdit.text()
        text = self.pe.toPlainText()

        reg = QtCore.QRegExp(pattern)
        self.cursor = self.parent.plainTextEdit.textCursor()

        #대소문자 구분 여부(QtCore에서 지원하는 함수 사용)
        if self.checkBoxignorecase.isChecked():
            cs = QtCore.Qt.CaseSensitive
        else:
            cs = QtCore.Qt.CaseInsensitive
        
        reg.setCaseSensitivity(cs)
        pos = self.cursor.position()  

        #찾는 방향 설정
        if self.up_down == "down":
            index = reg.indexIn(text, pos)
        else:
            pos -= len(pattern) + 1
            index = reg.lastIndexIn(text, pos)
        
        print(index, pos)

        #검색했을때 커서 위치 설정(없으면 오류 메시지 출력)
        if (index != -1) and (pos > -1) : #검색 결과 O
            self.setCursor(index, len(pattern)+index)
        else:
            self.notFoundMsg(pattern)
        
    #검색한 단어가 없을때
    def notFoundMsg(self, pattern):
        msgBox = QMessageBox()
        msgBox.setWindowTitle('메모장')
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText('''"{}"을(를) 찾을 수 없습니다.'''.format(pattern))
        msgBox.addButton('확인', QMessageBox.YesRole)
        ret = msgBox.exec_()    #실행하는 함수

    #찾는 창에서 버튼 활성화 이벤트 함수
    def keyReleaseEvent(self, event):
        if self.lineEdit.text():    #입력 창에 단어가 들어오면 활성화
            self.pushButtonfindnext.setEnabled(True)    
        else:                       #입력 창에 단어가 없으면 비활성화
            self.pushButtonfindnext.setEnabled(False)

    #찾은 단어로 커서 설정
    def setCursor(self, start, end):
        print(self.cursor.selectionStart(), self.cursor.selectionEnd())
        self.cursor.setPosition(start)
        self.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, end-start)  #커서를 뒤로 end-start 만큼 이동
        self.pe.setTextCursor(self.cursor)

    #위로 아래로 버튼으로 상태 설정
    def updownRadiobutton(self):
        if self.radioButtonUp.isChecked():
            self.up_down = "up"
        elif self.radioButtonDown.isChecked():
            self.up_down = "down"

#==================================================

#메인 메모장 클래스
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

#==================================================
        self.actionload.triggered.connect(self.loadFunction)        #불러오기 버튼
        self.actionsave.triggered.connect(self.saveFunction)        #저장 버튼
        self.actionsave_as.triggered.connect(self.saveAsFunction)   #다른이름으로 저장 버튼
        self.actionclose.triggered.connect(self.closeEvent)         #닫기 버튼
#==================================================
        self.actionundo.triggered.connect(self.undoFunction)        #되돌리기 버튼
        self.actioncut.triggered.connect(self.cutFunction)          #잘라내기 버튼
        self.actioncopy.triggered.connect(self.copyFunction)        #복사 버튼
        self.actionpaste.triggered.connect(self.pasteFunction)      #붙여넣기 버튼
#==================================================
        self.actionfind.triggered.connect(self.findFunction)        #찾기 버튼
#==================================================
        self.opened = False                                         #닫기 눌렀을때 열렸던 파일인지
        self.opened_file_path = ""                                  #저장 경로 설정

#==================================================
    #저장 기능
    def save_file(self, fname):
        data = self.plainTextEdit.toPlainText()
        with open(fname, 'w', encoding='UTF8') as f:
            f.write(data)

        self.opened = True
        self.opened_file_path = fname

    #불러오기 기능
    def load_file(self, fname):
        with open(fname, encoding='UTF8') as f:
            data = f.read()
        self.plainTextEdit.setPlainText(data)

        self.opened = True
        self.opened_file_path = fname

    #불러오는 기능 함수
    def loadFunction(self):
        if self.ischanged(): #열린적 있고 변경사항 O
            ret = self.save_changed_data()

        fname = QFileDialog.getOpenFileName(self)
        if fname[0]:
            self.load_file(fname[0])

    #저장 기능 함수
    def saveFunction(self):
        if self.opened:
            self.save_file(self.opened_file_path)
        else:
            self.saveAsFunction()

    #다른 이름으로 저장 기능
    def saveAsFunction(self):
        fname = QFileDialog.getSaveFileName(self)
        if fname[0]:
            self.save_file(fname[0])

    #닫기 눌렀을때 이벤트 함수
    def closeEvent(self, event):
        print("close")
        if self.ischanged(): #열린적 있고 변경사항 O
            
            ret = self.save_changed_data()
            
            print(ret)

            if ret == 2:
                event.ignore()
    
    #파일이 기존 열렸을때랑 변경점이 있는지
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
            print("Not changed")
            return False
        else:   #열린적 있고 변경사항 O
            print("changed")
            return True

    #바뀐 내용을 저장할지 물어보는 창을 띄움
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
    #각각 지원하는 함수가 있어서 사용
    #되돌리기
    def undoFunction(self):
        self.plainTextEdit.undo()
   
    #잘라내기
    def cutFunction(self):
        self.plainTextEdit.cut()
   
    #복사
    def copyFunction(self):
        self.plainTextEdit.copy()
   
    #붙여넣기
    def pasteFunction(self):
        self.plainTextEdit.paste()
#==================================================
    #찾기 기능: 누르면 찾기 창(findWindow를 열음)
    def findFunction(self):
        findWindow(self)
#==================================================

app = QApplication(sys.argv)
mainWindows = WindowClass()
mainWindows.show()
app.exec_()