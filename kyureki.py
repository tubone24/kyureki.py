import math

class KyurekiCalculator:
    def __init__(self):
        self.PI = 3.141592653589793238462
        self.k = self.PI / 180.0

    def gregorian_to_jd(self, year, month, day):
        """グレゴリオ暦からユリウス日を計算"""
        if month < 3:
            year -= 1
            month += 12

        jd = int(365.25 * year)
        jd += int(year / 400.0)
        jd -= int(year / 100.0)
        jd += int(30.59 * (month - 2.0))
        jd += 1721088
        jd += day
        return jd

    def jd_to_gregorian(self, jd):
        """ユリウス日からグレゴリオ暦を計算"""
        x0 = int(jd + 68570.0)
        x1 = int(x0 / 36524.25)
        x2 = x0 - int(36524.25 * x1 + 0.75)
        x3 = int((x2 + 1) / 365.2425)
        x4 = x2 - int(365.25 * x3) + 31.0
        x5 = int(int(x4) / 30.59)
        x6 = int(int(x5) / 11.0)

        day = x4 - int(30.59 * x5)
        month = x5 - 12 * x6 + 2
        year = 100 * (x1 - 49) + x3 + x6

        # 2月30日の補正
        if month == 2 and day > 28:
            if year % 100 == 0 and year % 400 == 0:
                day = 29
            elif year % 4 == 0:
                day = 29
            else:
                day = 28

        return [year, month, day]

    def normalize_angle(self, angle):
        """角度の正規化（0≦θ＜360）"""
        while angle < 0.0:
            angle += 360.0
        while angle >= 360.0:
            angle -= 360.0
        return angle

    def longitude_sun(self, t):
        """太陽の黄経を計算"""
        th = 0.0
        angles = [
            (31557.0, 161.0, 0.0004),
            (29930.0, 48.0, 0.0004),
            (2281.0, 221.0, 0.0005),
            (155.0, 118.0, 0.0005),
            (33718.0, 316.0, 0.0006),
            (9038.0, 64.0, 0.0007),
            (3035.0, 110.0, 0.0007),
            (65929.0, 45.0, 0.0007),
            (22519.0, 352.0, 0.0013),
            (45038.0, 254.0, 0.0015),
            (445267.0, 208.0, 0.0018),
            (19.0, 159.0, 0.0018),
            (32964.0, 158.0, 0.0020),
            (71998.1, 265.1, 0.0200),
            (35999.05, 267.52, 1.9147)
        ]

        for rate, angle, coef in angles:
            ang = self.normalize_angle(rate * t + angle)
            th += coef * math.cos(self.k * ang)

        ang = self.normalize_angle(36000.7695 * t)
        ang = self.normalize_angle(ang + 280.4659)
        th = self.normalize_angle(th + ang)

        return th

    def longitude_moon(self, t):
        """月の黄経を計算"""
        th = 0.0
        angles = [
            (477198.868, 44.963, 6.2888),
            (413335.35, 10.74, 1.2740),
            (890534.22, 145.7, 0.6583),
            (954397.74, 179.93, 0.2136),
            (35999.05, 87.53, 0.1851),
            (966404.0, 276.5, 0.1144)
        ]

        for rate, angle, coef in angles:
            ang = self.normalize_angle(rate * t + angle)
            th += coef * math.cos(self.k * ang)

        ang = self.normalize_angle(481267.8809 * t)
        ang = self.normalize_angle(ang + 218.3162)
        th = self.normalize_angle(th + ang)

        return th

    def calc_chu(self, tm, i, chu):
        """中気の時刻を計算"""
        tm1 = int(tm)
        tm2 = tm - tm1
        tm2 -= 9.0/24.0  # JST → DT

        t = (tm2 + 0.5) / 36525.0 + (tm1 - 2451545.0) / 36525.0
        rm_sun = self.longitude_sun(t)
        rm_sun0 = 30.0 * int(rm_sun/30.0)

        delta_t1 = delta_t2 = 1.0
        while abs(delta_t1 + delta_t2) > (1.0 / 86400.0):
            t = (tm2 + 0.5) / 36525.0 + (tm1 - 2451545.0) / 36525.0
            rm_sun = self.longitude_sun(t)
            delta_rm = rm_sun - rm_sun0

            if delta_rm > 180.0:
                delta_rm -= 360.0
            elif delta_rm < -180.0:
                delta_rm += 360.0

            delta_t1 = int(delta_rm * 365.2 / 360.0)
            delta_t2 = delta_rm * 365.2 / 360.0 - delta_t1

            tm1 = tm1 - delta_t1
            tm2 = tm2 - delta_t2
            if tm2 < 0:
                tm2 += 1.0
                tm1 -= 1.0

        chu[i][0] = tm2 + 9.0/24.0 + tm1
        chu[i][1] = rm_sun0

    def before_nibun(self, tm, nibun):
        """直前の二分二至の時刻を計算"""
        tm1 = int(tm)
        tm2 = tm - tm1
        tm2 -= 9.0/24.0

        t = (tm2 + 0.5) / 36525.0 + (tm1 - 2451545.0) / 36525.0
        rm_sun = self.longitude_sun(t)
        rm_sun0 = 90 * int(rm_sun/90.0)

        delta_t1 = delta_t2 = 1.0
        while abs(delta_t1 + delta_t2) > (1.0 / 86400.0):
            t = (tm2 + 0.5) / 36525.0 + (tm1 - 2451545.0) / 36525.0
            rm_sun = self.longitude_sun(t)
            delta_rm = rm_sun - rm_sun0

            if delta_rm > 180.0:
                delta_rm -= 360.0
            elif delta_rm < -180.0:
                delta_rm += 360.0

            delta_t1 = int(delta_rm * 365.2 / 360.0)
            delta_t2 = delta_rm * 365.2 / 360.0 - delta_t1

            tm1 = tm1 - delta_t1
            tm2 = tm2 - delta_t2
            if tm2 < 0:
                tm2 += 1.0
                tm1 -= 1.0

        nibun[0][0] = tm2 + 9.0/24.0 + tm1
        nibun[0][1] = rm_sun0

    def calc_saku(self, tm):
        """朔の時刻を計算"""
        tm1 = int(tm)
        tm2 = tm - tm1
        tm2 -= 9.0/24.0

        lc = 1
        delta_t1 = delta_t2 = 1.0
        while abs(delta_t1 + delta_t2) > (1.0 / 86400.0):
            t = (tm2 + 0.5) / 36525.0 + (tm1 - 2451545.0) / 36525.0
            rm_sun = self.longitude_sun(t)
            rm_moon = self.longitude_moon(t)

            delta_rm = rm_moon - rm_sun

            if lc == 1 and delta_rm < 0.0:
                delta_rm = self.normalize_angle(delta_rm)
            elif rm_sun >= 0 and rm_sun <= 20 and rm_moon >= 300:
                delta_rm = self.normalize_angle(delta_rm)
                delta_rm = 360.0 - delta_rm
            elif abs(delta_rm) > 40.0:
                delta_rm = self.normalize_angle(delta_rm)

            delta_t1 = int(delta_rm * 29.530589 / 360.0)
            delta_t2 = delta_rm * 29.530589 / 360.0 - delta_t1

            tm1 = tm1 - delta_t1
            tm2 = tm2 - delta_t2
            if tm2 < 0.0:
                tm2 += 1.0
                tm1 -= 1.0

            if lc == 15 and abs(delta_t1 + delta_t2) > (1.0 / 86400.0):
                tm1 = int(tm - 26)
                tm2 = 0
            elif lc > 30 and abs(delta_t1 + delta_t2) > (1.0 / 86400.0):
                return tm

            lc += 1

        return tm2 + tm1 + 9.0/24.0

    def calc_kyureki(self, tm0):
        """旧暦を計算"""
        chu = [[0.0, 0.0] for _ in range(4)]
        saku = [0.0] * 5

        self.before_nibun(tm0, chu)

        for i in range(1, 4):
            self.calc_chu(chu[i-1][0] + 32.0, i, chu)

        saku[0] = self.calc_saku(chu[0][0])

        for i in range(1, 5):
            tm = saku[i-1] + 30.0
            saku[i] = self.calc_saku(tm)
            if abs(int(saku[i-1]) - int(saku[i])) <= 26.0:
                saku[i] = self.calc_saku(saku[i-1] + 35.0)

        if int(saku[1]) <= int(chu[0][0]):
            saku = saku[1:] + [self.calc_saku(saku[3] + 35.0)]
        elif int(saku[0]) > int(chu[0][0]):
            saku = [self.calc_saku(saku[0] - 27.0)] + saku[:-1]

        lap = 1 if int(saku[4]) <= int(chu[3][0]) else 0

        m = [[0, 0, 0] for _ in range(5)]
        m[0][0] = int(chu[0][1] / 30.0) + 2
        if m[0][0] > 12:
            m[0][0] -= 12
        m[0][2] = int(saku[0])
        m[0][1] = 0

        for i in range(1, 5):
            if lap == 1 and i != 1:
                if int(chu[i-1][0]) <= int(saku[i-1]) or int(chu[i-1][0]) >= int(saku[i]):
                    m[i-1][0] = m[i-2][0]
                    m[i-1][1] = 1
                    m[i-1][2] = int(saku[i-1])
                    lap = 0
            m[i][0] = m[i-1][0] + 1
            if m[i][0] > 12:
                m[i][0] -= 12
            m[i][2] = int(saku[i])
            m[i][1] = 0

        state = 0
        i = 0
        for i in range(5):
            if int(tm0) < int(m[i][2]):
                state = 1
                break
            elif int(tm0) == int(m[i][2]):
                state = 2
                break

        if state == 0 or state == 1:
            i -= 1

        kyureki = [0] * 4
        kyureki[1] = m[i][1]  # 閏月フラグ
        kyureki[2] = m[i][0]  # 月
        kyureki[3] = int(tm0) - int(m[i][2]) + 1  # 日

        a = self.jd_to_gregorian(tm0)
        kyureki[0] = a[0]  # 年
        if kyureki[2] > 9 and kyureki[2] > a[1]:
            kyureki[0] -= 1

        return kyureki

    def calc_rokuyou(self, month, day):
        """六曜を計算"""
        rokuyou = ["先勝", "友引", "先負", "仏滅", "大安", "赤口"]
        idx = (month + day - 2) % 6
        return rokuyou[idx]
