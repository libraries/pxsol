# Solana/Private Key, Public Key and Address/A Cryptographic Explanation of Private Key (Part 1)

It's okay, this chapter isn't a straightforward article. I'll be explaining some cryptographic aspects of Solana keys in this chapter, which requires readers to have a basic understanding of mathematics. If you feel uncomfortable, you can skip this chapter content without any issues - it won't hinder your progress with the rest of the course. As part of my Solana tutorial series, this article has taken me the most time, so if you're determined to read it, I assure you that you'll gain something from it afterwards.

Before we get into cryptography, we first need to get into abstract algebra. Algebra is the study of rules of arithmetic. An algebra, in fact, abstracts some basic rules from a specific system of operations, establishes a system of axioms, and then builds on them. A set, together with a set of rules, constitutes an algebraic structure.

## Group

In algebra, a **group** is a set equipped with a binary operation (denoted here as addition "+") that satisfies four fundamental properties:

0. Additive closure: For any two elements in the group, their sum remains within the group.
0. Additive associative: For any three elements a, b, and c in the ring, (a + b) + c = a + (b + c).
0. Additive identity element: There exists a special element in the group called the identity element such that for any element a in the group, a + e = e + a = a, where e represents the identity element.
0. Additive inverse element: Every element in the group has an additive inverse. For any element a in the group, there exists an element b such that a + b = b + a = e, where e is the identity element.

If we add a fifth requirement:

0. Additive commutativity: a + b = b + a.

Then this group is called an **Abelian group** or **commutative group**.

Q: Does the set of integers form a group? What about the set of natural numbers?

A: The set of integers is an Abelian group. The set of natural numbers is not a group, because it does not satisfy the fourth group axiom.

Group have several concepts, which will be mentioned later in this article.

0. The number of elements of a finite group is called the order of the group.
0. A group element p is of order the smallest integer k such that k * p equals the identity element.
0. A group element p is called a generator of the group if its order is equal to the order of the group, and the group is a cyclic group.

## Ring

A ring builds upon the concept of a group by introducing another binary operation (denoted here as multiplication "×") along with its own set of properties:

0. Multiplication closure: After multiplying any two elements in the ring, the result still belongs to the ring.
0. Multiplication associative: For any three elements a, b, and c in the ring, (a × b) × c = a × (b × c).
0. Multiplication distributive: The multiplication operation in the ring satisfies the left distributive law and the right distributive law for addition operations, that is, for any three elements a, b, c in the ring, a * (b + c) = a * b + a * c and (b + c) * a = b * a + c * a.

## Field

A field is an algebraic structure consisting of a set and two binary operations (addition and multiplication). A field satisfies all the conditions of a ring and has the following additional properties:

0. Multiplication identity element: There exists a special element in the domain called multiplication identity element, for any element a in the domain, the result of multiplying a with the multiplication identity element is equal to a itself, i.e., a * 1 = 1 * a = a, where 1 denotes the multiplication identity element.
0. Multiplicative inverse element: For any nonzero element a in the domain, there exists an element b such that a * b = b * a = 1, where 1 denotes the multiplicative identity element.

Q: Does the set of integers, rational numbers, real numbers and complex numbers form a field?

A: The set of integers forms a ring but not a domain. The set of rational numbers, the set of real numbers and the set of complex numbers form a domain.

## Finite Field

A finite field is a collection containing a finite number of elements that support addition, subtraction, multiplication, and division operations, adhering to specific rules. The most common examples of finite fields are prime fields, which are formed by taking the integers modulo a specified prime number.

Q: Consider a prime field formed by taking the integer set modulo 23. Calculate the following expressions:

- 12 + 20
- 8 * 9
- 1 / 8

A:

- 12 + 20 = 32 % 23 = 9
- 8 * 9 = 72 % 23 = 3
- Since 3 * 8 = 24 % 23 = 1, therefore 1 / 8 = 3

Below, we implement a prime finite field using Python code. It is quite similar to the integers we use in our daily lives, but with an important distinction: all computational results must be taken modulo.

The following code is borrowed from [pabtc](https://github.com/libraries/pabtc) project; you can install it via `pip install pabtc`.

```py
import json
import typing


class Fp:
    # Galois field. In mathematics, a finite field or Galois field is a field that contains a finite number of elements.
    # As with any field, a finite field is a set on which the operations of multiplication, addition, subtraction and
    # division are defined and satisfy certain basic rules.
    #
    # https://www.cs.miami.edu/home/burt/learning/Csc609.142/ecdsa-cert.pdf
    # Don Johnson, Alfred Menezes and Scott Vanstone, The Elliptic Curve Digital Signature Algorithm (ECDSA)
    # 3.1 The Finite Field Fp

    p = 0

    def __init__(self, x: int) -> None:
        self.x = x % self.p

    def __add__(self, data: typing.Self) -> typing.Self:
        assert self.p == data.p
        return self.__class__(self.x + data.x)

    def __eq__(self, data: typing.Self) -> bool:
        assert self.p == data.p
        return self.x == data.x

    def __mul__(self, data: typing.Self) -> typing.Self:
        assert self.p == data.p
        return self.__class__(self.x * data.x)

    def __neg__(self) -> typing.Self:
        return self.__class__(self.p - self.x)

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def __sub__(self, data: typing.Self) -> typing.Self:
        assert self.p == data.p
        return self.__class__(self.x - data.x)

    def __truediv__(self, data: typing.Self) -> typing.Self:
        return self * data ** -1

    def __pos__(self) -> typing.Self:
        return self.__class__(self.x)

    def __pow__(self, data: int) -> typing.Self:
        return self.__class__(pow(self.x, data, self.p))

    def json(self) -> str:
        return f'{self.x:064x}'

    @classmethod
    def nil(cls) -> typing.Self:
        return cls(0)

    @classmethod
    def one(cls) -> typing.Self:
        return cls(1)
```

Verification of the above examples using code:

```py
Fp.p = 23
assert Fp(12) + Fp(20) == Fp(9)
assert Fp(8) * Fp(9) == Fp(3)
assert Fp(8) ** -1 == Fp(3)
```

It may have noticed that division in finite fields is a special case. When attempting to compute a / b, we are actually seeking a * b⁻¹. According to Fermat's little theorem, for a prime p, it holds that bᵖ⁻¹ = 1. Therefore, b * bᵖ⁻²  = 1, implying that b⁻¹ = bᵖ⁻². Thus, a / b is equivalent to a * bᵖ⁻².
