import sys
from random import *
from os import startfile
from PyQt5 import uic
from datetime import datetime
import sqlite3
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QInputDialog, QCheckBox
from PyQt5.QtWidgets import QDialogButtonBox, QVBoxLayout, QLabel, QPushButton, QTableWidgetItem
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import Qt

ver = 'v. 0.09'


class Caution(QDialog):     # Предупреждение
    def __init__(self, msg):
        super().__init__()
        
        self.setWindowTitle("Ошибка")
        
        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        
        message = QLabel(msg)
        message.setAlignment(Qt.AlignHCenter)
        
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        

class Confirm(QDialog):     # Подтверждение
    def __init__(self, msg):
        super().__init__()
        
        self.setWindowTitle("Подверждение действия")
        
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        

        self.layout = QVBoxLayout()
        
        message = QLabel(msg)
        message.setAlignment(Qt.AlignHCenter)
        
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        
        
class TrivElem(QDialog):    # Диалог создания нового элемента в словаре тривиалочек
    def __init__(self, con, table):
        super().__init__()
        uic.loadUi('newelem.ui', self)
        self.okbutton.clicked.connect(self.save)
        self.con = con
        self.table = table
        cur = self.con.cursor()
        self.items = cur.execute("SELECT type FROM types").fetchall()
        print(self.items)
        for i in self.items:
            self.group.addItem(i[0])
        
    def save(self):
        gr = self.group.currentText()
        gr = self.con.execute("""SELECT id FROM types WHERE type = ?""", (gr,)).fetchall()[0][0]
        return [self.table, [self.name.text(), self.formula.text()], str(gr)]
        
        
class NewElem(TrivElem):
    def __init__(self, con, table):
        super().__init__(con, table)
        self.setWindowTitle("Новое название")
    
    def save(self):
        data = super().save()
        print(data)
        x = "INSERT INTO " + data[0] + "(name, formula, typen) VALUES('" + "', '".join(data[1]) + "', " + data[2] + ')'
        print(x)
        self.con.execute(x)
        self.con.commit()
        self.close()
        
        
class EditElem(TrivElem):
    def __init__(self, con, table, row):
        print('editelem init')
        super().__init__(con, table)
        self.setWindowTitle("Редактировать")
        self.row = self.con.cursor().execute("SELECT * FROM trivials").fetchall()[row]
        print(self.row)
        self.name.setText(self.row[0])
        self.formula.setText(self.row[1])
        gr = self.con.cursor().execute("SELECT type FROM types WHERE id = ?", (self.row[2],)).fetchall()[0][0]
        self.group.setCurrentIndex(self.items.index((gr,)))
    
    def save(self):
        data = super().save()
        print(data)
        x = "UPDATE " + data[0] + " SET name = '" + data[1][0] + \
            "', formula = '" + data[1][1] + "', typen = " + data[2] + ' '
        x += "WHERE name = '" + self.row[0] + "' AND formula = '" + self.row[1] + "'"
        print(x)
        self.con.cursor().execute(x)
        self.con.commit()
        self.close()
        
        
class TestRes(QMainWindow):   # результаты
    def __init__(self, main):
        super().__init__()
        self.setWindowTitle("Результаты теста")
        self.resize(400, 200)
        
        self.message = QLabel(self)
        self.message.setText(f'Ошибка')
        self.message.move(20, 20)
        self.message.resize(360, 120)
        
        self.btn = QPushButton(self)
        self.btn.setText('ОК')
        self.btn.move(280, 140)
        self.btn.clicked.connect(self.leave)
        
        self.main = main
        
    def print(self, n1, n2):
        txt = 'Количество вопросов: ' + str(n2)
        txt += '\nПравильных ответов: ' + str(n1)
        txt += '\nРезультат: ' + str(round((n1 / n2) * 10000) / 100) + '%'
        self.message.setText(txt)
        return txt
        
    def leave(self):
        self.close()
        self.main.show()


