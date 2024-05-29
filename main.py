from views import View
from models import Model
from controllers import Controller

def main():
    model = Model()
    view = View()
    controller = Controller(view=view, model=model)
    controller.start_app()

if __name__ == "__main__":
    main()