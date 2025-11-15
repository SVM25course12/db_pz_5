import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,QLineEdit, QPushButton, QLabel, QTextEdit,
                             QTableWidget,QTableWidgetItem, QMessageBox)

from PyQt6.QtCore import Qt

from main import get_product_by_barcode, search_products, extract_kcal


class CalorieSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Поиск калорийности продуктов")
        self.setMinimumWidth(600)
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Введите название продукта или штрихкод")
        self.search_btn = QPushButton("Поиск")
        self.search_btn.clicked.connect(self.on_search_clicked)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.query_input)
        top_layout.addWidget(self.search_btn)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(["Штрихкод", "Название", "Бренд", "Ккал (100г)", "БЖУ (100г)"])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(QLabel("Результаты поиска:"))
        layout.addWidget(self.result_table)
        layout.addWidget(QLabel("Подробности:"))
        layout.addWidget(self.details_text)
        self.setLayout(layout)

    def on_search_clicked(self):
        query = self.query_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите название или штрихкод продукта.")
            return

        self.result_table.setRowCount(0)
        self.details_text.clear()

        try:
            if query.isdigit():
                data = get_product_by_barcode(query)
                product = data.get("product")
                if product:
                    self.show_products([product])
                else:
                    QMessageBox.information(self, "Результат", "Продукт не найден.")
            else:
                data = search_products(query, page_size=10)
                products = data.get("products", [])
                if products:
                    self.show_products(products)
                else:
                    QMessageBox.information(self, "Результат", "Ничего не найдено.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка запроса", str(e))

    def show_products(self, products):
        self.result_table.setRowCount(len(products))

        for i, p in enumerate(products):
            kcal_data = extract_kcal(p.get("nutriments", {}))
            kcal_100g = kcal_data.get("kcal_100g", "-")
            bju = f"Б:{kcal_data.get('protein_100g', '-')} Ж:{kcal_data.get('fat_100g', '-')} У:{kcal_data.get('carbs_100g', '-')}"

            self.result_table.setItem(i, 0, QTableWidgetItem(str(p.get("code", ""))))
            self.result_table.setItem(i, 1, QTableWidgetItem(p.get("product_name", "")))
            self.result_table.setItem(i, 2, QTableWidgetItem(p.get("brands", "")))
            self.result_table.setItem(i, 3, QTableWidgetItem(str(kcal_100g)))
            self.result_table.setItem(i, 4, QTableWidgetItem(bju))

        self.result_table.resizeColumnsToContents()
        self.result_table.cellClicked.connect(lambda row, col: self.show_details(products[row]))

    def show_details(self, product):
        kcal_data = extract_kcal(product.get("nutriments", {}))
        text = (
            f"<b>Название:</b> {product.get('product_name', '')}\n"
            f"<b>Бренд:</b> {product.get('brands', '')}\n"
            f"<b>Штрихкод:</b> {product.get('code', '')}\n"
            f"<b>Порция:</b> {product.get('serving_size', '')}\n\n"
            f"<b>Калорийность (на 100г):</b> {kcal_data.get('kcal_100g', '–')}\n"
            f"<b>Белки:</b> {kcal_data.get('protein_100g', '–')}\n"
            f"<b>Жиры:</b> {kcal_data.get('fat_100g', '–')}\n"
            f"<b>Углеводы:</b> {kcal_data.get('carbs_100g', '–')}\n"
        )
        self.details_text.setHtml(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalorieSearchApp()
    window.show()
    sys.exit(app.exec())
