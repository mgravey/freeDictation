import platform

def main():
    system = platform.system()
    if system == "Darwin":
        from platform_mac import FreeDictationApp
    elif system == "Windows":
        from platform_windows import FreeDictationApp
    elif system == "Linux":
        from platform_linux import FreeDictationApp
    else:
        raise NotImplementedError(f"Unsupported platform: {system}")

    app = FreeDictationApp()
    app.run()

if __name__ == "__main__":
    main()