import argparse

def main(
        
    )
    

    # ========================================================================
    # SHUT DOWN PRODUCTION CONTAINER

    # ========================================================================
    # RUN LET'S ENCRYPT CONTAINER

    # ========================================================================
    # RESTART PRODUCTION CONTAINER

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('container', type=str, help='Target container name.')
    parser.add_argument('domain', type=str, help='Domain name for cert.')

    args = args.parse_args()

    main(
        args.container,
        args.domain,
    )
