import json
import typing


class Fp:
    # Galois field. In mathematics, a finite field or Galois field is a field that contains a finite number of elements.
    # As with any field, a finite field is a set on which the operations of multiplication, addition, subtraction and
    # division are defined and satisfy certain basic rules.

    p = 0

    def __init__(self, n: int) -> None:
        self.n = n % self.p

    def __add__(self, data: typing.Self) -> typing.Self:
        assert self.p == data.p
        return self.__class__(self.n + data.n)

    def __eq__(self, data: object) -> bool:
        assert isinstance(data, self.__class__)
        assert self.p == data.p
        return self.n == data.n

    def __mul__(self, data: typing.Self) -> typing.Self:
        assert self.p == data.p
        return self.__class__(self.n * data.n)

    def __neg__(self) -> typing.Self:
        return self.__class__(self.p - self.n)

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def __sub__(self, data: typing.Self) -> typing.Self:
        assert self.p == data.p
        return self.__class__(self.n - data.n)

    def __truediv__(self, data: typing.Self) -> typing.Self:
        return self * data ** -1

    def __pos__(self) -> typing.Self:
        return self.__class__(self.n)

    def __pow__(self, data: int) -> typing.Self:
        return self.__class__(pow(self.n, data, self.p))

    def json(self) -> str:
        return f'{self.n:064x}'

    @classmethod
    def nil(cls) -> typing.Self:
        return cls(0)

    @classmethod
    def one(cls) -> typing.Self:
        return cls(1)


if __name__ == '__main__':
    Fp.p = 23
    assert Fp(12) + Fp(20) == Fp(9)
    assert Fp(8) * Fp(9) == Fp(3)
    assert Fp(8) ** -1 == Fp(3)
    Fp.p = 0

# Prime of finite field.
P = 0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffed
# The order n of G.
N = 0x1000000000000000000000000000000014def9dea2f79cd65812631a5cf5d3ed


class Fq(Fp):

    p = P


class Fr(Fp):

    p = N


A = -Fq(1)
D = -Fq(121665) / Fq(121666)


class Pt:

    def __init__(self, x: Fq, y: Fq) -> None:
        assert A * x * x + y * y == Fq(1) + D * x * x * y * y
        self.x = x
        self.y = y

    def __eq__(self, data: object) -> bool:
        assert isinstance(data, self.__class__)
        return all([
            self.x == data.x,
            self.y == data.y,
        ])

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def __add__(self, data: typing.Self) -> typing.Self:
        # https://datatracker.ietf.org/doc/html/rfc8032#ref-CURVE25519
        # Points on the curve form a group under addition, (x3, y3) = (x1, y1) + (x2, y2), with the formulas
        #           x1 * y2 + x2 * y1                y1 * y2 - a * x1 * x2
        # x3 = --------------------------,   y3 = ---------------------------
        #       1 + d * x1 * x2 * y1 * y2          1 - d * x1 * x2 * y1 * y2
        x1, x2 = self.x, data.x
        y1, y2 = self.y, data.y
        x3 = (x1 * y2 + x2 * y1) / (Fq(1) + D * x1 * x2 * y1 * y2)
        y3 = (y1 * y2 - A * x1 * x2) / (Fq(1) - D * x1 * x2 * y1 * y2)
        return self.__class__(x3, y3)

    def __mul__(self, k: Fr) -> Pt:
        # Point multiplication: Double-and-add
        # https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication
        n = k.n
        result = I
        addend = self
        while n:
            b = n & 1
            if b == 1:
                result += addend
            addend = addend + addend
            n = n >> 1
        return result

    def __neg__(self) -> Pt:
        return Pt(-self.x, self.y)

    def __sub__(self, data: Pt) -> Pt:
        return self + data.__neg__()

    def __truediv__(self, k: Fr) -> Pt:
        return self.__mul__(k ** -1)

    def __pos__(self) -> Pt:
        return self

    def json(self) -> dict[str, str]:
        return {
            'x': self.x.json(),
            'y': self.y.json(),
        }


# Identity element
I = Pt(
    Fq(0),
    Fq(1),
)
# Generator point
G = Pt(
    Fq(0x216936d3cd6e53fec0a4e231fdd6dc5c692cc7609525a7b2c9562d608f25d51a),
    Fq(0x6666666666666666666666666666666666666666666666666666666666666658),
)

if __name__ == '__main__':
    p = G * Fr(42)
    q = G * Fr(24)
    r = Pt(-p.x, p.y)
    assert p + q == G * Fr(66)
    assert p + p == G * Fr(84)
    assert p - q == G * Fr(18)
    assert r == -p
    assert p + r == I
    assert p + I == p
    assert p * Fr(42) == G * Fr(1764)
