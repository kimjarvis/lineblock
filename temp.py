import sys

def my_function():
    a = 4; b = "x"; c = True; d = [1, 2, "f"]; e = {"a": 1, "b": "G"}
    return 5


def main():
    result = my_function()
    print(result)

if __name__ == "__main__":
    sys.exit(main())