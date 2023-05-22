import json

class config:
    def __init__(self, config_file) -> None:
        self.config = config_file

    def get_info(self):
        try:
            self.config = json.load(open(self.config, "r", encoding="utf-8"))
            self.visible_folders = self.config["visible_folders"]
        except Exception as e:
            return e
        try:
            self.slaver_info = json.load(open(self.config["slaver_file"], "r", encoding="utf-8"))
            with open(self.config["psw_file"], "r", encoding="utf-8") as f:
                self.psw = f.readline()
            self.socket_info = self.config["socket_info"]
        except Exception as e:
            return e
    
    def update_slaver_info(self):
        try:
            new_slaver_info = json.load(open(self.config["slaver_file"], "r", encoding="utf-8"))
            for n in new_slaver_info:
                flag = False
                for s in self.slaver_info:
                    if n["name"] == s["name"]:
                        flag = True
                        break
                if not flag:
                    self.slaver_info.append(n)
        except Exception as e:
            print(e)
