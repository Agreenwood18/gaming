def prompt_yes_or_no(question) -> bool:
    while True:
        response = input(f"{question} (1: yes / 2: no): ").strip()
        if response == '1':
            return True
        elif response == '2':
            return False
