import sys
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (
	QApplication,
	QDialog,
	QFrame,
	QGraphicsDropShadowEffect,
	QLabel,
	QHBoxLayout,
	QLayout,
	QPushButton,
	QSizePolicy,
	QVBoxLayout,
	QWidget,
)


class CheckIcon(QWidget):
	def __init__(self, svg_path, parent=None):
		super().__init__(parent)
		self.setFixedSize(96, 96)

		layout = QHBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setAlignment(Qt.AlignCenter)

		if os.path.exists(svg_path):
			svg_widget = QSvgWidget(svg_path)
			svg_widget.setFixedSize(60, 60)
			layout.addWidget(svg_widget)
		else:
			fallback_label = QLabel("✓")
			fallback_label.setAlignment(Qt.AlignCenter)
			fallback_label.setFixedSize(60, 60)
			fallback_label.setStyleSheet(
				"background-color: rgba(6, 214, 160, 0.1);"
				"border-radius: 48px;"
				"color: #06D6A0;"
				"font-size: 50px;"
				"font-weight: 700;"
			)
			layout.addWidget(fallback_label)


class MessageBox(QDialog):
	VARIANTS = {
		"success": {
			"window_title": "Message de succès",
			"title": "Succès",
			"message": "Votre opération a été effectuée avec succès.",
			"icon": "../assets/global/success_messagebox.svg",
			"buttons": [
				{"text": "Continuer", "bg": "#06d6a0", "hover": "#05b88a", "pressed": "#049f77", "fg": "white", "result": "accept"}
			],
		},
		"error": {
			"window_title": "Message d'erreur",
			"title": "Erreur",
			"message": "Une erreur est survenue lors de votre opération.",
			"icon": "../assets/global/error_messagebox.svg",
			"buttons": [
				{"text": "Fermer", "bg": "#EF233C", "hover": "#d90429", "pressed": "#b50021", "fg": "white", "result": "accept"}
			],
		},
		"info": {
			"window_title": "Message d'information",
			"title": "Information",
			"message": "Votre information est prête.",
			"icon": "../assets/global/info_messagebox.svg",
			"buttons": [
				{"text": "Ok", "bg": "#3A86FF", "hover": "#2563EB", "pressed": "#1D4ED8", "fg": "white", "result": "accept"}
			],
		},
		"attention": {
			"window_title": "Message d'attention",
			"title": "Attention",
			"message": "Veuillez confirmer votre action.",
			"icon": "../assets/global/attention_messagebox.svg",
			"buttons": [
				{"text": "Accept", "bg": "#FFD166", "hover": "#ffc640", "pressed": "#f2b62d", "fg": "#231E10", "result": "accept"}
			],
		},
		"question": {
			"window_title": "Message de question",
			"title": "Question",
			"message": "Souhaitez-vous continuer ?",
			"icon": "../assets/global/question_messagebox.svg",
			"buttons": [
				{"text": "Oui", "bg": "#6366F1", "hover": "#4F46E5", "pressed": "#4338CA", "fg": "white", "result": "accept"},
				{"text": "No", "bg": "#F1F5F9", "hover": "#E2E8F0", "pressed": "#CBD5E1", "fg": "#0f172a", "result": "reject"},
			],
		},
	}

	def __init__(self, variant="success", title=None, message=None, parent=None):
		super().__init__(parent)
		if variant not in self.VARIANTS:
			raise ValueError(f"Unknown message box variant: {variant}")

		self.variant = variant
		self.variant_config = self.VARIANTS[variant]
		self.title = title or self.variant_config["title"]
		self.message = message or self.variant_config["message"]
		self._setup_ui()

	def _button_css(self, object_name, bg, hover, pressed, fg):
		return f"""
		QPushButton#{object_name} {{
			background-color: {bg};
			color: {fg};
			border: none;
			border-radius: 15px;
			font-family: Roboto;
			font-size: 17px;
			font-weight: 700;
			min-height: 35px;
			min-width: 100px;
			padding: 0 0px;
		}}
		QPushButton#{object_name}:hover {{
			background-color: {hover};
		}}
		QPushButton#{object_name}:pressed {{
			background-color: {pressed};
		}}
		"""

	def _setup_ui(self):
		self.setWindowTitle(self.variant_config["window_title"])
		self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.resize(450, 430)
		self.setMinimumSize(430, 400)

		button_style_rules = []
		for index, button in enumerate(self.variant_config["buttons"]):
			button_style_rules.append(
				self._button_css(
					f"actionButton{index}",
					button["bg"],
					button["hover"],
					button["pressed"],
					button["fg"],
				)
			)

		self.setStyleSheet(
			"""
			QDialog {
				background-color: transparent;
			}
			QFrame#card {
				background-color: #fefefe;
				border: 1px solid #f1f5f9;
				border-radius: 20px;
				min-width: 350px;
				min-height: 200px;
			}
			QLabel#title {
				color: #0f172a;
				font-family: Roboto;
				font-size: 25px;
				font-weight: 700;
			}
			QLabel#message {
				color: #475569;
				font-family: Roboto;
				font-size: 16px;
				font-weight: 400;
			}
			"""
			+ "\n".join(button_style_rules)
		)

		root_layout = QVBoxLayout(self)
		root_layout.setContentsMargins(20, 20, 20, 20)
		root_layout.setSpacing(0)
		root_layout.setSizeConstraint(QLayout.SetFixedSize)

		card = QFrame()
		card.setObjectName("card")
		card.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		shadow = QGraphicsDropShadowEffect(self)
		shadow.setBlurRadius(25)
		shadow.setOffset(0, 10)
		shadow.setColor(QColor(15, 23, 35, 35))
		card.setGraphicsEffect(shadow)

		card_layout = QVBoxLayout(card)
		card_layout.setContentsMargins(20, 0, 20, 20)
		card_layout.setSpacing(0)

		content_container = QWidget()
		content_layout = QVBoxLayout(content_container)
		content_layout.setContentsMargins(0, 0, 0, 0)
		content_layout.setSpacing(0)
		content_layout.setAlignment(Qt.AlignHCenter)

		svg_path = os.path.join(os.path.dirname(__file__), self.variant_config["icon"])
		icon = CheckIcon(svg_path)
		content_layout.addWidget(icon, alignment=Qt.AlignHCenter)
		content_layout.addSpacing(0)

		title_label = QLabel(self.title)
		title_label.setObjectName("title")
		title_label.setAlignment(Qt.AlignCenter)
		content_layout.addWidget(title_label)
		content_layout.addSpacing(10)

		message_label = QLabel(self.message)
		message_label.setObjectName("message")
		message_label.setWordWrap(True)
		message_label.setAlignment(Qt.AlignCenter)
		message_label.setContentsMargins(16, 0, 16, 0)
		content_layout.addWidget(message_label)
		content_layout.addSpacing(25)

		buttons = self.variant_config["buttons"]
		if len(buttons) == 1:
			button = QPushButton(buttons[0]["text"])
			button.setObjectName("actionButton0")
			button.setCursor(Qt.PointingHandCursor)
			button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
			if buttons[0]["result"] == "accept":
				button.clicked.connect(self.accept)
			else:
				button.clicked.connect(self.reject)
			content_layout.addWidget(button)
		else:
			buttons_layout = QHBoxLayout()
			buttons_layout.setContentsMargins(0, 0, 0, 0)
			buttons_layout.setSpacing(10)
			for index, button_cfg in enumerate(buttons):
				button = QPushButton(button_cfg["text"])
				button.setObjectName(f"actionButton{index}")
				button.setCursor(Qt.PointingHandCursor)
				button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
				if button_cfg["result"] == "accept":
					button.clicked.connect(self.accept)
				else:
					button.clicked.connect(self.reject)
				buttons_layout.addWidget(button)
			content_layout.addLayout(buttons_layout)

		card_layout.addWidget(content_container)
		root_layout.addWidget(card, alignment=Qt.AlignCenter)
		self.adjustSize()


