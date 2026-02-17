import fractions
import math
import random
import sympy

from pyrope.core import Exercise
from pyrope.nodes import (
    Equation, Expression, Natural, Integer, Problem, Rational, Set, Dropdown, Int, Boolean
)
from pyrope.nodes.dtype_nodes import OneOf, String
from pyrope.nodes.widgets import Slider, TextArea


class Apples(Exercise):

    def problem(self):
        return Problem(
            '''
            If there are five apples and you take away three,
            how many do you have?

            <<number>>
            ''',
            number=Natural()
        )

    def the_solution(self):
        return 3

    def feedback(self, number):
        if number == 3:
            return "Be honest: You knew the quiz, didn't you?"
        return 'You took three apples, so you have three!'

    def hints(self):
        yield "Hinweis 1"
        yield "Hinweis 2"
        yield "Hinweis 3"
        yield "Hinweis 4"
        yield 'Hinweis 5'
        yield "Hinweis 6"
        yield "Hinweis 7"
        yield 'Hinweis 8'
        yield "Hinweis 9"


class CinemaTickets(Exercise):

    def problem(self):
        return Problem(
            '''
            One grandmother, two mothers, two daughters and one granddaughter
            go to the cinema and buy one ticket each. How many tickets do they
            have to buy in total?

            <<number>>
            ''',
            number=Natural()
        )

    def the_solution(self):
        return 3

    def feedback(self, number):
        if number == 3:
            return "Be honest: You knew the problem, didn't you?"
        return (
            "The grandmother is also a mother and the mother is also "
            "a daughter."
        )


class Einstein(Exercise):

    def problem(self):
        return Problem(
            """
            Einstein's most famous formula, relating Energy $E$ and mass $m$
            via the speed of light $c$, reads $E=$<<RHS>>.
            """,
            RHS=Expression(symbols='m,c')
        )

    def the_solution(self):
        return sympy.parse_expr('m * c**2')


class Factor(Exercise):

    def problem(self):
        return Problem(
            'Give a factor of 42: <<answer>>',
            answer=Integer(minimum=1)
        )

    def scores(self, answer):
        return 42 % answer == 0

    def a_solution(self):  # prefix 'a_' indicates non-uniqueness
        return 7


class Factorisation(Exercise):

    def parameters(self):
        return dict(
            p=random.randint(2, 9),
            q=random.randint(2, 9),
        )

    def problem(self, p, q):
        return Problem(
            fr'{p * q} = <<p_>> $\times$ <<q_>>',
            p_=Integer(minimum=2),
            q_=Integer(minimum=2),
        )

    def scores(self, p, q, p_, q_):
        return p_ * q_ == p * q
    
    def hints(self):
        yield "Erster Hinweis: <<p>>"
        yield "Zweiter Hinweis: <<q>>"
        yield "Dritter Hinweis"


class FortyTwo(Exercise):

    def problem(self):
        return Problem(
            '''
            What is the answer to the Ultimate Question of Life, The Universe,
            and Everything?

            <<answer>>
            ''',
            answer=Natural()
        )

    def the_solution(self):
        return 42


class FreeLunch(Exercise):

    def problem(self):
        return Problem('Free lunch!')

    def scores(self):
        return 100


