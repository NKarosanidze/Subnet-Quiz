import sys
import sqlite3
import ipaddress
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtGui import QPainter


class IPDatabase:
    def __init__(self, db_name="ip_slash.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()
        if not self.has_data():
            self.populate_initial_ips()

    def create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS ip_slash (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_prefix TEXT NOT NULL
        )
        '''
        self.conn.execute(query)
        self.conn.commit()

    def has_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ip_slash")
        count = cursor.fetchone()[0]
        return count > 0

    def add_ip_prefix(self, ip_prefix):
        query = "INSERT INTO ip_slash (ip_prefix) VALUES (?)"
        self.conn.execute(query, (ip_prefix,))
        self.conn.commit()

    def update(self, record_id, new_prefix):
        query = "UPDATE ip_slash SET ip_prefix=? WHERE id=?"
        self.conn.execute(query, (new_prefix, record_id))
        self.conn.commit()

    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, ip_prefix FROM ip_slash ORDER BY id")
        return cursor.fetchall()

    def get_random_ip_prefix(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ip_prefix FROM ip_slash ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else None

    def delete(self, record_id):
        query = "DELETE FROM ip_slash WHERE id=?"
        self.conn.execute(query, (record_id,))
        self.conn.commit()

    def populate_initial_ips(self):
        ip_prefixes = [
            "10.0.0.0/8",
            "10.10.0.0/16",
            "10.10.10.0/24",
            "10.10.10.128/25",
            "172.16.0.0/12",
            "172.16.0.0/19",
            "172.16.32.0/20",
            "172.16.48.0/21",
            "172.16.56.0/22",
            "172.16.60.0/23",
            "172.16.62.0/24",
            "172.16.62.128/25",
            "172.16.62.192/26",
            "192.168.0.0/16",
            "192.168.1.0/24",
            "192.168.1.128/25",
            "192.168.1.192/26",
            "192.168.1.224/27",
            "192.168.1.240/28",
            "192.168.1.248/29",
            "192.168.1.252/30",
            "192.168.1.254/31",
            "198.51.100.0/24",
            "198.51.100.0/26",
            "198.51.100.64/27",
            "198.51.100.96/28",
            "198.51.100.112/29",
            "198.51.100.120/30",
            "198.51.100.124/31",
            "203.0.113.0/24",
            "203.0.113.128/25",
            "203.0.113.192/26",
            "203.0.113.224/27",
            "203.0.113.240/28",
            "203.0.113.248/29",
            "203.0.113.252/30",
            "203.0.113.254/31",
        ]
        for ip in ip_prefixes:
            self.add_ip_prefix(ip)




class IPSubnetQuiz(QWidget):
    def __init__(self):
        super().__init__()
        self.db = IPDatabase()
        self.current_ip_prefix = None
        self.correct_count = 0
        self.incorrect_count = 0
        self.total_questions = 0
        self.chart_windows = []
        self.is_lecturer = False
        self.init_ui()
        self.next_question()

    def init_ui(self):
        self.setWindowTitle("Subnet Quiz - Network, Broadcast, Mask")
        self.setGeometry(300, 300, 800, 800)
        self.setStyleSheet("background-color: #1C2833;")

        self.layout = QVBoxLayout()

        self.instruction_label = QLabel(
            "<b style='color:white;font-size: 20px; font-family:Sylfaen;'>პირობა:</b><br>"
            "<span style='color:white;font-size: 20px; font-family:Sylfaen;'>რა არის Network Address, Broadcast Address და Subnet Mask ქვიზში მოცემულ IP-სთვის?</span>"
        )
        self.instruction_label.setWordWrap(True)
        self.layout.addWidget(self.instruction_label)

        self.ip_label = QLabel("")
        self.ip_label.setAlignment(Qt.AlignCenter)
        self.ip_label.setStyleSheet("font-size: 28px; font-weight: bold; color: lightblue; font-family: Sylfaen;")
        self.layout.addWidget(self.ip_label)


        self.net_label = QLabel("Network Address:")
        self.net_label.setStyleSheet("color: white; font-weight: bold; font-size: 18px; font-family: Sylfaen;")
        self.net_input = QLineEdit()
        self.net_input.setPlaceholderText("მაგ: 1.1.1.1")
        self.net_input.setStyleSheet("""
            color: white;
            background-color: #2E4053;
            font-size: 20px;
            font-family: Sylfaen;
            border: 1px solid #ABB2B9;
            border-radius: 5px;
            padding: 5px;
        """)


        self.bc_label = QLabel("Broadcast Address:")
        self.bc_label.setStyleSheet("color: white; font-weight: bold; font-size: 18px; font-family: Sylfaen;")
        self.bc_input = QLineEdit()
        self.bc_input.setPlaceholderText("მაგ: 1.1.1.1")
        self.bc_input.setStyleSheet("""
            color: white;
            background-color: #2E4053;
            font-size: 20px;
            font-family: Sylfaen;
            border: 1px solid #ABB2B9;
            border-radius: 5px;
            padding: 5px;
        """)


        self.mask_label = QLabel("Subnet Mask:")
        self.mask_label.setStyleSheet("color: white; font-weight: bold; font-size: 18px; font-family: Sylfaen;")
        self.mask_input = QLineEdit()
        self.mask_input.setPlaceholderText("მაგ: 255.255.255.255")
        self.mask_input.setStyleSheet("""
            color: white;
            background-color: #2E4053;
            font-size: 20px;
            font-family: Sylfaen;
            border: 1px solid #ABB2B9;
            border-radius: 5px;
            padding: 5px;
        """)

        for widget in [
            self.net_label, self.net_input,
            self.bc_label, self.bc_input,
            self.mask_label, self.mask_input
        ]:
            self.layout.addWidget(widget)


        btn_layout = QHBoxLayout()
        self.check_btn = QPushButton("Check Answer")
        self.check_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980B9;
                color: white;
                font-size: 18px;
                font-family: Sylfaen;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
        """)
        self.next_btn = QPushButton("Next")
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-size: 18px;
                font-family: Sylfaen;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2ECC71;
            }
        """)

        self.check_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.next_question)

        btn_layout.addWidget(self.check_btn)
        btn_layout.addWidget(self.next_btn)

        self.layout.addLayout(btn_layout)

        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-weight: bold; font-size: 20px; color: #D35400; font-family: Sylfaen;")
        self.layout.addWidget(self.result_label)



        self.add_ip_input = QLineEdit()
        self.add_ip_input.setPlaceholderText("ახალი IP (მაგ. 192.168.5.0/24)")
        self.add_ip_input.setStyleSheet(self.mask_input.styleSheet())
        self.add_btn = QPushButton("Add IP")
        self.add_btn.setStyleSheet(self.next_btn.styleSheet())
        self.add_btn.clicked.connect(self.add_new_ip)

        self.list_btn = QPushButton("List All IPs")
        self.list_btn.setStyleSheet(self.next_btn.styleSheet())
        self.list_btn.clicked.connect(self.list_all_ips)

        self.update_input_id = QLineEdit()
        self.update_input_id.setPlaceholderText("ID for Update")
        self.update_input_id.setStyleSheet(self.mask_input.styleSheet())
        self.update_input_prefix = QLineEdit()
        self.update_input_prefix.setPlaceholderText("New IP Prefix")
        self.update_input_prefix.setStyleSheet(self.mask_input.styleSheet())
        self.update_btn = QPushButton("Update IP")
        self.update_btn.setStyleSheet(self.next_btn.styleSheet())
        self.update_btn.clicked.connect(self.update_ip)

        self.delete_input_id = QLineEdit()
        self.delete_input_id.setPlaceholderText("ID for Delete")
        self.delete_input_id.setStyleSheet(self.mask_input.styleSheet())
        self.delete_btn = QPushButton("Delete IP")
        self.delete_btn.setStyleSheet(self.next_btn.styleSheet())
        self.delete_btn.clicked.connect(self.delete_ip)


        for widget in [
            self.add_ip_input, self.add_btn,
            self.list_btn,
            self.update_input_id, self.update_input_prefix, self.update_btn,
            self.delete_input_id, self.delete_btn
        ]:
            widget.hide()
            self.layout.addWidget(widget)


        self.lecturer_btn = QPushButton("Lecturer Mode")
        self.lecturer_btn.setStyleSheet("""
            QPushButton {
                background-color: #E67E22;
                color: white;
                font-size: 18px;
                font-family: Sylfaen;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #D35400;
            }
        """)
        self.lecturer_btn.clicked.connect(self.toggle_lecturer_mode)
        self.layout.addWidget(self.lecturer_btn)

        self.setLayout(self.layout)




    def toggle_lecturer_mode(self):
        if self.is_lecturer:
            # Lecturer mode OFF
            self.is_lecturer = False
            QMessageBox.information(self, "Lecturer Mode", "ლექტორის რეჟიმი გამოირთო.")
            for widget in [
                self.add_ip_input, self.add_btn,
                self.list_btn,
                self.update_input_id, self.update_input_prefix, self.update_btn,
                self.delete_input_id, self.delete_btn
            ]:
                widget.hide()
        else:
            password, ok = QInputDialog.getText(self, "Lecturer Mode", "შეიყვანე პაროლი:", QLineEdit.Password)
            if ok:
                if password == "admin123":
                    self.is_lecturer = True
                    QMessageBox.information(self, "Lecturer Mode", "ლექტორის რეჟიმი ჩართულია!")
                    for widget in [
                        self.add_ip_input, self.add_btn,
                        self.list_btn,
                        self.update_input_id, self.update_input_prefix, self.update_btn,
                        self.delete_input_id, self.delete_btn
                    ]:
                        widget.show()
                else:
                    QMessageBox.warning(self, "Error", "პაროლი არასწორია!")

    def next_question(self):
        self.current_ip_prefix = self.db.get_random_ip_prefix()
        self.ip_label.setText(self.current_ip_prefix)
        self.result_label.clear()
        self.net_input.clear()
        self.bc_input.clear()
        self.mask_input.clear()

    def check_answer(self):
        try:
            net = ipaddress.ip_network(self.current_ip_prefix.strip(), strict=False)
        except Exception:
            QMessageBox.warning(self, "Error", f"Invalid IP/Prefix from DB: {self.current_ip_prefix}")
            return

        user_net = self.net_input.text().strip()
        user_bc = self.bc_input.text().strip()
        user_mask = self.mask_input.text().strip()

        correct_net = str(net.network_address)
        correct_bc = str(net.broadcast_address)
        correct_mask = str(net.netmask)

        correct = True
        msg = ""

        if user_net == correct_net:
            msg += "<span style='color:lightblue;'>Network Address: Correct</span><br>"
        else:
            msg += f"<span style='color:lightpink;'>Network Address: Incorrect (Correct: {correct_net})</span><br>"
            correct = False

        if user_bc == correct_bc:
            msg += "<span style='color:lightblue;'>Broadcast Address: Correct</span><br>"
        else:
            msg += f"<span style='color:lightpink;'>Broadcast Address: Incorrect (Correct: {correct_bc})</span><br>"
            correct = False

        if user_mask == correct_mask:
            msg += "<span style='color:lightblue;'>Subnet Mask: Correct</span>"
        else:
            msg += f"<span style='color:lightpink;'>Subnet Mask: Incorrect (Correct: {correct_mask})</span>"
            correct = False

        self.result_label.setText(msg)

        if correct:
            self.correct_count += 1
            QMessageBox.information(self, "Result", "ყველაფერი სწორია! სამხარა შენით იამაყებს.")
        else:
            self.incorrect_count += 1
            QMessageBox.warning(self, "Result", "რაცხა ოურიე. კიდო ცადე, რავქნაა.")

        self.total_questions += 1

        if self.total_questions % 10 == 0:
            self.show_chart()




    def show_chart(self):
        series = QPieSeries()
        series.append("სწორი პასუხები", self.correct_count)
        series.append("არასწორი პასუხები", self.incorrect_count)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("შენი შედეგები ბოლო 10 სავარჯიშოზე")
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        chart_window = QWidget()
        chart_window.setWindowTitle("Quiz Results Chart")
        layout = QVBoxLayout()
        layout.addWidget(chart_view)
        chart_window.setLayout(layout)
        chart_window.resize(400, 300)
        chart_window.show()

        self.chart_windows.append(chart_window)

        self.correct_count = 0
        self.incorrect_count = 0
        self.total_questions = 0


    def add_new_ip(self):
        new_ip = self.add_ip_input.text().strip()
        if new_ip:
            self.db.add_ip_prefix(new_ip)
            QMessageBox.information(self, "წარმატება", f"ახალი IP დამატებულია: {new_ip}")
            self.add_ip_input.clear()
        else:
            QMessageBox.warning(self, "შეცდომა", "IP ველი ცარიელია.")

    def list_all_ips(self):
        records = self.db.get_all()
        text = ""
        for row in records:
            text += f"ID: {row[0]} | Prefix: {row[1]}\n"
        QMessageBox.information(self, "ყველა ჩანაწერი", text or "ცარიელია ბაზა.")

    def update_ip(self):
        try:
            record_id = int(self.update_input_id.text().strip())
            new_prefix = self.update_input_prefix.text().strip()
            if new_prefix:
                self.db.update(record_id, new_prefix)
                QMessageBox.information(self, "წარმატება", f"ჩანაწერი განახლდა: {new_prefix}")
                self.update_input_id.clear()
                self.update_input_prefix.clear()
            else:
                QMessageBox.warning(self, "შეცდომა", "ახალი IP ცარიელია.")
        except ValueError:
            QMessageBox.warning(self, "შეცდომა", "ID უნდა იყოს რიცხვი.")

    def delete_ip(self):
        try:
            record_id = int(self.delete_input_id.text().strip())
            self.db.delete(record_id)
            QMessageBox.information(self, "წარმატება", f"ჩანაწერი წაიშალა ID: {record_id}")
            self.delete_input_id.clear()
        except ValueError:
            QMessageBox.warning(self, "შეცდომა", "ID უნდა იყოს რიცხვი.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IPSubnetQuiz()
    window.show()
    sys.exit(app.exec_())