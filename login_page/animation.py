    #    # 2. Install an event filter to detect hover
    #    self.pushButton.installEventFilter(self)
        
    #    # Store original geometry for resetting
    #    self.original_geometry = self.pushButton.geometry()

    #def eventFilter(self, obj, event):
    #    if obj == self.pushButton:
    #        if event.type() == QEvent.Enter:
    #            self.animate_button(obj, expand=True)
    #        elif event.type() == QEvent.Leave:
    #            self.animate_button(obj, expand=False)
    #    return super(MainWindow, self).eventFilter(obj, event)

    #def animate_button(self, button, expand=True):
    #    self.anim = QPropertyAnimation(button, b"geometry")
    #    self.anim.setDuration(150)
        
    #    curr = button.geometry()
    #    if expand:
    #        # Scale up: shift x/y by -5/-2 and increase width/height
    #        new_geo = QRect(curr.x()-5, curr.y()-2, curr.width()+10, curr.height()+4)
    #    else:
    #        # Return to original size
    #        # Note: In real layouts, you might need to handle this differently
    #        new_geo = QRect(curr.x()+5, curr.y()+2, curr.width()-10, curr.height()-4)
            
    #    self.anim.setEndValue(new_geo)
    #    self.anim.start()