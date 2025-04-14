easter_egg_hunt_puzzles = [
    {
        "question": "An equilateral triangle has an altitude of $5\\sqrt{3}$ cm. What is its perimeter?",
        "options": ["30 cm", "25 cm", "20 cm"],
    },
    {
        "question": "What is the output of the Python expression: `3 * (1 + 2**2) - 5`?",
        "options": ["10", "12", "8"],
    },
    {
        "question": "Given a function $f(x)$ satisfying $f(x+y)=f(x)f(y)$ for all real numbers and $f(1)=2$, what is $f(5)$?",
        "options": ["32", "10", "8"],
    },
    {
        "question": "Which ancient civilization is known for its codified law system, including the Code of Hammurabi?",
        "options": ["Babylon", "Rome", "Greece"],
    },
    {
        "question": "Which painting technique involves applying thick layers of paint to create texture on the canvas?",
        "options": ["Impasto", "Sfumato", "Fresco"],
    },
    {
        "question": "Which fundamental force is responsible for keeping the planets in orbit around the sun?",
        "options": ["Gravity", "Electromagnetism", "Strong nuclear force"],
    },
    {
        "question": "Which element is often referred to as the 'building block' for organic molecules?",
        "options": ["Carbon", "Oxygen", "Nitrogen"],
    },
    {
        "question": "Which cellular structure is known as the powerhouse of the cell?",
        "options": ["Mitochondrion", "Ribosome", "Chloroplast"],
    },
    {
        "question": "In a set of 100 numbers with an average of 50, if one number is removed and the new average of the remaining 99 numbers is 49, what was the removed number?",
        "options": ["149", "150", "148"],
    },
    {
        "question": "Which sorting algorithm has an average time complexity of O(n log n)?",
        "options": ["Merge sort", "Bubble sort", "Selection sort"],
    },
    {
        "question": "Which mathematician is associated with the statement, 'There are no three positive integers a, b, and c that can satisfy the equation $a^n + b^n = c^n$ for any integer value of n greater than 2'?",
        "options": ["Fermat", "Gauss", "Euler"],
    },
    {
        "question": "In a recursive algorithm where every function call spawns two additional calls until reaching a depth of 3 (with the initial call at depth 0), how many total function calls are made?",
        "options": ["15", "14", "16"],
    },
    {
        "question": "How many distinct arrangements can be formed from the letters in the word 'LEVEL'?",
        "options": ["30", "60", "20"],
    },
]


def main():
    for i, d in enumerate(easter_egg_hunt_puzzles):
        print(f"{i+1}. {d['question']}\n\n")
        for j, ans in enumerate(d["options"]):
            print(f"    {j+1}. {ans}\n\n")


if __name__ == "__main__":
    main()
