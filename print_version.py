import sys

if sys.version_info[0] < 3:
    from past.builtins.misc import raw_input

    # noinspection PyShadowingBuiltins
    input = raw_input

# Not using f-strings because someone can run this with Python <3.5 or even Python 2.7.

print("This script ({}) was run with Python version:".format(sys.argv[0]))
print("\t" + sys.version + "\n")

print("Using executable:")
print("\t" + sys.executable + "\n")

args = sys.argv[1:]
if args:
    print("With provided {} command line arguments:".format(len(args)))
    for arg in args:
        print("\t" + arg)
else:
    print("No command line arguments were provided.")

# noinspection PyUnboundLocalVariable
input("\nPrint Enter to exit...")
