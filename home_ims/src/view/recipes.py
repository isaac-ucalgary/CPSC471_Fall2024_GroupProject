import view.add_recipe as add_recipe

class RecipesView:
    def __init__(self, window, dba):
        self.window = window
        self.dba = dba

        self.window.addRecipeBtn.clicked.connect(lambda: add_recipe.show(self.window, self.dba))

    def rebuild_ui(self):
        pass

    def configure_user(self, user, privileged):
        self.window.addRecipeBtn.setEnabled(privileged)