class GroupsEdit(QMainWindow):
    def __init__(self, main, mainset):
        super().__init__()
        self.con = sqlite3.connect('trivials.db')
        uic.loadUi('edittable1.ui', self)
        self.setWindowTitle("Редактирование наборов")
        self.table.doubleClicked.connect(self.editrow)
        self.savebtn.clicked.connect(self.save)
        self.main = main
        self.mainset = mainset
        self.btn1.clicked.connect(self.append)
        self.btn2.clicked.connect(self.delete)
        self.update_table()
        
    def update_table(self):
        res = self.con.cursor().execute("SELECT type FROM types").fetchall()
        self.table.setColumnCount(1)
        self.table.setRowCount(0)
        for i, row in enumerate(res):
            self.table.setRowCount(
                self.table.rowCount() + 1)
            for j, elem in enumerate(row):
                self.table.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.table.resizeColumnsToContents()
        self.table.setHorizontalHeaderLabels(["Название"])
        
    def editrow(self, mi):
        print('editrow GroupsEdit')
        rw = self.con.cursor().execute('SELECT * FROM types').fetchall()[mi.row()]
        print(rw)
        text, ok = QInputDialog.getText(self, 'Изменить название', 'Введите новое название.', text=rw[1])
        if ok:
            x = "UPDATE types SET type = '" + text + "' WHERE type = '" + rw[1] + "'"
            print(x)
            self.con.cursor().execute(x)
            self.con.commit()
        self.update_table()
        self.main.update_table()
    
    def save(self):
        self.mainset.update_collections()
        self.close()
    
    def delete(self):
        cur = self.con.cursor()
        a = self.table.currentRow()
        print(a)
        dl = cur.execute('SELECT type from types').fetchall()[a][0]
        msg = Confirm('Действительно удалить "' + dl + '"?\nВместе с набором удаляется всё содержимое.')
        if msg.exec_():
            cur.execute('DELETE from trivials WHERE typen = (SELECT id FROM types WHERE type = ?)', (dl,))
            cur.execute('DELETE from types WHERE type = ?', (dl,))
            self.con.commit()
            
        self.update_table()
        self.main.update_table()
            
    def append(self):
        text, ok = QInputDialog.getText(self, 'Новый набор', 'Введите название.')
        if ok:
            x = "INSERT INTO types(type) VALUES('" + text + "')"
            print(x)
            self.con.cursor().execute(x)
            self.con.commit()
            self.update_table()
        

class ViewTable(QMainWindow):    
    def __init__(self):
        super().__init__()
        uic.loadUi('edittable.ui', self)
        self.savebtn.clicked.connect(self.savefile)
        self.file = ''
        self.hdrs = []
        
    def update_table(self, res, n):
        self.table.setColumnCount(n)
        self.table.setRowCount(0)
        # Заполняем таблицу элементами
        for i, row in enumerate(res):
            self.table.setRowCount(
                self.table.rowCount() + 1)
            for j, elem in enumerate(row):
                if j == 2:
                    try:
                        elem = self.con.cursor().execute('SELECT type FROM types WHERE id = ?',
                                                         (elem,)).fetchall()[0][0]
                    except:
                        pass
                self.table.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.table.resizeColumnsToContents()
        self.table.setHorizontalHeaderLabels(self.hdrs)

    def savefile(self):
        self.close()
        
    def editrow(self, mi):
        print(mi.row())


