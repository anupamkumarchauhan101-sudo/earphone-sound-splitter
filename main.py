import argparse
from splitter.devices import list_devices
from splitter.engine import SplitterEngine


def main():
    p = argparse.ArgumentParser(description="Play one app in your left ear and another in your right.")
    p.add_argument("--list", action="store_true", help="list audio devices and exit")
    p.add_argument("--left", help="name (or part of it) of the LEFT source device")
    p.add_argument("--right", help="name (or part of it) of the RIGHT source device")
    p.add_argument("--out", help="name (or part of it) of your earphones")
    p.add_argument("--left-gain", type=float, default=1.0)
    p.add_argument("--right-gain", type=float, default=1.0)
    p.add_argument("--block", type=int, default=1024, help="buffer size: higher = safer, lower = less delay")
    args = p.parse_args()

    if args.list:
        for i, name, n_in, n_out in list_devices():
            print(f"{i:>3} | in:{n_in} out:{n_out} | {name}")
        return

    if not (args.left and args.right and args.out):
        p.error("--left, --right and --out are required (or use --list)")

    with SplitterEngine(args.left, args.right, args.out, block=args.block,
                        left_gain=args.left_gain, right_gain=args.right_gain):
        input("Splitting audio. Press Enter to stop.\n")


if __name__ == "__main__":
    main()