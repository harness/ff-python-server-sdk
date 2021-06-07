# from featureflags.client import CfClient
# from featureflags.config import Config, with_base_url, with_stream_enabled


# def test_client_baseurl_conf():
#     client = CfClient("some key",
#                       with_base_url("localhost"),
#                       with_stream_enabled(True))
#     got = client.config.base_url
#     expect = "localhost"

#     assert got == expect

#     got = client.config.enable_stream
#     expect = True

#     assert got == expect


# def test_client_custom_config():
#     config = Config(enable_stream=True)
#     client = CfClient("some key", *(), config=config)

#     got = client.config.enable_stream
#     expect = True

#     assert got == expect
