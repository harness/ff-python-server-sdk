import time
from featureflags.client import CfClient


def main():
    client = CfClient("43353147-8daa-4583-ad3d-26eca1c4765e")
    print(client.get_environment_id())
    time.sleep(10)


if __name__ == "__main__":
    main()
