class EvmLogic:
    # Logic for Signalling:
    # 0 - Off
    # 1 - On / Green
    # 2 - Flashing / Yellow
    def __init__(self):
        super().__init__()

    def get_signal_aspect(self, train_speed):
        match train_speed:

            case None:
                return [0, 0, 0, 0, 0, 0]
            case 0:
                return [0, 0, 1, 0, 0, 0]
            case 40:
                return [0, 2, 0, 1, 0, 0]
            case 60:
                return [0, 2, 0, 1, 0, 1]
            case 100:
                return [2, 0, 0, 1, 0, 2]
            case _ if train_speed > 100:
                return [1, 0, 0, 0, 0, 0]
            case _:
                return [0, 0, 0, 0, 0, 0]

    def get_signal_repeater_aspect(self, train_speed):
        match train_speed:
            case None:
                return [0, 0, 0, 0, 0, 1, 0]
            case 0:
                return [0, 0, 0, 1, 0, 0, 0]
            case 40:
                return [0, 0, 1, 0, 0, 0, 0]
            case 60:
                return [0, 0, 2, 0, 0, 0, 0]
            case 80:
                return [0, 1, 0, 0, 0, 0, 0]
            case 100:
                return [0, 2, 0, 0, 0, 0, 0]
            case 120:
                return [0, 1, 1, 0, 0, 0, 0]
            case 130:
                return [2, 0, 0, 0, 0, 0, 0]
            case _ if train_speed > 130:
                return [1, 0, 0, 0, 0, 0, 0]
            case _:
                return [0, 0, 0, 0, 1, 0, 0]

    def get_dvj_text(self, train_speed):
        match train_speed:
            case None:
                return "ERR"
            case 40 | 60:
                return "MAX"
            case 80 | 100:
                return " o "
            case 120:
                return "120"
            case _ if train_speed > 100:
                return str(train_speed)
            case _:
                return "---"