class EditTrivials(ViewTable):
    def __init__(self, main):
        super().__init__()
        try:
            self.con = sqlite3.connect('trivials.db')
        except Exception as e:
            print('AAAAAAAAAAAA', e.__class__.__name__)
        self.setWindowTitle('Редактирование наборов')
        self.btn1.clicked.connect(self.createnew)
        self.btn2.clicked.connect(self.delete)
        self.hdrs = ['Название', 'Формула', 'Набор']
        self.table.doubleClicked.connect(self.editrow)
        
        self.btn3 = QPushButton('Наборы', self)
        self.btn3.move(20, 520)
        self.btn3.setFont(QFont('MS Shell Dlg 2', 9))
        self.grpedit = GroupsEdit(self, main)
        self.btn3.clicked.connect(self.opergrpedit)
        
        self.update_table()

    def createnew(self):
        new = NewElem(self.con, 'trivials')
        new.exec()
        self.update_table()
        
    def delete(self):
        cur = self.con.cursor()
        a = self.table.currentRow()
        print(a)
        dl = cur.execute('SELECT name from trivials').fetchall()[a][0]
        msg = Confirm('Действительно удалить "' + dl + '"?')
        if msg.exec_():
            cur.execute('DELETE from trivials WHERE name = ?', (dl,))
            self.con.commit()
            self.update_table()
        
    def update_table(self):
        cur = self.con.cursor()
        res = cur.execute('SELECT * from trivials').fetchall()
        super().update_table(res, 3)
        
    def editrow(self, mi):
        print('edittrivials')
        super().editrow(mi)
        edit = EditElem(self.con, 'trivials', mi.row())
        edit.exec()
        self.update_table()
        
    def opergrpedit(self):
        self.grpedit.show()
        
        
class ViewResults(ViewTable):
    def __init__(self):
        super().__init__()
        self.con = sqlite3.connect('results.db')
        self.setWindowTitle('Просмотр результатов')
        self.btn1.clicked.connect(self.reserase)
        self.btn1.setText('Очистить')
        self.btn2.hide()
        self.table.doubleClicked.connect(self.editrow)
        self.hdrs = ['Имя', 'Дата', 'Время', 'Режим', 'Группы', 'Всего', 'Правильно', '%']
        self.update_table()
   
    def reserase(self):
        msg = Confirm('Действительно очистить?')
        if msg.exec():
            self.con.cursor().execute("DELETE FROM results")
            self.con.commit()
        self.update_table()
        
    def update_table(self):
        cur = self.con.cursor()
        res = cur.execute('SELECT * from results').fetchall()
        super().update_table(res, 8)
        
    def editrow(self, mi):
        print('edittrivials')
        super().editrow(mi)
        rw = self.con.cursor().execute('SELECT * FROM results').fetchall()[mi.row()]
        defname = rw[0]
        text, ok = QInputDialog.getText(self, 'Введите имя', 'Под этим именем запишется ваш результат.', text=defname)
        if ok:
            x = "UPDATE results SET name = '" + text + "' WHERE name = '" + defname + \
                "' AND date = '" + rw[1] + "' AND time = '" + rw[2] + "'"
            print(x)
            self.con.cursor().execute(x)
            self.con.commit()
        self.update_table()
        
        
class Test:
    def __init__(self, testwindow, n, dic):
        self.testwindow = testwindow
        self.settings = self.testwindow.main.sett.getsettings()
        
        self.dic = dic.copy()
        self.constdic = dic.copy()

        if self.settings['rnum']:
            self.testwindow.gotright.show()
            self.testwindow.gotright.setText(f'Правильных ответов')
        else:
            self.testwindow.gotright.hide()
        
        self.qnum = 0
        self.rnum = 0
        self.n1 = n
        self.testwindow.nextquestion.setText('Далее')
        self.dic2 = {}
        print(self.settings)
    
    def generate(self):
        print('generate')
        if self.settings['rnum']:
            self.testwindow.gotright.setText(f'Правильных ответов: {self.rnum} / {self.qnum}')
        self.testwindow.qnumber.setText(f'Вопрос №{self.qnum + 1}')
        self.qnum += 1
        if self.qnum >= self.n1 and self.n1 not in (-1, 0):
            self.testwindow.nextquestion.setText('Завершить тест')
        self.n = choice((1, 2))  # 1  спрашивается тривиалочка, 2 - спрашивается формула.
        print('mode:', self.n1)
        if not self.dic or len(self.dic) < 4:
            self.testwindow.endtest()
            return 'ERROR'
        self.asked = choice(list(self.dic))
        varis = sample(list(self.constdic), 3)
        while self.asked in varis:
            varis = sample(list(self.constdic), 3)
        varis += [self.asked]
        shuffle(varis)
        
        if self.n == 1:
            for i in enumerate(self.testwindow.anslist):
                i[1].setText(varis[i[0]])
            question = f'{self.dic[self.asked]} имеет тривиальное название...'
        else:
            for i in enumerate(self.testwindow.anslist):
                i[1].setText(self.constdic[varis[i[0]]])
            question = f'{self.asked} имеет формулу...'
        return question
        
                
