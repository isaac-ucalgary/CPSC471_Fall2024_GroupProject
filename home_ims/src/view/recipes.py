import view.add_recipe as add_recipe

class RecipesView:
    def __init__(self, window, dba):
        self.window = window
        self.dba = dba

        self.window.addRecipeBtn.clicked.connect(self.gen_add_recipe_slot())

    def rebuild_ui(self):
        pass

    def configure_user(self, user, privileged):
        self.window.addRecipeBtn.setEnabled(privileged)

    def gen_add_recipe_slot(self):
        def open():
            add_recipe.show(self.window, self.dba)
        return open
