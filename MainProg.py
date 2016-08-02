from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog,QCompleter, QLineEdit, QStringListModel, QMessageBox
from PyQt4.QtCore import Qt
from IDNS_Gui import Ui_Dialog
from dbQuery import *
import sys
import pandas as pd

class Gui_Dialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_Dialog()
        #super(self.__class__, self).__init__()
        self.ui.setupUi(self)
         
        # Connect up the buttons.
        #self.connect(self.ui.btLoad, QtCore.SIGNAL('clicked()'), self.Loaddata)
        self.ui.btLoad.clicked.connect(self.Loaddata)
        self.ui.btRecom.clicked.connect(self.FindItems)
        self.ui.tableWidget.setRowCount(15)
        self.ui.tableWidget.setColumnCount(3)
        # self.ui.cancelButton.clicked.connect(self.reject)

    def Loaddata(self):
        print "Start querying"
        customer=self.ui.text_Name.toPlainText()
        cust_id=self.ui.lnID.text()
        cust_address=self.ui.textType.toPlainText()
        items=self.ui.textItems.toPlainText()
        print customer
        print cust_id
        print cust_address
        print items

        if not cust_id is None and not cust_id=='':
            data=read_table_customer(unicode(cust_id))
            
            if not data is None:
                if len(data)>1:
                    QtGui.QMessageBox.warning(self,  "Warning!","More than one matching record", QMessageBox.Ok)
                elif len(data)==1:
                    for row in data: #can do this because there is only one line
                        self.ui.text_Name.setText(row[4])
                        self.ui.textType.setText(row[2])
                        #Find past purchase history
                        past_pur=read_table_pastpurchase(unicode(cust_id))
                        self.ui.lbPurchase.setText('Found '+ str(len(past_pur))+' matching records')
                        items=[]
                        if len(past_pur)>0:
                            for row in past_pur:
                                if not row is None:
                                    if not row[1] is None or row[1]=='':
                                        phrase=row[1]
                                    if not row[2] is None or row[2]=='':
                                        phrase+=  ', ind.price='+str(row[2])
                                    if not row[3] is None or row[3]=='':
                                        phrase+=', qty= '+str(row[3])
                                    items.append(phrase)
                            self.ui.comboBox.addItems(items)                            
                        else:
                            QtGui.QMessageBox.warning(self,  "Warning!","No past purchase", QMessageBox.Ok)    
                else:
                    QtGui.QMessageBox.warning(self,"Warning!","No matching record", QMessageBox.Ok)
            else:
                QtGui.QMessageBox.information(self,"Warning!","No matching record", QMessageBox.Ok)
    def FindItems(self):
        print "Finding similar items"
        items=self.ui.textItems.toPlainText()
        ListItems=items.split(';') #delimited by ;
        for item in ListItems:
            Recommendation=pd.DataFrame(findItems(unicode(item)))
            print Recommendation[:10]
            #self.tableFriends.clear()
            for i in range(len(Recommendation.index)):
                for j in range(len(Recommendation.columns)):
                    self.ui.tableWidget.setItem(i,j,QtGui.QTableWidgetItem(str(Recommendation.iget_value(i, j))))    
def main(): 

        
    app=QtGui.QApplication(sys.argv)
    form=Gui_Dialog()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()