class TestMenu(QMainWindow):
    def __init__(self, main):
        super().__init__()
        self.main = main
        uic.loadUi('testwindow.ui', self)
        self.setWindowTitle("Тестирование")
        self.anslist = [self.v1, self.v2, self.v3, self.v4]
        self.nextquestion.clicked.connect(self.nextq)
        self.menu.clicked.connect(self.leavetest)
        self.testres = TestRes(main)
        self.endtest2.hide()
        self.endtest2.clicked.connect(self.endtest)
        self.bck.setPixmap(QPixmap('images/background.png'))
            
    def keyPressEvent(self, qKeyEvent):
        print(qKeyEvent.key())
        if qKeyEvent.key() == Qt.Key_Return: 
            self.nextq()
        if qKeyEvent.key() == Qt.Key_End:
            if self.n == -1:
                self.endtest()
            else:
                self.leavetest()
        else:
            super().keyPressEvent(qKeyEvent)
        
    def start(self, n, dic):
        self.statusBar().showMessage('')
        self.n = n
        if n == -1:
            self.endtest2.show()
        else:
            self.endtest2.hide()
        try:
            self.testsys = Test(self, n, dic)
            a = self.testsys.generate()
            self.text.setText(a)
        except Exception as e:
            print(e.__class__.__name__)
            
    def nextq(self):
        dic2 = self.testsys.dic2
        print('\nnextq')
        for i in self.anslist:
            if i.isChecked():
                x = (i.text(), self.testsys.dic[self.testsys.asked], self.testsys.dic.get(i.text(), ''))
                if x[0] == x[1] or x[1] == x[2]:        # Проверка правильности ответа
                    dic2[self.testsys.asked] = dic2.get(self.testsys.asked, 0) + 1
                    self.testsys.rnum += 1
                    if dic2[self.testsys.asked] == 5 and self.n == 0:
                        self.testsys.dic.pop(self.testsys.asked)
                    if not self.testsys.settings['last']:
                        break
                    self.statusBar().showMessage('Правильно!')
                else:
                    if not self.testsys.settings['last']:
                        break
                    x1 = self.testsys.asked
                    x2 = self.testsys.dic[x1]
                    if self.testsys.n == 2:       # В зависимости от рода вопроса, выводит в правильном порядке
                        x2, x1 = x1, x2
                    self.statusBar().showMessage(f'Неправильно! {x2} - {x1}')
                break
        else:
            print('choose')
            return
        if self.testsys.qnum >= self.n and self.n not in (-1, 0):    # -1 - неограниченное число вопросов, 0 - режим "до пяти"
            print('test end')
            self.endtest()
            return
        self.text.setText(self.testsys.generate())
        
    def leavetest(self):
        print('leavetest')
        msg = Confirm('Тест не завершён. Выйти?')
        if msg.exec():
            self.close()
            self.main.show()
        
    def endtest(self):
        self.close()
        con = sqlite3.connect('results.db')
        t = self.testres.print(self.testsys.rnum, self.testsys.qnum) + '\n'
        tm = datetime.now()
        if self.main.sett.getsettings()['save']:
            try:
                defname = con.cursor().execute('SELECT name FROM results').fetchall()[-1][0]
            except:
                defname = ''
            text, ok = QInputDialog.getText(self, 'Введите имя', 'Под этим именем запишется ваш результат.', text=defname)
            if ok:
                ns = []
                for i in self.main.sett.trivgroups:
                    if i.isChecked():
                        ns.append('"' + i.text() + '"')
                que = "INSERT INTO results(name, date, time, mode, types, questions, right, result) VALUES("
                name = "'" + str(text) + "'"
                d = "'" + tm.strftime("%d.%m.%Y") + "'"
                t = "'" + tm.strftime("%H:%M") + "'"
                modes = {0: 'До 5 правильных',
                         -1: 'Бесконечный'}
                ns = "'" + ', '.join(ns) + "'"
                perc = "'" + str(round((self.testsys.rnum / self.testsys.qnum) * 10000) / 100) + '%' + "'"
                m = "'" + modes.get(self.n, 'Ограниченное количество вопросов') + "'"
                que += ', '.join([name, d, t, m, ns, str(self.testsys.qnum), str(self.testsys.rnum), perc]) + ')'
                print(que)
                con.cursor().execute(que)
                con.commit()
            
        self.testres.show()
        print('endtest')
        

