class MealView:
    def __init__(self, window, dba):
        self.window = window
        self.dba = dba

    def rebuild_ui():
        pass
    
    def configure_user(self, user, privileged):
        self.window.addRecipeBtn.setEnabled(privileged)