class IntegerDivision(Exercise):

    def parameters(self):
        a = random.randint(2, 10)
        b = random.randint(1, a)
        return dict(a=a, b=b)

    def problem(self):
        return Problem(
            '<<a>> divided by <<b>> is <<q_>> with remainder <<r_>>.',
            q_=Natural(),
            r_=Natural(),
        )

    def scores(self, a, b, q_, r_):
        scores = dict(q_=0, r_=0)
        if q_ == a // b:
            scores['q_'] = 2
        if r_ == a % b:
            scores['r_'] = 1
        return scores

    def the_solution(self, a, b):
        return dict(q_=a // b, r_=a % b)
    
    def hints(self):
        yield "Ein Hinweis: Wie oft passt <<b>> in <<a>>?"
        yield "Noch ein Hinweis: Wie viel bleibt dann noch übrig?"


class MultiplicationTable(Exercise):

    def parameters(self):
        return dict(
            a=random.randint(1, 10),
            b=random.randint(1, 10),
        )

    def problem(self):
        return Problem(r'<<a>> $\times$ <<b>> = <<c>>', c=Natural())

    def the_solution(self, a, b):
        return a * b


class PythagoreanTheorem(Exercise):

    def problem(self):
        return Problem(
            'The Pythagorean Theorem reads <<equation>>.',
            equation=Equation(symbols='a,b,c')
        )

    def the_solution(self):
        return sympy.parse_expr('Eq(a**2 + b**2, c**2)')


class RationalExample(Exercise):

    def problem(self):
        return Problem(
            '''
            A half is a third of it. What is it?

            <<number>>
            ''',
            number=Rational()
        )

    def the_solution(self):
        return fractions.Fraction(3, 2)


class Sextillion(Exercise):

    def problem(self):
        return Problem("A 'Sextillion' equals <<answer>>.", answer=Natural())

    def the_solution(self):
        return 1e21


class SumEqualsProduct(Exercise):

    def preamble(self):
        return r'You know that $2 + 2 = 2 \times 2$.'

    def problem(self):
        return Problem(
            '''
            Find a set of three different integers whose sum is equal to their
            product.

            <<numbers>>
            ''',
            numbers=Set(count=3)
        )

    def a_solution(self):
        return {1, 2, 3}

    def scores(self, numbers):
        return sum(numbers) == math.prod(numbers)


class SquareRoot(Exercise):

    def parameters(self):
        root = random.randint(1, 10)
        return dict(root=root, radicand=root**2)

    def problem(self, radicand):
        return Problem(
            'The square root of <<radicand>> is <<root_>>.',
            root_=Natural()
        )
class DropTest(Exercise):

    def problem(self):
        return Problem(
            '''
            This question has <<count_>> options.
            ''',
            count_=Int(minimum=2, maximum=4, widget=Dropdown(2, 3, 4)),
        )
    
    def the_solution(self):
        return 3

class CheckboxTest(Exercise):

    def problem(self):
        return Problem(
            '''
            Choose all correct statements:

            <<option1>> $1 + 1 = 2$ 

            <<option2>> $2^{0} = 2$

            <<option3>> All rational numbers are real.''',
        option1 = Boolean(),
        option2 = Boolean(),
        option3 = Boolean()
        )
    def the_solution(self):
        return dict(option1=True, option2=False, option3=True)
    
class RadioButtonTest(Exercise):
    def problem(self):
        return Problem(
            '''
            What's the best way to improve your math skills?

            <<test>>''',
        test = OneOf("Quit school.","Beg for wisdom.","Lots of studying.")
        )
    def the_solution(self):
        return "Lots of studying."

class RadioTest3(Exercise):
    def problem(self):
        return Problem(
            '''
            ONE of these numbers is correct. Which is it?

            <<test>>''',
        test = OneOf(1,2,3,4,5,6,7,8,9)
        )
    def the_solution(self):
        return 1

class RadioTest4(Exercise):
    def problem(self):
        return Problem(
            '''
            Choose the number that is NOT a prime.

            <<test>>''',
        test = OneOf(1,2,3,5,7)
        )
    def the_solution(self):
        return 1

class SliderTest(Exercise):

    def problem(self):
        return Problem(
            '''
            Which natural one digit number is the only one that starts and ends with an unique letter?

            <<test>>
            ''',
            test=Int(minimum=0, maximum=9, widget=Slider(0, 9)),
        )
    
    def the_solution(self):
        return 8

class TextAreaTest(Exercise):

    def problem(self):
        return Problem(
            '''
            Write about your experience with this test.

            <<answer>>
            ''',
            answer=String(widget=TextArea(8, 100))
        )

    def scores(self, answer):
        if "good" in answer:
            return 2
        elif answer.__len__() >= 100:
            return 1
        else: return 0

    def a_solution(self):
        return "This test is good."
    
import math
import random
import sympy

from pyrope.core import Exercise
from pyrope.nodes import Problem, Natural, Int, Expression, Dropdown

plaudits = (
    'Fine',
    'Nice',
    'Excellent',
    'Impressive',
    'Amazing',
    'Fantastic',
    'Outstanding',
    'Exceptional',
    'Brilliant',
    'Magnificent',
    'Superb',
    'Terrific',
    'Phenomenal',
    'Remarkable',
    'Spectacular',
    'Stunning',
    'Sublime',
    'Bravo',
)


def pigeonhole(p, levels, sublevels=1):
    try:
        nlevels = len(levels)
    except TypeError:
        nlevels = levels
        levels = range(nlevels)
    try:
        nsublevels = len(sublevels)
    except TypeError:
        nsublevels = sublevels
        sublevels = range(nsublevels)
    level, sublevel = divmod(
        math.floor((nlevels * nsublevels - 0.01) * p),
        nsublevels
    )
    if nsublevels == 1:
        return levels[level]
    return levels[level], sublevels[sublevel]


# The following is a minimalistic template without metadata or comments,
# including only the essential parts of an exercise. For writing custom
# quality exercises in PyRope, we recommend using the fully fledged template
# provided below.
#
class IntegerDivisionExtended(Exercise):

    def preamble(self):
        return r'''
            Integer division of two natural numbers, the *divisor* $m$ and
            the *dividend* $n$, results in an *integer quotient* $q$ and a
            *remainder* $r$ satisfying

            $$n=q\cdot m+r$$

            with

            $$0\leq r<m.$$
        '''

    def parameters(self):
        dividend = random.randint(10, 99)
        divisor = random.randint(2, dividend - 1)
        return dict(dividend=dividend, divisor=divisor)

    def problem(self):
        return Problem(
            '''
            <<dividend>> divided by <<divisor>> is equal to
            <<quotient>> with remainder <<remainder>>.
            ''',
            quotient=Natural(),
            remainder=Natural(),
        )

    def the_solution(self, dividend, divisor):
        return dict(
            quotient=dividend // divisor,
            remainder=dividend % divisor
        )

    def scores(self, dividend, divisor, quotient, remainder):
        scores = {'quotient': 0, 'remainder': 0}
        if quotient == dividend // divisor:
            scores['quotient'] = 2
        if remainder == dividend % divisor:
            scores['remainder'] = 1
        return scores

    def hints(self):
        yield '''
            Imagine you give a pizza party. You have ordered <<dividend>>
            pizzas for <<divisor>> people and want to share them in equal
            parts. How many entire pizzas can everyone eat?
        '''
        yield "That's the first answer, the *quotient*."
        yield 'How many pizzas will be left?'
        yield "That's the second answer, the *remainder*."

    def feedback(self, dividend, divisor, quotient, remainder):
        if None not in {quotient, remainder}:
            if quotient * divisor + remainder != dividend:
                return fr'''
                    ${quotient} \times {divisor} + {remainder}$
                    equals {quotient * divisor + remainder}, not
                    {dividend}.
                '''
        if remainder is not None and remainder >= divisor:
            return f'''
                Your remainder {remainder} is not smaller than the divisor
                {divisor}.
            '''

