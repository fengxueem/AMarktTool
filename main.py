from views import View
from controllers import Controller

def main():
    view = View()
    controller = Controller(view=view)
    controller.start_app()

if __name__ == "__main__":
    main()