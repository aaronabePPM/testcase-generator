import sys
import traceback
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    import testcase_generator
    print("Import successful!")
    testcase_generator.main()
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
