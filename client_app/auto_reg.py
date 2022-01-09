import winreg


def save_account(name: str, password: str) -> bool:
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Pymogus")
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Pymogus", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "login", 0, winreg.REG_SZ, name)
        winreg.SetValueEx(key, "password", 0, winreg.REG_SZ, password)
        winreg.CloseKey(key)
        return True
    except OSError:
        return False


def load_account() -> tuple[bool, str, str]:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Pymogus", 0, winreg.KEY_READ)
        login = winreg.QueryValueEx(key, "login")[0]
        password = winreg.QueryValueEx(key, "password")[0]
        winreg.CloseKey(key)
        return True, login, password
    except OSError:
        return False, "", ""
