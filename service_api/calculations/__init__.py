class BaseCalculation:
    def get_result(self):
        raise NotImplementedError

    @staticmethod
    def apply_rounding(val: float, precision: int = 2) -> float:
        return round(val, precision)

    @staticmethod
    def _multiply(k: int, value: str) -> float:
        return sum(k * float(i) for i in value.split())

    @staticmethod
    def _multiply_complex(k: int, value: str) -> float:
        """V1(K1) V2(K2) ... Vn(Kn)"""
        r = 0
        if value == "0":
            return r

        for i in value.split(";"):
            for j in i.split("("):
                r += k * float(j.replace(')', '').replace(",", "."))
        return r

    @staticmethod
    def _divide(k: int, value: str) -> float:
        return sum((k / float(i)) if i != "0" else 0 for i in value.split())
