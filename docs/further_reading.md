# Further Reading

Covers advanced topics (different config options and scenarios)

## Recommended reading

[Feature Flag Concepts](https://ngdocs.harness.io/article/7n9433hkc0-cf-feature-flag-overview)

[Feature Flag SDK Concepts](https://ngdocs.harness.io/article/rvqprvbq8f-client-side-and-server-side-sdks)

## Setting up your Feature Flags

[Feature Flags Getting Started](https://ngdocs.harness.io/article/0a2u2ppp8s-getting-started-with-feature-flags)

## Other Variation Types

### String Variation 
```python
client.string_variation('identifier_of_your_string_flag', target, "default string")
```
[Example](examples/string_variation_example/string_variation.py)

### Number Variation
```python
client.number_variation('identifier_of_your_number_flag', target, -1)
```
[Example](examples/number_variation_example/number_variation.py)

### JSON Variation
```python
client.json_variation('identifier_of_your_json_flag', target, {})
```
[Example](examples/json_variation_example/json_variation.py)

## Cleanup
Call the close function on the client 

```python
client.close()
```
[Example](examples/cleanup_example/cleanup.py)

## Change default URL

When using your Feature Flag SDKs with a [Harness Relay Proxy](https://ngdocs.harness.io/article/q0kvq8nd2o-relay-proxy) you need to change the default URL.

To do this you import the url helper functions 

```python
from featureflags.config import with_base_url
from featureflags.config import with_events_url

```

Then pass them with the new URLs when creating your client.

```python
    client = CfClient(api_key,
                      with_base_url("https://config.feature-flags.uat.harness.io/api/1.0"),
                      with_events_url("https://event.feature-flags.uat.harness.io/api/1.0"))
```

[Example](examples/url_change_example/url_change.py)

