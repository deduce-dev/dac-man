import time

ts = time.time()

import os
import sys

OUTPUT_CSV_DIR = "/global/homes/e/elbashan/workspace/dac-man/sandbox/batch_timestamps_dir/"

if __name__ == "__main__":

    if (len(sys.argv) < 2):
            print("Usage: python save_ts.py <filename>")
    else:
        filename = sys.argv[1]

        with open(os.path.join(OUTPUT_CSV_DIR, "dacman_batch_ts", 
            filename), 'w') as f:
            print(str(ts), file=f)