class About(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("О программе")
        self.resize(500, 500)
        
        self.qtbutton = QPushButton("ОК", self)
        self.qtbutton.clicked.connect(self.quitabout)
        self.qtbutton.move(380, 450)

        self.message = QLabel(self)
        msg = open("О программе.txt", 'r', encoding='utf8').read()
        self.message.setText(f'Тест "Тривиальные названия веществ" {ver}.\n' + msg)
        self.message.move(20, 20)
        self.message.resize(460, 250)
        self.spr = QPushButton('Справка', self)
        self.spr.clicked.connect(self.spravka)
        self.spr.move(260, 450)
        
    def quitabout(self):
        self.close()
        
    def spravka(self):
        try:
            startfile("Справка.txt")
        except Exception:
            msg = Caution('Файл со справкой был удалён или перемещён.')
            msg.exec()
        
        
class Settings(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('settingswindow.ui', self)
        self.setWindowTitle("Настройки")
        self.editwindow = EditTrivials(self)
        self.winresults = ViewResults()
        con = sqlite3.connect('trivials.db')
        self.cur = con.cursor()
        self.trivgroups = []
        for i in self.cur.execute("SELECT type FROM types").fetchall():
            a = QCheckBox(i[0])
            self.verticalLayout_3.addWidget(a)
            self.trivgroups.append(a)
        self.allbuttons = [self.limitrb, self.get5rightb, self.nolimitrb,
                           self.lastcheck, self.rnumcheck, self.savecheck]
        self.setWindowTitle("Настройки")
        self.applybtn.clicked.connect(self.apply)
        self.blockq(self.limitrb.isChecked())
        self.limitrb.toggled.connect(self.blockq)
        self.resetbtn.clicked.connect(self.reset)
        self.viewresults.clicked.connect(self.results)
        self.tableedit.clicked.connect(self.openedit)
        try:
            self.loadsettings()
        except Exception as e:
            msg = Caution('Не удалось импортировать прошлые настройки.')
            if msg.exec():
                pass
            for i in self.trivgroups:
                i.setChecked(False)
            self.trivgroups[0].setChecked(True)
            self.limitrb.setChecked(True)
            print('ERROR loadsettings:', e.__class__.__name__)
            
    def update_collections(self):
        for i in reversed(range(self.verticalLayout_3.count())): 
            self.verticalLayout_3.itemAt(i).widget().setParent(None)
        self.trivgroups = []
        for i in self.cur.execute("SELECT type FROM types").fetchall():
            a = QCheckBox(i[0])
            self.verticalLayout_3.addWidget(a)
            self.trivgroups.append(a)
            
    def openedit(self):
        print('openedit')
        self.editwindow.show()
        
    def reset(self):
        msg = Confirm('Действительно сбросить?')
        if msg.exec():
            for i in self.allbuttons:
                i.setChecked(False)
            self.limitrb.setChecked(True)
            for i in self.trivgroups:
                i.setChecked(False)
            self.trivgroups[0].setChecked(True)
            self.qnum.setValue(10)
    
    def loadsettings(self):
        con = sqlite3.connect('config.db')
        for i in (self.allbuttons + self.trivgroups):
            a = con.cursor().execute('SELECT val FROM config WHERE btn = ?', (i.text(),)).fetchall()
            print(i, a)
            if a:
                if a[0][0] == 1:
                    i.setChecked(True)
                else:
                    i.setChecked(False)
        qnum = con.cursor().execute('SELECT val FROM config WHERE btn = "qnum"').fetchall()
        if qnum:
            self.qnum.setValue(qnum[0][0])
        else:
            self.qnum.setValue(10)
        
    def apply(self):
        con = sqlite3.connect('config.db')
        for i in (self.allbuttons + self.trivgroups):
            a = i.isChecked()
            if a:
                a = 1
            else:
                a = 0
            if not con.cursor().execute('SELECT * FROM config WHERE btn = ?', (i.text(),)).fetchall():
                con.cursor().execute('INSERT INTO config(btn, val) VALUES(?, ?)', (i.text(), a)).fetchall()
            con.cursor().execute('UPDATE config SET val = ? WHERE btn = ?', (a, i.text(),)).fetchall()
        qnum = self.qnum.value()
        con.cursor().execute('UPDATE config SET val = ? WHERE btn = "qnum"', (qnum,)).fetchall()
        con.commit()
        self.close()
            
    def results(self):
        self.winresults.update_table()
        self.winresults.show()
        
    def getsettings(self):
        print('\ngetsettings')
        dic = list(map(lambda x: x.text(), filter(lambda x: x.isChecked(), self.trivgroups)))
        print(dic)
        if self.limitrb.isChecked():
            limt = self.qnum.value()
        elif self.get5rightb.isChecked():
            limt = 0
        else:
            limt = -1
        self.sets = {'rnum': self.rnumcheck.isChecked(),
                     'last': self.lastcheck.isChecked(),
                     'save': self.savecheck.isChecked(),
                     'limt': limt,
                     'dict': dic}
        print('getsettings end')
        return self.sets
    
    def blockq(self, b):
        if b:
            self.qnum.setReadOnly(False)
            self.qnum.setStyleSheet("QSpinBox{background-color : #FFFFFF;}")
        else:
            self.qnum.setReadOnly(True)
            self.qnum.setStyleSheet("QSpinBox{background-color : #DDDDDD;}")


class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('mainwindow.ui', self)
        self.setWindowTitle("Тривиальные названия веществ - тест")
        self.statusBar().showMessage(ver)
        self.bck.setPixmap(QPixmap('images/background.png'))
        
        self.sett = Settings()
        self.test = TestMenu(self)
        self.abtt = About()
        
        self.exit.clicked.connect(self.exittest)
        self.start.clicked.connect(self.starttest)
        self.settings.clicked.connect(self.opensettings)
        self.about.clicked.connect(self.openabout)
        
    def starttest(self):
        print('starttest')
        
        d = self.sett.getsettings()["dict"]
        print(d)
        if not d:
            msg = Caution('Набор не выбран.')
            if msg.exec():
                print('Набор не выбран.')
                return
        con = sqlite3.connect('trivials.db')
        que = 'SELECT name, formula FROM trivials WHERE typen IN (SELECT id FROM types WHERE type in (' + str(d)[1:-1] + '))'
        dct = con.cursor().execute(que).fetchall()
        print('dct', dct, d)
        dic = {}
        for i in dct:
            dic[i[0]] = i[1]
        print(dic)
        if not dic or len(dic) < 4:
            msg = Caution('В наборе слишком мало элементов.')
            msg.exec()
        else:
            sets = self.sett.getsettings()
            if sets['dict'] == '("")':
                msg = Caution('Пожалуйста, выберите хотя бы один набор названий.')
                if msg.exec():
                    pass
                return
            self.test.show()
            self.test.start(sets['limt'], dic)
            self.close()
        
    def opensettings(self):
        print('opensettings')
        self.sett.show()
            
    def openabout(self):
        print('openabout')
        self.abtt.show()
            
    def exittest(self):
        print('exittest')
        msg = Confirm('Выйти?')
        if msg.exec():
            QCoreApplication.instance().quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainMenu()
    ex.show()
    sys.exit(app.exec_())