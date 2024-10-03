def prompt_yes_or_no(question) -> bool:
    while True:
        response = input(f"{question} (1: yes / 2: no): ").strip()
        if response == '1':
            print()
            return True
        elif response == '2':
            print()
            return False

def get_int_response(question) -> int:
    val = input(question).strip()
    while True:
        if val.isdigit():
            print()
            return int(val)
        val = input("please enter an integer value: ").strip()

class SingletonClass(object):
  def __new__(cls) -> any:
    if not hasattr(cls, 'instance'):
      cls.instance: SingletonClass = super(SingletonClass, cls).__new__(cls)
    return cls.instance