class LogoutDialog(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.setWindowTitle("Message de déconnexion")
		self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.setModal(True)
		self.resize(450, 430)
		self.setMinimumSize(430, 400)

		self.setStyleSheet("""
			QDialog {
				background-color: transparent;
			}
			QFrame#card {
				background-color: #fefefe;
				border: 1px solid #f1f5f9;
				border-radius: 20px;
				min-width: 450px;
				min-height: 200px;
			}
			QLabel#title {
				color: #0f172a;
				font-family: Roboto;
				font-size: 25px;
				font-weight: 700;
			}
			QLabel#message {
				color: #475569;
				font-family: Roboto;
				font-size: 16px;
				font-weight: 400;
			}
			QPushButton#deconnexionButton {
				background-color: #3A86FF;
				color: white;
				border: none;
				border-radius: 15px;
				font-family: Roboto;
				font-size: 17px;
				font-weight: 700;
				min-height: 35px;
				min-width: 100px;
				padding: 0 0px;
			}
			QPushButton#deconnexionButton:hover {
				background-color: #2563EB;
			}
			QPushButton#deconnexionButton:pressed {
				background-color: #1D4ED8;
			}
			QPushButton#exitButton {
				background-color: #EF233C;
				color: white;
				border: none;
				border-radius: 15px;
				font-family: Roboto;
				font-size: 17px;
				font-weight: 700;
				min-height: 35px;
				min-width: 100px;
				padding: 0 0px;
			}
			QPushButton#exitButton:hover {
				background-color: #d90429;
			}
			QPushButton#exitButton:pressed {
				background-color: #b50021;
			}
			QPushButton#annulerButton {
				background-color: #F1F5F9;
				color: #0f172a;
				border: none;
				border-radius: 15px;
				font-family: Roboto;
				font-size: 17px;
				font-weight: 700;
				min-height: 35px;
				min-width: 100px;
				padding: 0 0px;
			}
			QPushButton#annulerButton:hover {
				background-color: #E2E8F0;
			}
			QPushButton#annulerButton:pressed {
				background-color: #CBD5E1;
			}
		""")

		root_layout = QVBoxLayout(self)
		root_layout.setContentsMargins(20, 20, 20, 20)
		root_layout.setSpacing(0)
		root_layout.setSizeConstraint(QLayout.SetFixedSize)

		self.frame = QFrame()
		self.frame.setObjectName("card")
		self.frame.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		shadow = QGraphicsDropShadowEffect(self)
		shadow.setBlurRadius(25)
		shadow.setOffset(0, 10)
		shadow.setColor(QColor(15, 23, 35, 35))
		self.frame.setGraphicsEffect(shadow)

		content_layout = QVBoxLayout(self.frame)
		content_layout.setContentsMargins(20, 0, 20, 20)
		content_layout.setSpacing(0)
		content_layout.setAlignment(Qt.AlignHCenter)

		svg_path = os.path.join(os.path.dirname(__file__), "../assets/global/info_messagebox.svg")
		icon = CheckIcon(svg_path)
		content_layout.addWidget(icon, alignment=Qt.AlignHCenter)
		content_layout.addSpacing(0)

		self.title_label = QLabel("Déconnexion")
		self.title_label.setObjectName("title")
		self.title_label.setAlignment(Qt.AlignCenter)
		content_layout.addWidget(self.title_label)
		content_layout.addSpacing(10)

		message_label = QLabel("Voulez-vous vraiment quitter ?")
		message_label.setObjectName("message")
		message_label.setWordWrap(True)
		message_label.setAlignment(Qt.AlignCenter)
		message_label.setContentsMargins(16, 0, 16, 0)
		content_layout.addWidget(message_label)
		content_layout.addSpacing(25)

		buttons_layout = QHBoxLayout()
		buttons_layout.setContentsMargins(0, 0, 0, 0)
		buttons_layout.setSpacing(10)

		self.deconnexion_button = QPushButton("Déconnexion")
		self.deconnexion_button.setObjectName("deconnexionButton")
		self.deconnexion_button.setCursor(Qt.PointingHandCursor)
		self.deconnexion_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

		self.exit_button = QPushButton("Exit")
		self.exit_button.setObjectName("exitButton")
		self.exit_button.setCursor(Qt.PointingHandCursor)
		self.exit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

		self.annuler_button = QPushButton("Annuler")
		self.annuler_button.setObjectName("annulerButton")
		self.annuler_button.setCursor(Qt.PointingHandCursor)
		self.annuler_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

		buttons_layout.addWidget(self.deconnexion_button)
		buttons_layout.addWidget(self.exit_button)
		buttons_layout.addWidget(self.annuler_button)
		content_layout.addLayout(buttons_layout)

		root_layout.addWidget(self.frame, alignment=Qt.AlignCenter)
		self.adjustSize()

		self.deconnexion_button.clicked.connect(self.handle_deconnexion)
		self.exit_button.clicked.connect(self.handle_exit)
		self.annuler_button.clicked.connect(self.reject)

	def handle_deconnexion(self):
		self.done(1)

	def handle_exit(self):
		QApplication.quit()



def main():
	app = QApplication(sys.argv)
	window = MessageBox("success")
	window.exec_()
	window = MessageBox("error")
	window.exec_()
	window = MessageBox("info")
	window.exec_()
	window = MessageBox("attention")
	window.exec_()
	window = MessageBox("question")
	window.exec_()
	window = LogoutDialog()
	window.exec_()
	sys.exit(0)


if __name__ == "__main__":
	main()