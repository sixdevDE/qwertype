import os
import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtCore import Qt

class Calibrator(QMainWindow):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Hand Calibrator - Click on Fingertips")
        self.image_path = image_path
        self.pixmap = QPixmap(image_path)
        if self.pixmap.isNull():
            print(f"Error: Could not load {image_path}")
            sys.exit(1)
            
        self.label = QLabel()
        self.label.setPixmap(self.pixmap)
        self.setCentralWidget(self.label)
        
        self.fingers = ["pinky", "ring", "middle", "index", "thumb"]
        self.current_idx = 0
        self.results = {}
        
        print(f"\n--- Calibrating: {os.path.basename(image_path)} ---")
        print(f"Please click exactly on the TIP of the: {self.fingers[self.current_idx].upper()}")

    def mousePressEvent(self, event: QMouseEvent):
        if self.current_idx < len(self.fingers):
            # We use the label's local coordinates
            pos = self.label.mapFromGlobal(event.globalPosition().toPoint())
            
            w = self.pixmap.width()
            h = self.pixmap.height()
            
            # Clamp and normalize
            nx = max(0.0, min(1.0, pos.x() / w))
            ny = max(0.0, min(1.0, pos.y() / h))
            
            finger = self.fingers[self.current_idx]
            self.results[finger] = (round(nx, 4), round(ny, 4))
            
            print(f"SAVED {finger}: {self.results[finger]}")
            
            self.current_idx += 1
            if self.current_idx < len(self.fingers):
                print(f"Next: Click on the TIP of the: {self.fingers[self.current_idx].upper()}")
            else:
                print("\n--- CALIBRATION COMPLETE ---")
                print("Copy this block and paste it into the chat:")
                print("```python")
                print(f"norm = {self.results}")
                print("```")
                self.close()

if __name__ == "__main__":
    # Check current directory
    asset_path = "assets/hands_left.png"
    if not os.path.exists(asset_path):
        # try parent main dir
        asset_path = os.path.join(os.getcwd(), asset_path)
        
    if not os.path.exists(asset_path):
        print(f"Error: Could not find '{asset_path}'. Please run this script from the project root folder.")
        sys.exit(1)
        
    app = QApplication(sys.argv)
    win = Calibrator(asset_path)
    win.show()
    sys.exit(app.exec())
