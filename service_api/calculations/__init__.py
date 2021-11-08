class BaseCalculation:
    def __init__(self, skip_adjustment: bool = False):
        self.skip_adjustment = skip_adjustment

    def get_result(self):
        raise NotImplementedError

    @staticmethod
    def apply_rounding(val: float, precision: int = 2) -> float:
        return round(val, precision)

    @staticmethod
    def _multiply(k: float, value: str) -> float:
        return sum(k * float(i.replace(",", ".") or 0) for i in value.split(";"))

    @staticmethod
    def _multiply_complex(const: float, value: str) -> float:
        """V1(K1) V2(K2) ... Vn(Kn)"""
        r = 0
        if value == "0":
            return r

        for i in value.split(";"):
            v, k = i.split("(")
            r += const * float(v.replace(",", ".")) * float(k.replace(")", "").replace(",", ".") or 0)
        return r

    @staticmethod
    def _divide(k: int, value: str) -> float:
        return sum(
            (k / float(i.replace(",", "."))) if float(i.replace(",", ".") or 0) != 0 else 0 for i in value.split(";")
        )
