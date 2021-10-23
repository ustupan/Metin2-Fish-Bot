from game import Process

p = Process.get_by_name("metin2client.exe", 'Mt2 Classic')
captcha = p.screenshot_captcha(80, 34)
captcha.show()

