import argparse
from register_module import generate_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-id1', '--id1_file_path', type=str, default='/config/id1')
    parser.add_argument('-id2', '--id2_file_path', type=str, default='/config/id2')
    args = parser.parse_args()
    
    generate_id(args.id1_file_path, args.id2_file_path)
